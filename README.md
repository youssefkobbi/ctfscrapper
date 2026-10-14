# ctfscrapper 🏴‍☠️

> **Universal CTF Challenge Scraper** - Scrape, organize, and prepare CTF challenges from any platform

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg)]()
[![Status](https://img.shields.io/badge/Status-Beta-yellow.svg)]()
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)]()
[![Code Style](https://img.shields.io/badge/Code%20Style-Black-000000.svg)]()

```
    ██████╗██╗  ██╗███████╗███████╗████████╗ ██████╗ ██████╗ ███╗   ██╗
   ██╔════╝██║  ██║██╔════╝██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗████╗  ██║
   ██║     ███████║█████╗  ███████╗   ██║   ██║   ██║██████╔╝██╔██╗ ██║
   ██║     ██╔══██║██╔═══╝  ╚════██║   ██║   ██║   ██║██╔══██╗██║╚██╗██║
   ╚██████╗██║  ██║███████╗███████║   ██║   ╚██████╔╝██║  ██║██║ ╚████║
    ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝
              Universal CTF Challenge Scraper v1.0.0
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **Multi-Platform** | CTFd, NoCTF, and generic REST APIs |
| 🔐 **Smart Auth** | Auto-detects CSRF tokens, handles nonces |
| 📥 **File Download** | Downloads all challenge attachments (binaries, source, PCAPs, images) |
| 🔌 **Netcat Capture** | Connects to `nc` services and captures initial output/banners |
| 📁 **Organized Output** | `CTF_Name/category/challenge_name/` with `info.txt`, `files/`, `nc_output.txt` |
| 📊 **Summary Index** | `summary.json` with complete challenge metadata |
| 🎯 **Selective Scraping** | Choose specific categories and challenges interactively |
| 🔄 **Folder Persistence** | Resume scraping - merges into existing folders, handles overwrites |
| ⚡ **Fast & Resilient** | Retries, timeouts, rate limiting, resume capability |
| 🖥️ **Cross-Platform** | Linux, Windows, macOS (Python 3.8+) |

---

## 📦 Installation

### Prerequisites
- **Python 3.8+** (check with `python3 --version` or `python --version`)
- **pip** (usually comes with Python)
- **git** (for cloning from source)

### 🐧 Linux (Ubuntu/Debian/Kali/Arch/Fedora)

```bash
# Install dependencies
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git

# Clone and install
git clone https://github.com/youssefkobbi/ctfscrapper.git
cd ctfscrapper
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Or install globally (without venv)
pip install -e .
```

**Arch Linux:**
```bash
sudo pacman -S python python-virtualenv git
git clone https://github.com/youssefkobbi/ctfscrapper.git
cd ctfscrapper
python -m venv venv
source venv/bin/activate
pip install -e .
```

**Fedora:**
```bash
sudo dnf install python3 python3-virtualenv git
git clone https://github.com/youssefkobbi/ctfscrapper.git
cd ctfscrapper
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### 🪟 Windows (PowerShell / CMD)

```powershell
# Install Python from https://python.org/downloads (check "Add to PATH")
# Or use winget:
winget install Python.Python.3.11

# Clone and install
git clone https://github.com/youssefkobbi/ctfscrapper.git
cd ctfscrapper
python -m venv venv
venv\Scripts\activate
pip install -e .

# Or install globally
pip install -e .
```

### 🍎 macOS

```bash
# Install via Homebrew
brew install python3 git

# Or install Python from https://python.org/downloads

# Clone and install
git clone https://github.com/youssefkobbi/ctfscrapper.git
cd ctfscrapper
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### 🐳 Docker (Alternative)

```bash
# Build
docker build -t ctfscrapper .

# Run
docker run --rm -it \
  -v $(pwd)/output:/output \
  ctfscrapper \
  -u https://ctf.example.com -U user -P pass -o /output
```

### Verify Installation

```bash
ctfscrapper --help
# Or without install:
python -m ctfscrapper --help
```

---

## 🚀 Quick Start

### 1. Interactive Mode (Recommended for Beginners)

```bash
# Just provide the URL - it will prompt for everything else
ctfscrapper https://ctf.example.com
```

**What happens:**
1. Enter CTF URL → prompts for username/password
2. Select platform (auto-detect / CTFd / NoCTF / Generic)
3. Choose mode: **Selective** (pick categories/challenges) or **Full** (all)
4. For selective: pick categories → pick challenges per category → confirm
5. Scrapes and organizes everything automatically

### 2. Direct Mode (Automation / CI/CD)

```bash
# Full scrape with all options
ctfscrapper \
  -u https://ctf.example.com \
  -U myusername \
  -P mypassword \
  -o my_ctf_data \
  --platform ctfd

# Quick recon (metadata only, fast)
ctfscrapper -u https://ctf.example.com -U user -P pass \
  --no-files --no-nc --max 5 -q

# Use environment variables (recommended for CI/CD)
export CTFSCRAPPER_URL="https://ctf.example.com"
export CTFSCRAPPER_USER="myuser"
export CTFSCRAPPER_PASS="mypassword"
ctfscrapper -o output_dir
```

---

## 📖 Complete Command Reference

```
ctfscrapper [OPTIONS] [URL]

Positional Arguments:
  URL                     CTF base URL (interactive mode if provided without -u)

Required (Direct Mode):
  -u, --url URL           CTF base URL (e.g., https://ctf.example.com)
  -U, --user USER         Username/email
  -P, --pass PASS         Password

Platform Options:
  --platform CHOICE       Platform: auto|ctfd|noctf|generic (default: auto)
  --login-url URL         Custom login endpoint (default: <url>/login)

Output Options:
  -o, --output DIR        Output directory (default: ctf-data)
  --no-files              Skip downloading challenge files
  --no-nc                 Skip netcat connections
  --max N                 Maximum challenges to process (0 = all)

Network Options:
  --timeout SEC           HTTP timeout in seconds (default: 30)
  --nc-timeout SEC        Netcat timeout in seconds (default: 10)
  --delay SEC             Delay between requests in seconds (default: 0.1)
  --no-verify-ssl         Disable SSL certificate verification (for self-signed certs)

Display Options:
  -q, --quiet             Quiet mode (minimal output, no banner)
  --no-color              Disable colored output
  -v, --verbose           Verbose output
  -i, --interactive       Force interactive mode
  --version               Show version
  -h, --help              Show this help message and exit

Environment Variables:
  CTFSCRAPPER_URL         Default CTF URL
  CTFSCRAPPER_USER        Default username
  CTFSCRAPPER_PASS        Default password
```

### Exit Codes
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Login failed / scraping failed |
| 2 | No challenges found |
| 3 | Network error |
| 4 | Invalid arguments |
| 130 | Interrupted by user (Ctrl+C) |

---

## 🎮 Usage Modes

### Mode 1: Selective Scrape (Interactive - Default)

```bash
ctfscrapper https://ctf.example.com
```

**Interactive Flow:**
```
1. Enter username/password
2. Select platform (auto/ctfd/noctf/generic)
3. Choose: [1] Selective Scrape  [2] Full Scrape
4. If Selective:
   - Enter CTF name (for folder)
   - List available categories → enter: Web/Pwn/Crypto
   - For each category: select challenges (Baby Win/Flag Roulette)
   - Add more categories? (y/n)
   - Shows summary → confirm (y/n)
6. Scrapes only selected → organizes into folders
```

**Category/Challenge Selection Syntax:**
```
# Categories (separated by /)
Web
Web/Pwn
Web/Pwn/Crypto
all or everything    # All categories

# Challenges (same syntax)
Baby Win
Baby Win/Flag Roulette
Baby Win/Flag Roulette/Black Flash
all or everything    # All challenges in category
```

**Matching:** Case-insensitive, space-insensitive (e.g., "Baby Win" matches "baby-win")

---

### Mode 2: Full Scrape (All Challenges)

```bash
# Interactive - choose "Full Scrape" at mode selection
ctfscrapper https://ctf.example.com
# Select mode 2 at prompt

# Or direct mode (scrapes everything)
ctfscrapper -u https://ctf.example.com -U user -P pass
```

---

## 📁 Output Structure

```
ctf-data/                           # or custom -o directory
├── CTF_Name/                       # Your CTF name
│   ├── .ctfscrapper_meta.json      # Metadata for persistence
│   ├── summary.json                # Complete index
│   ├── pwn/
│   │   ├── Baby_Win/
│   │   │   ├── info.txt            # Metadata + description
│   │   │   ├── files/
│   │   │   │   ├── challenge.c     # Source code
│   │   │   │   └── chall           # Binary
│   │   │   └── nc_output.txt       # Netcat banner output
│   │   └── Libc_Voyage/
│   │       ├── info.txt
│   │       ├── files/
│   │       │   ├── libc_voyage
│   │       │   ├── libc_voyage.c
│   │       │   ├── libc.so.6
│   │       │   └── ld-linux-x86-64.so.2
│   │       └── nc_output.txt
│   ├── Cryptography/
│   │   ├── Reused_key/
│   │   │   ├── info.txt
│   │   │   ├── files/
│   │   │   │   ├── message_a.txt
│   │   │   │   └── message_b.txt
│   │   │   └── nc_output.txt
│   └── ...
├── summary.json                    # Master index
└── .ctfscrapper_meta.json          # Global metadata
```

### info.txt Format
```
Challenge: Baby Win
ID: 73
Category: pwn
Points: 100
Solves: 49
Type: dynamic
Author: Written by Author Name
Connection: nc pwn.example.com 1300
Tags: ret2win

Description:
A first stack-smashing exercise. Redirect execution to the function that was never called.
```

### summary.json
```json
{
  "ctf_url": "https://ctf.example.com",
  "platform": "ctfd",
  "total_challenges": 138,
  "categories": {
    "pwn": 24,
    "Cryptography": 18,
    "Reverse Engineering": 35,
    "Web": 16,
    "DFIR": 26,
    "misc": 21,
    "OSINT": 7
  },
  "challenges": [
    {
      "id": 73,
      "name": "Baby Win",
      "category": "pwn",
      "value": 100,
      "solves": 49,
      "connection_info": "nc pwn.example.com 1300",
      "has_files": true,
      "has_nc": true
    }
  ]
}
```

---

## 🔄 Folder Persistence & Resume

**Key Feature:** Run the tool multiple times on the same CTF - it merges intelligently!

### How It Works
1. **First run:** Creates `CTF_Name/` folder with selected challenges
2. **Second run (same CTF name + URL):**
   - Detects existing folder
   - Shows existing challenges
   - Prompts for overwrite: `y` (yes), `n` (no), `all` (overwrite all), `skip` (skip all)
   - Merges new challenges into existing folders
   - Updates metadata

### Overwrite Options
| Scenario | Prompt | Options |
|----------|--------|---------|
| 1 existing challenge | "Challenge 'X' exists. Overwrite?" | `y` / `n` |
| Multiple existing | "N challenges exist. Overwrite?" | `y` / `n` / `all` / `skip` |
| `all` | Overwrite all existing | |
| `skip` | Skip all existing | |

---

## 🔧 Advanced Usage

### As a Python Module

```python
from ctfscrapper import CTFScraper, run_interactive

# Basic usage
scraper = CTFScraper(
    base_url="https://ctf.example.com",
    username="user",
    password="pass",
    platform="ctfd",
    output_dir="my_data",
    timeout=30,
    nc_timeout=10,
    delay=0.1,
)

# Full scrape
success = scraper.run(download_files=True, connect_nc=True)

# Selective scrape
success = scraper.run_selective(
    category_filter=["Web", "Pwn"],
    challenge_filter={"Web": ["Hash Comparison"], "Pwn": ["Baby Win"]},
    download_files=True,
    connect_nc=True,
)

# Interactive mode programmatically
run_interactive("https://ctf.example.com", verify_ssl=True)
```

### Custom Logger

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("myapp")

scraper = CTFScraper(
    base_url="https://ctf.example.com",
    username="user",
    password="pass",
    logger=lambda level, msg: logger.log(
        {"info": logging.INFO, "success": logging.INFO, 
         "warning": logging.WARNING, "error": logging.ERROR, "debug": logging.DEBUG}[level], msg
    ),
)
```

### CI/CD Integration (GitHub Actions)

```yaml
# .github/workflows/scrape.yml
name: Scrape CTF Challenges

on:
  workflow_dispatch:
    inputs:
      ctf_url:
        description: 'CTF URL'
        required: true
      ctf_user:
        description: 'Username'
        required: true

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install ctfscrapper
        run: pip install ctfscrapper
      
      - name: Scrape challenges
        run: |
          ctfscrapper \
            -u "${{ github.event.inputs.ctf_url }}" \
            -U "${{ github.event.inputs.ctf_user }}" \
            -P "${{ secrets.CTF_PASSWORD }}" \
            -o artifacts/ctf-data \
            --no-nc \
            -q
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: ctf-challenges
          path: artifacts/ctf-data/
```

### GitLab CI

```yaml
scrape_ctf:
  stage: scrape
  image: python:3.11-slim
  variables:
    PIP_CACHE_DIR: "$CI_PROJECT_DIR/.pip-cache"
  script:
    - pip install ctfscrapper
    - ctfscrapper -u "$CTF_URL" -U "$CTF_USER" -P "$CTF_PASS" -o ctf-data --no-nc -q
  artifacts:
    paths:
      - ctf-data/
    expire_in: 1 week
  only:
    - schedules
```

---

## 🌐 Supported Platforms

| Platform | API Endpoint | Auth Method | Status |
|----------|-------------|-------------|--------|
| **CTFd** | `/api/v1/challenges` | Form + CSRF nonce | ✅ Full |
| **NoCTF** | `/api/challenges` | JSON POST | ✅ Full |
| **Generic** | `/api/challenges` | Form POST | ✅ Best effort |

---

## ⚠️ Disclaimer

> **This tool is for educational purposes and authorized CTF participation only.**
> 
> - Only use on platforms you have explicit permission to access
> - Respect CTF rules, rate limits, and terms of service
> - Do not use against production systems without authorization
> - The authors are not responsible for misuse

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

Areas for contribution:
- [ ] Additional platform support (HackTheBox, TryHackMe, etc.)
- [ ] Interactive netcat sessions
- [ ] Challenge solution tracking
- [ ] Export to markdown/writeups
- [ ] Parallel downloads for speed
- [ ] Docker support

---

## 🙏 Acknowledgments

- CTFd team for the excellent platform
- All CTF organizers and challenge authors
- The CTF community for sharing knowledge

---

**Made with ❤️ for the CTF community**

[⬆ Back to Top](#ctfscrapper-)