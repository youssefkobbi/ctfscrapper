"""Core scraping logic for ctfscrapper"""

import json
import re
import signal
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Known CTFd paths that should be stripped to get base URL
CTFD_KNOWN_PATHS = [
    "/scoreboard",
    "/scoreboard/",
    "/challenges",
    "/challenges/",
    "/login",
    "/login/",
    "/register",
    "/register/",
    "/admin",
    "/admin/",
    "/users",
    "/users/",
    "/teams",
    "/teams/",
    "/api/v1",
    "/api/v1/",
    "/api",
    "/api/",
]

# CTFd API endpoints to try (in order of preference)
CTFD_API_ENDPOINTS = [
    "/api/v1/challenges",
    "/api/challenges",
    "/challenges",
]

# CTFd identifiers for platform detection
CTFD_INDICATORS = [
    "ctfd",
    "ctf.inst",
    "ctfd.io",
    "ctfd_instance",
]


def normalize_base_url(url: str) -> str:
    """Extract base URL from any CTFd URL by stripping known paths."""
    url = url.rstrip("/")
    for path in CTFD_KNOWN_PATHS:
        if url.endswith(path):
            return url[: -len(path)]
    return url


def is_ctfd_url(url: str) -> bool:
    """Check if URL appears to be a CTFd instance."""
    url_lower = url.lower()
    return any(indicator in url_lower for indicator in CTFD_INDICATORS)


class CTFScraper:
    """Universal CTF Challenge Scraper supporting CTFd, NoCTF, and generic platforms."""

    PLATFORMS: Dict[str, Dict[str, object]] = {
        "ctfd": {
            "api_challenges": "/api/v1/challenges",
            "api_challenge": "/api/v1/challenges/{id}",
            "login_field": "name",
            "password_field": "password",
            "nonce_field": "nonce",
            "nonce_patterns": [
                r"'csrfNonce':\s*\"([^\"]+)\"",
                r'name="nonce"\s+value="([^"]+)"',
                r'csrf-token["\']?\s*:\s*["\']([^"\']+)["\']',
            ],
        },
        "noctf": {
            "api_challenges": "/api/challenges",
            "api_challenge": "/api/challenges/{id}",
            "login_field": "username",
            "password_field": "password",
        },
        "generic": {
            "api_challenges": "/api/challenges",
            "api_challenge": "/api/challenges/{id}",
            "login_field": "username",
            "password_field": "password",
        },
    }

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        platform: str = "auto",
        output_dir: str = "ctf-data",
        login_url: Optional[str] = None,
        verify_ssl: bool = True,
        timeout: int = 30,
        nc_timeout: int = 10,
        delay: float = 0.1,
        logger=None,
    ):
        # Normalize base URL to handle any CTFd URL (scoreboard, challenges, login, etc.)
        self.base_url = normalize_base_url(base_url)
        self.original_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.platform = platform.lower()
        self.output_dir = Path(output_dir)
        self.login_url = login_url or f"{self.base_url}/login"
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.nc_timeout = nc_timeout
        self.delay = delay
        self.logger = logger or self._default_logger

        self.session = requests.Session()
        self.session.verify = verify_ssl

        # Set a proper User-Agent to avoid 403 errors
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/html, */*",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

        # Configure retries
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.challenges: list[dict] = []
        self.config: Optional[Dict] = None
        self._shutdown = False

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _default_logger(self, level: str, msg: str):
        """Default logger using print with colors"""
        colors = {
            "info": "\033[94m",  # Blue
            "success": "\033[92m",  # Green
            "warning": "\033[93m",  # Yellow
            "error": "\033[91m",  # Red
            "debug": "\033[90m",  # Gray
            "reset": "\033[0m",
        }
        prefix = {
            "info": "[*]",
            "success": "[+]",
            "warning": "[!]",
            "error": "[-]",
            "debug": "[>]",
        }
        color = colors.get(level, "")
        reset = colors["reset"]
        print(f"{color}{prefix.get(level, '[*]')} {msg}{reset}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger("warning", "Interrupt received, saving progress...")
        self._shutdown = True

    def detect_platform(self) -> str:
        """Auto-detect CTF platform"""
        self.logger("info", f"Detecting platform for {self.base_url}...")

        try:
            resp = self.session.get(self.base_url, timeout=10)
            text_lower = resp.text.lower()
            server = resp.headers.get("Server", "").lower()

            if "ctfd" in text_lower or "ctfd" in server:
                return "ctfd"
            if "noctf" in text_lower:
                return "noctf"

            # Try API endpoints
            for platform in ["ctfd", "noctf"]:
                api_url = urljoin(self.base_url, str(self.PLATFORMS[platform]["api_challenges"]))
                resp = self.session.get(api_url, timeout=5)
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        if "data" in data or "results" in data:
                            return platform
                    except Exception:
                        pass

            return "generic"
        except Exception as e:
            self.logger("warning", f"Platform detection failed: {e}")
            return "generic"

    def get_csrf_nonce(self) -> Optional[str]:
        """Extract CSRF nonce from login page (CTFd specific)"""
        try:
            resp = self.session.get(self.login_url, timeout=10)
            config = self.PLATFORMS.get("ctfd", {})

            patterns = config.get("nonce_patterns", [])
            if isinstance(patterns, list):
                for pattern in patterns:
                    match = re.search(pattern, resp.text)
                    if match:
                        return match.group(1)
        except Exception as e:
            self.logger("debug", f"Nonce extraction error: {e}")
        return None

    def login(self) -> bool:
        """Login to CTF platform"""
        self.logger("info", f"Logging in to {self.base_url}...")

        config: Dict[str, Any] = self.PLATFORMS.get(self.platform, self.PLATFORMS["generic"])
        self.config = config

        # Get CSRF nonce for CTFd
        nonce = None
        if self.platform == "ctfd":
            nonce = self.get_csrf_nonce()
            if nonce:
                self.logger("success", "Found CSRF nonce")

        # Prepare login data
        login_data = {
            str(config["login_field"]): self.username,
            str(config["password_field"]): self.password,
        }

        if nonce and config.get("nonce_field"):
            login_data[str(config["nonce_field"])] = nonce

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": self.login_url,
        }

        try:
            resp = self.session.post(
                self.login_url,
                data=login_data,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True,
            )

            # Check if login was successful (could be 200, 302, or even 403 with redirect)
            if resp.status_code in [200, 302]:
                # Verify login by accessing challenges API - use detected endpoint
                api_endpoint = self.detect_api_endpoint()
                if not api_endpoint:
                    self.logger("error", "Could not find challenges API endpoint")
                    return False

                test_url = urljoin(self.base_url, api_endpoint)
                test_resp = self.session.get(test_url, timeout=10)
                if test_resp.status_code == 200:
                    try:
                        data = test_resp.json()
                        if data.get("success") or "data" in data or "results" in data:
                            self.logger("success", "Login successful!")
                            # Update config with detected API endpoint
                            self.config["api_challenges"] = api_endpoint
                            return True
                    except Exception:
                        pass
                elif resp.status_code == 403:
                    # Some CTFd instances return 403 but still set session cookies
                    # Try to verify login anyway
                    api_endpoint = self.detect_api_endpoint()
                    if api_endpoint:
                        test_url = urljoin(self.base_url, api_endpoint)
                        test_resp = self.session.get(test_url, timeout=10)
                        if test_resp.status_code == 200:
                            try:
                                data = test_resp.json()
                                if data.get("success") or "data" in data or "results" in data:
                                    self.logger(
                                        "success", "Login successful (403 but session valid)!"
                                    )
                                    self.config["api_challenges"] = api_endpoint
                                    return True
                            except Exception:
                                pass

            self.logger("error", f"Login failed (status: {resp.status_code})")
            if resp.status_code == 403:
                self.logger(
                    "warning",
                    "Got 403 - check if platform needs special headers or has rate limiting",
                )
            return False

        except Exception as e:
            self.logger("error", f"Login error: {e}")
            return False

    def fetch_challenges_list(self) -> List[Dict]:
        """Fetch list of all challenges"""
        assert self.config is not None, "login() must be called first"

        # Use detected API endpoint or fallback to config
        api_endpoint = self.config.get("api_challenges")
        if not api_endpoint:
            self.logger("warning", "API endpoint not in config, detecting...")
            api_endpoint = self.detect_api_endpoint()
            if not api_endpoint:
                self.logger("error", "Could not find challenges API endpoint")
                return []
            self.config["api_challenges"] = api_endpoint

        api_url = urljoin(self.base_url, api_endpoint)
        self.logger("info", f"Fetching challenges from API: {api_url}")

        try:
            resp = self.session.get(api_url, timeout=self.timeout)
            resp.raise_for_status()
            data: Dict[str, Any] = resp.json()

            challenges: List[Dict[str, Any]]
            if "data" in data:
                challenges = data["data"]
            elif "results" in data:
                challenges = data["results"]
            elif isinstance(data, list):
                challenges = data
            else:
                challenges = []

            self.logger("success", f"Found {len(challenges)} challenges")
            return challenges

        except Exception as e:
            self.logger("error", f"Failed to fetch challenges: {e}")
            return []

    def fetch_challenge_details(self, challenge_id: int) -> Optional[Dict]:
        """Fetch detailed info for a single challenge"""
        assert self.config is not None, "login() must be called first"
        api_url = urljoin(self.base_url, self.config["api_challenge"].format(id=challenge_id))

        try:
            resp = self.session.get(api_url, timeout=self.timeout)
            resp.raise_for_status()
            data: Dict[str, Any] = resp.json()

            if data.get("success") and "data" in data:
                return data["data"]  # type: ignore
            elif "data" in data:
                return data["data"]  # type: ignore
            return data  # type: ignore

        except Exception as e:
            self.logger("debug", f"Failed to fetch challenge {challenge_id}: {e}")
            return None

    def download_file(self, file_url: str, dest_path: Path) -> bool:
        """Download a challenge file"""
        try:
            if file_url.startswith("/"):
                full_url = urljoin(self.base_url, file_url)
            else:
                full_url = file_url

            resp = self.session.get(full_url, timeout=self.timeout, stream=True)
            resp.raise_for_status()

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True

        except Exception as e:
            self.logger("debug", f"Failed to download {file_url}: {e}")
            return False

    def connect_netcat(self, host: str, port: int) -> str:
        """Connect to netcat service and capture output"""
        import socket

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.nc_timeout)
            sock.connect((host, port))

            data = b""
            try:
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    data += chunk
            except socket.timeout:
                pass
            sock.close()

            return data.decode("utf-8", errors="replace")

        except Exception as e:
            return f"Connection failed: {e}"

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Sanitize filename for filesystem (cross-platform)"""
        # Windows forbidden chars: < > : " / \ | ? *
        # Also handle reserved names
        name = re.sub(r'[<>:"/\\|?*]', "_", name)
        name = name.strip(". ")

        # Windows reserved names
        reserved = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        }
        if name.upper() in reserved:
            name = f"_{name}"

        return name[:255]

    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalize name for case-insensitive, space-insensitive comparison"""
        return name.lower().replace(" ", "").replace("-", "").replace("_", "")

    def detect_api_endpoint(self) -> Optional[str]:
        """Detect and validate the challenges API endpoint by trying multiple endpoints.

        Returns the working API endpoint path if found, None otherwise.
        """
        self.logger("info", "Detecting challenges API endpoint...")

        for endpoint in CTFD_API_ENDPOINTS:
            api_url = urljoin(self.base_url, endpoint)
            self.logger("debug", f"Trying API endpoint: {api_url}")

            try:
                resp = self.session.get(api_url, timeout=10)
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        # Check if response has expected structure
                        if "data" in data or "results" in data or isinstance(data, list):
                            self.logger("success", f"Found working API endpoint: {endpoint}")
                            return endpoint
                    except Exception:
                        continue
                elif resp.status_code == 401:
                    # Unauthorized but endpoint exists
                    self.logger("success", f"Found API endpoint (requires auth): {endpoint}")
                    return endpoint
                elif resp.status_code == 403:
                    # Forbidden but endpoint exists
                    self.logger("success", f"Found API endpoint (forbidden): {endpoint}")
                    return endpoint
            except Exception as e:
                self.logger("debug", f"Endpoint {endpoint} failed: {e}")
                continue

        self.logger("error", "Could not find a working challenges API endpoint")
        return None

    def organize_challenges(
        self,
        download_files: bool = True,
        connect_nc: bool = True,
        malware_scan: bool = True,
        quarantine_dir: Optional[str] = None,
        max_scan_time: int = 60,
    ):
        """Organize all challenges into category/challenge folders"""
        self.logger("info", f"Organizing {len(self.challenges)} challenges...")

        self._load_metadata()

        if self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.output_dir.mkdir(parents=True, exist_ok=True)

        # Group by category
        categories: Dict[str, List[Dict]] = {}
        for c in self.challenges:
            cat = c.get("category", "Unknown")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(c)

        for cat_name, challenges in categories.items():
            cat_dir = self.output_dir / self.sanitize_filename(cat_name)
            cat_dir.mkdir(exist_ok=True)

            challenges.sort(key=lambda x: x.get("value", 0))

            # Load existing challenges in this category
            existing_challenges = set()
            if cat_dir.exists():
                for d in cat_dir.iterdir():
                    if d.is_dir():
                        existing_challenges.add(d.name)

            # Determine which challenges need overwrite handling
            challenges_to_process = []
            skip_all = False
            overwrite_all = False

            for c in challenges:
                chal_name = self.sanitize_filename(
                    c.get("name", f"challenge_{c.get('id', 'unknown')}")
                )

                if chal_name in existing_challenges:
                    if overwrite_all:
                        challenges_to_process.append(c)
                    elif skip_all:
                        self.logger("info", f"Skipping existing challenge: {c.get('name')}")
                    else:
                        # Count how many challenges would be overwritten
                        overwrite_count = sum(
                            1
                            for c in challenges
                            if self.sanitize_filename(
                                c.get("name", f"challenge_{c.get('id', 'unknown')}")
                            )
                            in existing_challenges
                        )

                        if overwrite_count > 1 and not hasattr(self, "_overwrite_all"):
                            # Ask user for batch decision
                            decision = self._prompt_overwrite_batch(
                                len(
                                    existing_challenges
                                    & set(
                                        self.sanitize_filename(
                                            c.get("name", f"challenge_{c.get('id', 'unknown')}")
                                        )
                                        for c in challenges
                                    )
                                )
                            )
                            if decision == "all":
                                overwrite_all = True
                                challenges_to_process.append(c)
                            elif decision == "skip":
                                skip_all = True
                                self.logger("info", f"Skipping existing challenge: {c.get('name')}")
                            elif decision == "y":
                                challenges_to_process.append(c)
                            else:  # n
                                self.logger("info", f"Skipping existing challenge: {c.get('name')}")
                        else:
                            # Single or already decided
                            decision = self._prompt_overwrite(c.get("name", "Unknown"))
                            if decision == "y":
                                challenges_to_process.append(c)
                            else:
                                self.logger("info", f"Skipping existing challenge: {c.get('name')}")
                else:
                    challenges_to_process.append(c)

            # Process challenges
            for c in challenges_to_process:
                chal_name = self.sanitize_filename(
                    c.get("name", f"challenge_{c.get('id', 'unknown')}")
                )
                chal_dir = cat_dir / chal_name
                chal_dir.mkdir(exist_ok=True)

                # Write info.txt
                self._write_info_file(c, chal_dir)

                # Download files
                if download_files:
                    files = c.get("files", [])
                    if files:
                        files_dir = chal_dir / "files"
                        files_dir.mkdir(exist_ok=True)

                        for file_url in files:
                            filename = file_url.split("/")[-1].split("?")[0]
                            if not filename or filename == "chall":
                                filename = f"file_{c.get('id', 'unknown')}"
                            dest = files_dir / self.sanitize_filename(filename)
                            if not dest.exists():
                                self.logger("info", f"Downloading {c['name']} -> {filename}")
                                self.download_file(file_url, dest)
                                time.sleep(self.delay)

                # Connect to netcat
                if connect_nc:
                    conn_info = c.get("connection_info", "")
                    if conn_info and "nc " in conn_info:
                        nc_match = re.search(r"nc\s+(\S+)\s+(\d+)", conn_info)
                        if nc_match:
                            host, port = nc_match.group(1), int(nc_match.group(2))
                            self.logger("info", f"Connecting to nc {host} {port}...")
                            output = self.connect_netcat(host, port)
                            nc_file = chal_dir / "nc_output.txt"
                            with open(nc_file, "w", encoding="utf-8") as f:
                                f.write(f"Connection: nc {host} {port}\n")
                                f.write(f"Output:\n{output}\n")
                            time.sleep(self.delay)

        # Save metadata
        self._save_metadata(categories)

        # Save summary JSON
        self._save_summary(categories)
        self.logger("success", f"Done! Data saved to {self.output_dir}")

    def _write_info_file(self, challenge: Dict, chal_dir: Path):
        """Write challenge info.txt"""
        info_file = chal_dir / "info.txt"
        with open(info_file, "w", encoding="utf-8") as f:
            f.write(f"Challenge: {challenge.get('name', 'Unknown')}\n")
            f.write(f"ID: {challenge.get('id', 'N/A')}\n")
            f.write(f"Category: {challenge.get('category', 'N/A')}\n")
            f.write(f"Points: {challenge.get('value', 'N/A')}\n")
            f.write(f"Solves: {challenge.get('solves', 'N/A')}\n")
            f.write(f"Type: {challenge.get('type', 'N/A')}\n")
            if challenge.get("attribution"):
                f.write(f"Author: {challenge['attribution']}\n")
            if challenge.get("connection_info"):
                f.write(f"Connection: {challenge['connection_info']}\n")
            if challenge.get("tags"):
                tags = []
                for t in challenge["tags"]:
                    if isinstance(t, dict):
                        tags.append(t.get("value", str(t)))
                    else:
                        tags.append(str(t))
                f.write(f"Tags: {', '.join(tags)}\n")
            f.write(f"\nDescription:\n{challenge.get('description', 'No description')}\n")
            if challenge.get("hints"):
                f.write("\nHints:\n")
                for hint in challenge["hints"]:
                    hint_text = hint.get("content", hint.get("hint", str(hint)))
                    f.write(f"  - {hint_text}\n")

    def _save_summary(self, categories: Dict):
        """Save summary.json"""
        summary_file = self.output_dir / "summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "ctf_url": self.base_url,
                    "platform": self.platform,
                    "total_challenges": len(self.challenges),
                    "categories": {k: len(v) for k, v in categories.items()},
                    "challenges": [
                        {
                            "id": c.get("id"),
                            "name": c.get("name"),
                            "category": c.get("category"),
                            "value": c.get("value"),
                            "solves": c.get("solves"),
                            "connection_info": c.get("connection_info"),
                            "has_files": bool(c.get("files")),
                            "has_nc": "nc " in (c.get("connection_info") or ""),
                        }
                        for c in self.challenges
                    ],
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

    def run(
        self,
        download_files: bool = True,
        connect_nc: bool = True,
        max_challenges: Optional[int] = None,
        malware_scan: bool = True,
        quarantine_dir: Optional[str] = None,
        max_scan_time: int = 60,
    ) -> bool:
        """Main execution flow"""
        self.logger("info", "Starting CTF Challenge Scraper")
        self.logger("info", f"Target: {self.base_url}")
        self.logger("info", f"Platform: {self.platform}")
        self.logger("info", f"Output: {self.output_dir}")

        if self.platform == "auto":
            self.platform = self.detect_platform()
            self.logger("info", f"Detected platform: {self.platform}")

        if not self.login():
            return False

        challenge_list = self.fetch_challenges_list()
        if not challenge_list:
            return False

        if max_challenges:
            challenge_list = challenge_list[:max_challenges]

        self.logger("info", f"Fetching details for {len(challenge_list)} challenges...")
        for i, chal in enumerate(challenge_list, 1):
            if self._shutdown:
                self.logger("warning", "Shutdown requested, saving progress...")
                break
            chal_id = chal.get("id")
            if chal_id is None:
                continue
            name = chal.get("name", str(chal_id))
            self.logger("info", f"[{i}/{len(challenge_list)}] {name} (ID: {chal_id})")
            details = self.fetch_challenge_details(chal_id)
            if details:
                self.challenges.append(details)
                # Save metadata incrementally after each challenge
                self._save_incremental_metadata()
            time.sleep(self.delay)

        self.organize_challenges(
            download_files=download_files,
            connect_nc=connect_nc,
            malware_scan=malware_scan,
            quarantine_dir=quarantine_dir,
            max_scan_time=max_scan_time,
        )
        return True

    def run_selective(
        self,
        category_filter: Optional[List[str]] = None,
        challenge_filter: Optional[Dict[str, List[str]]] = None,
        download_files: bool = True,
        connect_nc: bool = True,
        malware_scan: bool = True,
        quarantine_dir: Optional[str] = None,
        max_scan_time: int = 60,
    ) -> bool:
        """Selective scraping with category and challenge filters"""
        self.logger("info", "Starting CTF Challenge Scraper (Selective Mode)")
        self.logger("info", f"Target: {self.base_url}")
        self.logger("info", f"Platform: {self.platform}")
        self.logger("info", f"Output: {self.output_dir}")

        if self.platform == "auto":
            self.platform = self.detect_platform()
            self.logger("info", f"Detected platform: {self.platform}")

        if not self.login():
            return False

        challenge_list = self.fetch_challenges_list()
        if not challenge_list:
            return False

        # Apply category filter
        if category_filter:
            category_filter_norm = {self.normalize_name(c) for c in category_filter}
            challenge_list = [
                c
                for c in challenge_list
                if self.normalize_name(c.get("category", "Unknown")) in category_filter_norm
            ]

        if not challenge_list:
            self.logger("warning", "No challenges match the category filter")
            return False

        self.logger("info", f"Fetching details for {len(challenge_list)} challenges...")
        for i, chal in enumerate(challenge_list, 1):
            chal_id = chal.get("id")
            if chal_id is None:
                continue
            name = chal.get("name", str(chal_id))
            self.logger("info", f"[{i}/{len(challenge_list)}] {name} (ID: {chal_id})")
            details = self.fetch_challenge_details(chal_id)
            if details:
                self.challenges.append(details)
            time.sleep(self.delay)

        # Apply challenge filter
        if challenge_filter:
            self.challenges = self._apply_challenge_filter(self.challenges, challenge_filter)

        self.organize_challenges(
            download_files=download_files,
            connect_nc=connect_nc,
            malware_scan=malware_scan,
            quarantine_dir=quarantine_dir,
            max_scan_time=max_scan_time,
        )
        return True

    def _apply_challenge_filter(
        self,
        challenges: List[Dict],
        challenge_filter: Dict[str, List[str]],
    ) -> List[Dict]:
        """Apply challenge filter by category"""
        # Build normalized filter: category -> set of normalized challenge names
        filter_map: Dict[str, set] = {}
        for cat, chals in challenge_filter.items():
            cat_norm = self.normalize_name(cat)
            filter_map[cat_norm] = {self.normalize_name(c) for c in chals}

        filtered = []
        for c in self.challenges:
            cat = c.get("category", "Unknown")
            cat_norm = self.normalize_name(cat)
            name = c.get("name", "")
            name_norm = self.normalize_name(name)

            if cat_norm in filter_map:
                if name_norm in filter_map[cat_norm]:
                    filtered.append(c)
            else:
                # Category not in filter, include it
                filtered.append(c)

        return filtered

    def _get_metadata_path(self) -> Path:
        """Get path to metadata file"""
        return self.output_dir / ".ctfscrapper_meta.json"

    def _load_metadata(self) -> Dict:
        """Load existing metadata"""
        meta_path = self._get_metadata_path()
        if meta_path.exists():
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    return json.load(f)  # type: ignore
            except Exception:
                return {}
        return {}

    def _save_incremental_metadata(self):
        """Save metadata incrementally after each challenge"""
        if not self.challenges:
            return
        # Build categories from current challenges
        categories: Dict[str, List[Dict]] = {}
        for c in self.challenges:
            cat = c.get("category", "Unknown")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(c)
        self._save_metadata(categories)

    def _save_metadata(self, categories: Dict):
        """Save metadata about scraped challenges"""
        meta = {
            "ctf_url": self.base_url,
            "platform": self.platform,
            "categories": {
                cat: [c.get("name", "") for c in challenges]
                for cat, challenges in categories.items()
            },
            "last_scraped": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self._get_metadata_path(), "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger("warning", f"Failed to save metadata: {e}")

    def _prompt_overwrite(self, challenge_name: str) -> str:
        """Prompt user for single challenge overwrite"""
        while True:
            choice = (
                input(f"Challenge '{challenge_name}' already exists. Overwrite? (y/n): ")
                .strip()
                .lower()
            )
            if choice in ("y", "yes"):
                return "y"
            elif choice in ("n", "no"):
                return "n"
            print("Please enter 'y' or 'n'")

    def _prompt_overwrite_batch(self, count: int) -> str:
        """Prompt user for batch overwrite decision"""
        while True:
            choice = (
                input(f"{count} challenges already exist. Overwrite? (y/n/all/skip): ")
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
