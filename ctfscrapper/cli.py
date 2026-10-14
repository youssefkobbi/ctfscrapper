"""Command-line interface for ctfscrapper"""

import argparse
import sys
import os

from .core import CTFScraper
from .interactive import run_interactive

# ASCII Art Banner
BANNER = r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    ██████╗██╗  ██╗███████╗███████╗████████╗ ██████╗ ██████╗ ███╗   ██╗      ║
║   ██╔════╝██║  ██║██╔════╝██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗████╗  ██║      ║
║   ██║     ███████║█████╗  ███████╗   ██║   ██║   ██║██████╔╝██╔██╗ ██║      ║
║   ██║     ██╔══██║██╔══╝  ╚════██║   ██║   ██║   ██║██╔══██╗██║╚██╗██║      ║
║   ╚██████╗██║  ██║███████╗███████║   ██║   ╚██████╔╝██║  ██║██║ ╚████║      ║
║    ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝      ║
║                                                                              ║
║              Universal CTF Challenge Scraper v1.0.0                         ║
║         Supports: CTFd • NoCTF • Generic Platforms                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

BANNER_SMALL = r"""
    ██████╗██╗  ██╗███████╗███████╗████████╗ ██████╗ ██████╗ ███╗   ██╗
   ██╔════╝██║  ██║██╔════╝██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗████╗  ██║
   ██║     ███████║█████╗  ███████╗   ██║   ██║   ██║██████╔╝██╔██╗ ██║
   ██║     ██╔══██║██╔══╝  ╚════██║   ██║   ██║   ██║██╔══██╗██║╚██╗██║
   ╚██████╗██║  ██║███████╗███████║   ██║   ╚██████╔╝██║  ██║██║ ╚████║
    ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝
              Universal CTF Challenge Scraper v1.0.0
"""


def print_banner(use_color: bool = True):
    """Print the ASCII art banner"""
    if use_color:
        cyan = "\033[96m"
        green = "\033[92m"
        reset = "\033[0m"
        print(f"{cyan}{BANNER}{reset}")
        print(f"{green}    🏴‍☠️  Scrape • Organize • Solve  🏴‍☠️{reset}\n")
    else:
        print(BANNER)
        print("    Scrape • Organize • Solve\n")


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        prog="ctfscrapper",
        description="Universal CTF Challenge Scraper - Supports CTFd, NoCTF, and generic platforms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{BANNER_SMALL}

Usage Modes:
  1. Interactive (recommended for beginners):
     ctfscrapper https://ctf.example.com
     # Will prompt for username, password, and options

  2. Direct arguments (for automation):
     ctfscrapper -u https://ctf.example.com -U user -P pass

  3. Environment variables:
     export CTFSCRAPPER_URL="https://ctf.example.com"
     export CTFSCRAPPER_USER="user"
     export CTFSCRAPPER_PASS="pass"
     ctfscrapper

Examples:
   # Interactive mode - just provide URL
   ctfscrapper https://ctf.example.com

   # Direct mode with all args
   ctfscrapper -u https://ctf.example.com -U user -P pass -o my_data

   # CTFd explicit
   ctfscrapper -u https://ctf.example.com -U user -P pass --platform ctfd

   # Skip features for speed
   ctfscrapper -u https://ctf.example.com -U user -P pass --no-files --no-nc

   # Quiet for CI/CD
   ctfscrapper -u https://ctf.example.com -U user -P pass -q

Environment Variables:
  CTFSCRAPPER_URL     Default CTF URL
  CTFSCRAPPER_USER    Default username
  CTFSCRAPPER_PASS    Default password

Exit Codes:
  0  Success
  1  Login failed
  2  No challenges found
  3  Network error
  4  Invalid arguments
        """,
    )

    # Positional argument for interactive mode
    parser.add_argument("url", nargs="?", help="CTF URL (interactive mode if provided without -u)")

    # Direct mode arguments
    parser.add_argument("-u", "--url", dest="url_opt", help="CTF base URL (direct mode)")
    parser.add_argument("-U", "--user", dest="user", help="Username (direct mode)")
    parser.add_argument("-P", "--pass", dest="password", help="Password (direct mode)")

    # Platform options
    platform = parser.add_argument_group("Platform Options")
    platform.add_argument(
        "--platform",
        choices=["auto", "ctfd", "noctf", "generic"],
        default="auto",
        help="CTF platform (default: auto-detect)",
    )
    platform.add_argument("--login-url", help="Custom login URL (default: <url>/login)")

    # Output options
    output = parser.add_argument_group("Output Options")
    output.add_argument(
        "-o", "--output", default="ctf-data", help="Output directory (default: ctf-data)"
    )
    output.add_argument("--no-files", action="store_true", help="Skip downloading challenge files")
    output.add_argument("--no-nc", action="store_true", help="Skip netcat connections")
    output.add_argument(
        "--max", type=int, dest="max_challenges", help="Maximum number of challenges to process"
    )

    # Network options
    network = parser.add_argument_group("Network Options")
    network.add_argument(
        "--timeout", type=int, default=30, help="HTTP timeout in seconds (default: 30)"
    )
    network.add_argument(
        "--nc-timeout", type=int, default=10, help="Netcat timeout in seconds (default: 10)"
    )
    network.add_argument(
        "--delay", type=float, default=0.1, help="Delay between requests in seconds (default: 0.1)"
    )
    network.add_argument(
        "--no-verify-ssl", action="store_true", help="Disable SSL certificate verification"
    )

    # Display options
    display = parser.add_argument_group("Display Options")
    display.add_argument(
        "-q", "--quiet", action="store_true", help="Quiet mode (no banner, minimal output)"
    )
    display.add_argument("--no-color", action="store_true", help="Disable colored output")
    display.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    display.add_argument("-i", "--interactive", action="store_true", help="Force interactive mode")
    display.add_argument("--version", action="version", version="ctfscrapper 1.0.0")

    return parser


def get_env_defaults() -> dict:
    """Get defaults from environment variables"""
    return {
        "url": os.getenv("CTFSCRAPPER_URL"),
        "user": os.getenv("CTFSCRAPPER_USER"),
        "password": os.getenv("CTFSCRAPPER_PASS"),
    }


def validate_direct_args(args) -> bool:
    """Validate direct mode arguments"""
    env = get_env_defaults()

    # Fill from env if not provided
    if not args.url_opt and env["url"]:
        args.url_opt = env["url"]
    if not args.user and env["user"]:
        args.user = env["user"]
    if not args.password and env["password"]:
        args.password = env["password"]

    missing = []
    if not args.url_opt:
        missing.append("--url / CTFSCRAPPER_URL")
    if not args.user:
        missing.append("--user / CTFSCRAPPER_USER")
    if not args.password:
        missing.append("--pass / CTFSCRAPPER_PASS")

    if missing:
        print(f"Missing required arguments for direct mode: {', '.join(missing)}")
        print("Run without arguments for interactive mode, or use --help")
        return False

    return True


def run_direct_mode(args) -> int:
    """Run in direct/automation mode"""
    if not args.quiet:
        print_banner(use_color=not args.no_color and sys.stdout.isatty())

    if not validate_direct_args(args):
        return 4

    scraper = CTFScraper(
        base_url=args.url_opt,
        username=args.user,
        password=args.password,
        platform=args.platform,
        output_dir=args.output,
        login_url=args.login_url,
        verify_ssl=not args.no_verify_ssl,
        timeout=args.timeout,
        nc_timeout=args.nc_timeout,
        delay=args.delay,
    )

    try:
        success = scraper.run(
            download_files=not args.no_files,
            connect_nc=not args.no_nc,
            max_challenges=args.max_challenges,
        )
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        return 130
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
            print("    Or use --platform to specify the platform explicitly.")
        elif "Could not find challenges API endpoint" in error_msg:
            print("[-] Error: Could not find the challenges API endpoint.")
            print(
                "    Try providing the exact challenges page URL "
                "(e.g., https://ctf.example.com/challenges)"
            )
        if args.verbose:
            import traceback

            traceback.print_exc()
        else:
            print(f"[-] Error: {e}")
        return 3


def main(args=None) -> int:
    """Main entry point"""
    parser = create_parser()

    if args is None:
        args = parser.parse_args()

    # Determine mode:
    # - If positional URL provided without -u/--url -> interactive
    # - If -u/--url provided -> direct mode
    # - If neither -> interactive (will prompt for URL)

    has_direct_url = bool(args.url_opt)
    has_positional_url = bool(args.url)
    force_interactive = args.interactive

    if force_interactive or (has_positional_url and not has_direct_url):
        # Interactive mode
        url = args.url or args.url_opt or get_env_defaults()["url"]
        if not url:
            # Prompt for URL
            print_banner(use_color=not args.no_color and sys.stdout.isatty())
            url = input("CTF URL: ").strip()
            if not url:
                print("[-] URL is required")
                return 4
        return run_interactive(url, verify_ssl=not args.no_verify_ssl)

    elif has_direct_url:
        # Direct mode
        return run_direct_mode(args)

    else:
        # No arguments at all - interactive
        print_banner(use_color=not args.no_color and sys.stdout.isatty())
        url = input("CTF URL: ").strip()
        if not url:
            print("[-] URL is required")
            return 4
        return run_interactive(url, verify_ssl=not args.no_verify_ssl)


if __name__ == "__main__":
    sys.exit(main())
