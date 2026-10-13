"""Interactive mode for ctfscrapper"""

import getpass
from typing import Optional

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
        if result in ('y', 'yes'):
            return True
        if result in ('n', 'no'):
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
    
    login_url = prompt_with_default("Custom login URL (optional)", "")
    if not login_url:
        login_url = None
    
    download_files = prompt_yes_no("Download challenge files?", True)
    connect_nc = prompt_yes_no("Connect to netcat services?", True)
    
    max_challenges_str = prompt_with_default("Max challenges to process (0 = all)", "0")
    max_challenges = int(max_challenges_str) if max_challenges_str.isdigit() and int(max_challenges_str) > 0 else None
    
    timeout = int(prompt_with_default("HTTP timeout (seconds)", "30"))
    nc_timeout = int(prompt_with_default("Netcat timeout (seconds)", "10"))
    delay = float(prompt_with_default("Delay between requests (seconds)", "0.1"))
    
    verify_ssl = prompt_yes_no("Verify SSL certificates?", verify_ssl)
    
    # Summary
    print(f"\n{'='*60}")
    print("Configuration Summary:")
    print(f"{'='*60}")
    print(f"  URL: {url}")
    print(f"  Username: {username}")
    print(f"  Platform: {platform}")
    print(f"  Output: {output_dir}")
    print(f"  Download files: {'Yes' if download_files else 'No'}")
    print(f"  Connect netcat: {'Yes' if connect_nc else 'No'}")
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
        login_url=login_url,
        verify_ssl=verify_ssl,
        timeout=timeout,
        nc_timeout=nc_timeout,
        delay=delay,
    )
    
    success = scraper.run(
        download_files=download_files,
        connect_nc=connect_nc,
        max_challenges=max_challenges,
    )
    
    return 0 if success else 1
