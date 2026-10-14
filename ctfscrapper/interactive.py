"""Interactive mode for ctfscrapper"""

import getpass
from typing import Optional, List, Dict

from .core import CTFScraper


def prompt_with_default(prompt: str, default: str = "") -> str:
    """Prompt user with optional default value"""
    if default:
        result = input(f"{prompt} [{default}]: ").strip()
        return result if result else default
    return input(f"{prompt}: ").strip()


def prompt_yes_no(prompt: str, default: bool = True) -> bool:
    """Prompt user for yes/no"""
    default_str = "Y/n" if default else "y/N"
    while True:
        result = input(f"{prompt} ({default_str}): ").strip().lower()
        if not result:
            return default
        if result in ("y", "yes"):
            return True
        if result in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'")


def prompt_platform() -> str:
    """Prompt user to select platform"""
    print("\nSelect platform:")
    print("  1. Auto-detect (recommended)")
    print("  2. CTFd")
    print("  3. NoCTF")
    print("  4. Generic")

    while True:
        choice = input("Choice [1]: ").strip()
        if not choice or choice == "1":
            return "auto"
        elif choice == "2":
            return "ctfd"
        elif choice == "3":
            return "noctf"
        elif choice == "4":
            return "generic"
        print("Invalid choice. Please enter 1-4.")


def normalize_name(name: str) -> str:
    """Normalize name for case-insensitive, space-insensitive comparison"""
    return name.lower().replace(" ", "").replace("-", "").replace("_", "")


def parse_selection(input_str: str) -> List[str]:
    """Parse user input like 'cat1/cat2/cat3' into list"""
    if not input_str.strip():
        return []
    return [s.strip() for s in input_str.split("/") if s.strip()]


def select_categories(all_categories: List[str]) -> List[str]:
    """Prompt user to select categories"""
    print("\nAvailable categories:")
    for i, cat in enumerate(sorted(all_categories), 1):
        print(f"  {i}. {cat}")

    print("\nEnter categories to scrape (separated by '/'):")
    print("  Examples: Web, Web/Pwn, Web/Pwn/Crypto")
    print("  Leave empty or type 'all'/'everything' for all categories")

    while True:
        user_input = prompt_with_default("Categories").strip()
        if not user_input or user_input.lower() in ("all", "everything"):
            return all_categories

        selected = parse_selection(user_input)
        invalid = []
        for sel in selected:
            # Find matching category (case-insensitive)
            matches = [c for c in all_categories if normalize_name(c) == normalize_name(sel)]
            if not matches:
                invalid.append(sel)

        if invalid:
            print(f"Invalid categories: {', '.join(invalid)}")
            print("Please try again.")
            continue

        # Return actual category names (proper case)
        result = []
        for sel in selected:
            matches = [c for c in all_categories if normalize_name(c) == normalize_name(sel)]
            result.append(matches[0])
        return result


def select_challenges(category: str, all_challenges: List[Dict]) -> List[str]:
    """Prompt user to select challenges for a category"""
    cat_challenges = [c for c in all_challenges if c.get("category") == category]
    challenge_names = [c.get("name", "") for c in cat_challenges]

    print(f"\nChallenges in '{category}':")
    for i, name in enumerate(sorted(challenge_names), 1):
        print(f"  {i}. {name}")

    print(f"\nEnter challenges to scrape for '{category}' (separated by '/'):")
    print("  Examples: Baby Win, Baby Win/Flag Roulette, Baby Win/Flag Roulette/Black Flash")
    print("  Leave empty or type 'all'/'everything' for all challenges")

    while True:
        user_input = prompt_with_default(f"Challenges for {category}").strip()
        if not user_input or user_input.lower() in ("all", "everything"):
            return challenge_names

        selected = parse_selection(user_input)
        invalid = []
        for sel in selected:
            matches = [c for c in challenge_names if normalize_name(c) == normalize_name(sel)]
            if not matches:
                invalid.append(sel)

        if invalid:
            print(f"Invalid challenges: {', '.join(invalid)}")
            print("Please try again.")
            continue

        # Return actual challenge names (proper case)
        result = []
        for sel in selected:
            matches = [c for c in challenge_names if normalize_name(c) == normalize_name(sel)]
            result.append(matches[0])
        return result


def prompt_overwrite(existing_count: int) -> str:
    """Prompt user for overwrite decision"""
    if existing_count == 1:
        while True:
            choice = input("Challenge already exists. Overwrite? (y/n): ").strip().lower()
            if choice in ("y", "yes"):
                return "y"
            elif choice in ("n", "no"):
                return "n"
            print("Please enter 'y' or 'n'")
    else:
        while True:
            choice = (
                input(f"{existing_count} challenges already exist. Overwrite? (y/n/all/skip): ")
                .strip()
                .lower()
            )
            if choice in ("y", "yes"):
                return "y"
            elif choice in ("n", "no"):
                return "n"
            elif choice in ("all", "a"):
                return "all"
            elif choice in ("skip", "s"):
                return "skip"
            print("Please enter 'y', 'n', 'all', or 'skip'")


def run_selective_scrape(
    url: str,
    username: str,
    password: str,
    platform: str,
    output_dir: str,
    login_url: Optional[str],
    verify_ssl: bool,
    timeout: int,
    nc_timeout: int,
    delay: float,
    ctf_name: str,
    malware_scan: bool = True,
    quarantine_dir: Optional[str] = None,
    max_scan_time: int = 60,
) -> int:
    """Run interactive selective scraping"""
    print(f"\n{'='*60}")
    print("  ctfscrapper - Selective Scrape Mode")
    print(f"{'='*60}")
    print(f"\nTarget URL: {url}")
    print(f"CTF Name: {ctf_name}\n")

    # Create scraper to fetch categories
    scraper = CTFScraper(
        base_url=url,
        username=username,
        password=password,
        platform=platform,
        output_dir=output_dir,
        login_url=login_url,
        verify_ssl=verify_ssl,
        timeout=timeout,
        nc_timeout=nc_timeout,
        delay=0.1,  # Fast delay for category discovery
    )

    # Login and fetch challenges
    print("[*] Logging in and fetching challenge list...")
    if not scraper.login():
        return 1

    challenge_list = scraper.fetch_challenges_list()
    if not challenge_list:
        print("[-] No challenges found")
        return 1

    # Get all categories
    all_categories = sorted(set(c.get("category", "Unknown") for c in challenge_list))

    # Select categories
    selected_categories = select_categories(all_categories)
    if not selected_categories:
        print("[-] No categories selected. Exiting.")
        return 0

    # For each category, select challenges
    selected_challenges: Dict[str, List[str]] = {}
    for cat in selected_categories:
        challenges = select_challenges(cat, challenge_list)
        if challenges:
            selected_challenges[cat] = challenges

    if not selected_challenges:
        print("[-] No challenges selected. Exiting.")
        return 0

    # Summary
    print(f"\n{'='*60}")
    print("Scrape Summary:")
    print(f"{'='*60}")
    print(f"  CTF Name: {ctf_name}")
    print(f"  URL: {url}")
    print(f"  Platform: {platform}")
    print(f"  Output: {output_dir}")
    print(f"  Categories: {len(selected_challenges)}")
    total_challenges = sum(len(chals) for chals in selected_challenges.values())
    print(f"  Challenges: {total_challenges}")
    for cat, chals in selected_challenges.items():
        print(f"    {cat}: {len(chals)} challenges")
        for ch in chals:
            print(f"      - {ch}")
    print(f"{'='*60}\n")

    if not prompt_yes_no("Proceed with scrape?"):
        print("Cancelled.")
        return 0

    # Run scraper with filters
    print("\n[*] Starting selective scrape...")
    scraper = CTFScraper(
        base_url=url,
        username=username,
        password=password,
        platform=platform,
        output_dir=output_dir,
        login_url=login_url,
        verify_ssl=verify_ssl,
        timeout=timeout,
        nc_timeout=nc_timeout,
        delay=0.1,
    )

    try:
        success = scraper.run_selective(
            category_filter=list(selected_challenges.keys()),
            challenge_filter=selected_challenges,
            download_files=True,
            connect_nc=True,
            malware_scan=malware_scan,
            quarantine_dir=quarantine_dir,
            max_scan_time=max_scan_time,
        )
        return 0 if success else 1
    except Exception as e:
        error_msg = str(e)
        if "Could not find challenges API endpoint" in error_msg:
            print("[-] Error: Could not find the challenges API endpoint.")
            print(
                "    The provided URL may not be a valid CTFd instance, "
                "or the challenges API is not accessible."
            )
            print(
                "    Try providing the exact challenges page URL "
                "(e.g., https://ctf.example.com/challenges)"
            )
        return 1


def run_interactive(
    url: str,
    verify_ssl: bool = True,
) -> int:
    """Run interactive configuration"""
    print(f"\n{'='*60}")
    print("  ctfscrapper - Interactive Mode")
    print(f"{'='*60}")
    print(f"\nTarget URL: {url}\n")

    # Get credentials
    username = prompt_with_default("Username")
    if not username:
        print("[-] Username is required")
        return 4

    try:
        password = getpass.getpass("Password: ")
    except Exception:
        password = input("Password (visible): ").strip()

    if not password:
        print("[-] Password is required")
        return 4

    # Platform selection
    platform = prompt_platform()

    # Optional settings
    print("\n--- Optional Settings (press Enter for defaults) ---")

    output_dir = prompt_with_default("Output directory", "ctf-data")

    # CTF Name (required for folder organization)
    ctf_name = ""
    while not ctf_name:
        ctf_name = prompt_with_default("CTF Name (for folder organization)")
        if not ctf_name:
            print("[-] CTF Name is required for folder organization. Please enter a name.")

    # CTF Name comes after Output directory, before other options
    login_url: Optional[str] = prompt_with_default("Custom login URL (optional)", "")
    if not login_url:
        login_url = None

    download_files = prompt_yes_no("Download challenge files?", True)
    connect_nc = prompt_yes_no("Connect to netcat services?", True)

    # Use sensible defaults for advanced options, only ask if user wants to customize
    customize_advanced = prompt_yes_no("Customize advanced options (timeout, delay, etc.)?", False)

    if customize_advanced:
        max_challenges_str = prompt_with_default("Max challenges to process (0 = all)", "0")
        max_challenges = (
            int(max_challenges_str)
            if max_challenges_str.isdigit() and int(max_challenges_str) > 0
            else None
        )
        timeout = int(prompt_with_default("HTTP timeout (seconds)", "30"))
        nc_timeout = int(prompt_with_default("Netcat timeout (seconds)", "10"))
        delay = float(prompt_with_default("Delay between requests (seconds)", "0.1"))
    else:
        max_challenges = None
        timeout = 30
        nc_timeout = 10
        delay = 0.1

    verify_ssl = prompt_yes_no("Verify SSL certificates?", True)

    # Malware scanning options
    print("\n--- Malware Scanning Options ---")
    malware_scan = prompt_yes_no("Enable malware scanning?", True)

    quarantine_dir = None
    max_scan_time = 60
    if malware_scan:
        quarantine_dir = prompt_with_default(
            "Quarantine directory (relative to output)", ".quarantine"
        )
        if not quarantine_dir:
            quarantine_dir = ".quarantine"
        max_scan_time = int(prompt_with_default("Max scan time per file (seconds)", "60"))

    # Mode selection
    print("\n--- Scrape Mode ---")
    print("  1. Selective Scrape (choose categories and challenges)")
    print("  2. Full Scrape (all challenges)")

    while True:
        choice = input("Mode [1]: ").strip()
        if not choice or choice == "1":
            return run_selective_scrape(
                url=url,
                username=username,
                password=password,
                platform=platform,
                output_dir=output_dir,
                login_url=None,
                verify_ssl=verify_ssl,
                timeout=timeout,
                nc_timeout=nc_timeout,
                delay=delay,
                ctf_name=ctf_name,
                malware_scan=malware_scan,
                quarantine_dir=quarantine_dir,
                max_scan_time=max_scan_time,
            )
        elif choice == "2":
            # Use the collected settings for full scrape
            break
        print("Invalid choice. Please enter 1 or 2.")

    # Summary
    print(f"\n{'='*60}")
    print("Configuration Summary:")
    print(f"{'='*60}")
    print(f"  URL: {url}")
    print(f"  Username: {username}")
    print(f"  Platform: {platform}")
    print(f"  Output: {output_dir}")
    print(f"  CTF Name: {ctf_name}")
    print(f"  Download files: {'Yes' if download_files else 'No'}")
    print(f"  Connect netcat: {'Yes' if connect_nc else 'No'}")
    print(f"  Malware scan: {'Yes' if malware_scan else 'No'}")
    if malware_scan:
        print(f"  Quarantine dir: {quarantine_dir}")
        print(f"  Max scan time: {max_scan_time}s")
    if max_challenges:
        print(f"  Max challenges: {max_challenges}")
    print(f"  Verify SSL: {'Yes' if verify_ssl else 'No'}")
    print(f"{'='*60}\n")

    if not prompt_yes_no("Proceed with scrape?"):
        print("Cancelled.")
        return 0

    # Run scraper
    scraper = CTFScraper(
        base_url=url,
        username=username,
        password=password,
        platform=platform,
        output_dir=output_dir,
        login_url=None,
        verify_ssl=verify_ssl,
        timeout=timeout,
        nc_timeout=nc_timeout,
        delay=delay,
    )

    try:
        success = scraper.run(
            download_files=download_files,
            connect_nc=connect_nc,
            max_challenges=max_challenges,
            malware_scan=malware_scan,
            quarantine_dir=quarantine_dir,
            max_scan_time=max_scan_time,
        )
        return 0 if success else 1
    except Exception as e:
        error_msg = str(e)
        if "Could not find challenges API endpoint" in error_msg:
            print("[-] Error: Could not find the challenges API endpoint.")
            print(
                "    The provided URL may not be a valid CTFd instance, "
                "or the challenges API is not accessible."
            )
            print(
                "    Try providing the exact challenges page URL "
                "(e.g., https://ctf.example.com/challenges)"
            )
        return 1
    except Exception as e:
        error_msg = str(e)
        if "Could not find challenges API endpoint" in error_msg:
            print("[-] Error: Could not find the challenges API endpoint.")
            print(
                "    The provided URL may not be a valid CTFd instance, "
                "or the challenges API is not accessible."
            )
            print(
                "    Try providing the exact challenges page URL "
                "(e.g., https://ctf.example.com/challenges)"
            )
        return 1
