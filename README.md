# ctfscrapper 🏴‍☠️

> **Universal CTF Challenge Scraper** - Scrape, organize, and prepare CTF challenges from any platform

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg)]()
[![Status](https://img.shields.io/badge/Status-Beta-yellow.svg)]()

```
    ██████╗██╗  ██╗███████╗███████╗████████╗ ██████╗ ██████╗ ███╗   ██╗
   ██╔════╝██║  ██║██╔════╝██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗████╗  ██║
   ██║     ███████║█████╗  ███████╗   ██║   ██║   ██║██████╔╝██╔██╗ ██║
   ██║     ██╔══██║██╔═══╝  ╚════██║   ██║   ██║   ██║██╔══██╗██║╚██╗██║
   ╚██████╗██║  ██║███████╗███████║   ██║   ╚██████╔╝██║  ██║██║ ╚████║
    ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝
              Universal CTF Challenge Scraper v1.0.0
```

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **Multi-Platform** | CTFd, NoCTF, and generic REST APIs |
| 🔐 **Smart Auth** | Auto-detects CSRF tokens, handles nonces |
| 📥 **File Download** | Downloads all challenge attachments (binaries, source, PCAPs, images) |
| 🔌 **Netcat Capture** | Connects to `nc` services and captures initial output/banners |
| 📁 **Organized Output** | `category/challenge_name/` with `info.txt`, `files/`, `nc_output.txt` |
| 📊 **Summary Index** | `summary.json` with complete challenge metadata |
| ⚡ **Fast & Resilient** | Retries, timeouts, rate limiting, resume capability |
| 🖥️ **Cross-Platform** | Linux, Windows, macOS (Python 3.8+) |

## 🚀 Quick Start

### Installation

```bash
# From PyPI (when published)
pip install ctfscrapper

# From source
git clone https://github.com/youssefkobbi/ctfscrapper.git
cd ctfscrapper
pip install -e .

# Or run directly without install
python -m ctfscrapper --help
```

### Basic Usage

```bash
# CTFd (auto-detected)
ctfscrapper -u https://ctf.example.com -U myuser -P mypass

# Explicit platform
ctfscrapper -u https://ctf.example.com -U user -P pass --platform ctfd

# NoCTF
ctfscrapper -u https://ctf.example.com -U user -P pass --platform noctf

# Custom output directory
ctfscrapper -u https://ctf.example.com -U user -P pass -o my_ctf_data
```

### Environment Variables

```bash
export CTFSCRAPPER_URL="https://ctf.example.com"
export CTFSCRAPPER_USER="myuser"
export CTFSCRAPPER_PASS="mypass"

# Now just run:
ctfscrapper
```

## 📁 Output Structure

```
ctf-data/
├── pwn/
│   ├── Baby_Win/
│   │   ├── info.txt              # Challenge metadata + description
│   │   ├── files/
│   │   │   ├── challenge.c       # Source code
│   │   │   └── chall             # Binary
│   │   └── nc_output.txt         # "=== CTF baby_win ===\nTell me a story:"
│   ├── Libc_Voyage/
│   │   ├── info.txt
│   │   ├── files/
│   │   │   ├── libc_voyage
│   │   │   ├── libc_voyage.c
│   │   │   ├── libc.so.6
│   │   │   └── ld-linux-x86-64.so.2
│   │   └── nc_output.txt
│   └── ...
├── Cryptography/
│   ├── Reused_key/
│   │   ├── info.txt
│   │   ├── files/
│   │   │   ├── message_a.txt
│   │   │   └── message_b.txt
│   │   └── nc_output.txt
│   └── ...
├── Web/
│   ├── Hash_Comparison/
│   │   ├── info.txt
│   │   └── nc_output.txt         # HTTP connection info
│   └── ...
├── Reverse_Engineering/
├── DFIR/
├── OSINT/
├── misc/
├── Cyber_Threat_Intelligence/
└── summary.json                  # Complete challenge index
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

## 📖 Command Reference

```
ctfscrapper [OPTIONS]

Required:
  -u, --url URL           CTF base URL
  -U, --user USER         Username
  -P, --pass PASS         Password

Platform:
  --platform CHOICE       auto|ctfd|noctf|generic (default: auto)
  --login-url URL         Custom login endpoint

Output:
  -o, --output DIR        Output directory (default: ctf-data)
  --no-files              Skip file downloads
  --no-nc                 Skip netcat connections
  --max N                 Limit challenges to process

Network:
  --timeout SEC           HTTP timeout (default: 30)
  --nc-timeout SEC        Netcat timeout (default: 10)
  --delay SEC             Delay between requests (default: 0.1)
  --no-verify-ssl         Disable SSL verification

Display:
  -q, --quiet             Minimal output
  --no-color              Disable colors
  -v, --verbose           Verbose output
  --version               Show version
```

## 🎯 Examples

### Full Scrape with All Features

```bash
ctfscrapper \
  -u https://ctf.example.com \
  -U player1 \
  -P secret123 \
  -o ctf_2024 \
  --platform ctfd
```

### Quick Recon (Metadata Only)

```bash
ctfscrapper -u https://ctf.example.com -U u -P p --no-files --no-nc --max 5
```

### CI/CD Pipeline

```bash
# In your CI script
ctfscrapper \
  -u "$CTF_URL" \
  -U "$CTF_USER" \
  -P "$CTF_PASS" \
  -o artifacts/ctf-data \
  --no-nc \
  -q
```

### Windows PowerShell

```powershell
# Works natively on Windows
python -m ctfscrapper -u https://ctf.example.com -U user -P pass
```

## 🔧 Advanced Usage

### As a Python Module

```python
from ctfscrapper import CTFScraper

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

success = scraper.run(download_files=True, connect_nc=True)
```

### Custom Logger

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("ctfscrapper")

scraper = CTFScraper(..., logger=lambda level, msg: logger.log(
    {"info": logging.INFO, "success": logging.INFO, 
     "warning": logging.WARNING, "error": logging.ERROR, "debug": logging.DEBUG}[level], msg
))
```

## 🛠️ Development

```bash
# Clone and setup
git clone https://github.com/youssefkobbi/ctfscrapper.git
cd ctfscrapper
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .[dev]

# Run tests
pytest

# Format code
black ctfscrapper/
flake8 ctfscrapper/
mypy ctfscrapper/
```

## 📋 Supported Platforms

| Platform | API Endpoint | Auth Method | Status |
|----------|-------------|-------------|--------|
| **CTFd** | `/api/v1/challenges` | Form + CSRF nonce | ✅ Full |
| **NoCTF** | `/api/challenges` | JSON POST | ✅ Full |
| **Generic** | `/api/challenges` | Form POST | ✅ Best effort |

## ⚠️ Disclaimer

> **This tool is for educational purposes and authorized CTF participation only.**
> 
> - Only use on platforms you have explicit permission to access
> - Respect CTF rules, rate limits, and terms of service
> - Do not use against production systems without authorization
> - The authors are not responsible for misuse

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

Areas for contribution:
- [ ] Additional platform support (HackTheBox, TryHackMe, etc.)
- [ ] Interactive netcat sessions
- [ ] Challenge solution tracking
- [ ] Export to markdown/writeups
- [ ] Parallel downloads for speed
- [ ] Docker support

## 🙏 Acknowledgments

- CTFd team for the excellent platform
- All CTF organizers and challenge authors
- The CTF community for sharing knowledge