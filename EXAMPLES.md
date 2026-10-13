# Usage Examples

## Basic CTFd Scrape

```bash
# Full scrape with all features
ctfscrapper \
  --url https://ctf.example.com \
  --user myuser \
  --pass mypass \
  --output my_ctf_data \
  --platform ctfd
```

## Quick Recon

```bash
# Just metadata, no files, no netcat, limit to 10 challenges
ctfscrapper \
  -u https://ctf.example.com \
  -U player1 \
  -P secret \
  --no-files \
  --no-nc \
  --max 10 \
  -o quick_recon
```

## Using Environment Variables

```bash
# Set once in your shell profile
export CTFSCRAPPER_URL="https://ctf.example.com"
export CTFSCRAPPER_USER="myuser"
export CTFSCRAPPER_PASS="mypass"

# Then just run
ctfscrapper -o my_ctf_data
```

## Windows PowerShell

```powershell
# Using environment variables
$env:CTFSCRAPPER_URL = "https://ctf.example.com"
$env:CTFSCRAPPER_USER = "myuser"
$env:CTFSCRAPPER_PASS = "mypass"

ctfscrapper -o ctf_data

# Or with explicit args
python -m ctfscrapper -u https://ctf.example.com -U user -P pass -o ctf_data
```

## CI/CD Integration

### GitHub Actions

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
        run: |
          pip install ctfscrapper
      
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
# .gitlab-ci.yml
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

## Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
RUN pip install ctfscrapper

ENTRYPOINT ["ctfscrapper"]
```

```bash
# Build
docker build -t ctfscrapper .

# Run
docker run --rm \
  -v $(pwd)/output:/output \
  ctfscrapper \
  -u https://ctf.example.com \
  -U user -P pass \
  -o /output/ctf-data
```

## Python API

```python
from ctfscrapper import CTFScraper

# Basic usage
scraper = CTFScraper(
    base_url="https://ctf.example.com",
    username="user",
    password="pass",
    platform="ctfd",
    output_dir="my_ctf_data",
)

success = scraper.run()

# With custom options
scraper = CTFScraper(
    base_url="https://ctf.example.com",
    username="user",
    password="pass",
    platform="ctfd",
    output_dir="my_ctf_data",
    timeout=60,           # Longer HTTP timeout
    nc_timeout=30,        # Longer netcat timeout
    delay=0.5,            # Slower requests
)

# Only metadata
success = scraper.run(download_files=False, connect_nc=False)

# Limit challenges for testing
success = scraper.run(max_challenges=5)

# Custom logger
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("myapp")

scraper = CTFScraper(
    ...,
    logger=lambda level, msg: logger.log(
        {"info": logging.INFO, "success": logging.INFO,
         "warning": logging.WARNING, "error": logging.ERROR, "debug": logging.DEBUG}[level], msg
    ),
)
```

## Specific Platform Examples

### CTFd (Most Common)

```bash
# Auto-detect (recommended)
ctfscrapper -u https://ctf.example.com -U user -P pass

# Explicit
ctfscrapper -u https://ctf.example.com -U user -P pass --platform ctfd

# Custom login URL
ctfscrapper -u https://ctf.example.com -U user -P pass --login-url https://ctf.example.com/login
```

### NoCTF

```bash
ctfscrapper -u https://ctf.example.com -U user -P pass --platform noctf
```

### Generic/Unknown

```bash
# Tries common API endpoints
ctfscrapper -u https://ctf.example.com -U user -P pass --platform generic

# Or let it auto-detect
ctfscrapper -u https://ctf.example.com -U user -P pass
```

## Advanced Options

```bash
# Increase timeouts for slow CTFs
ctfscrapper -u https://ctf.example.com -U user -P pass \
  --timeout 60 --nc-timeout 30 --delay 0.5

# Disable SSL verification (self-signed certs)
ctfscrapper -u https://ctf.example.com -U user -P pass --no-verify-ssl

# Quiet mode for scripts
ctfscrapper -u https://ctf.example.com -U user -P pass -q -o data

# Verbose for debugging
ctfscrapper -u https://ctf.example.com -U user -P pass -v
```

## Output Processing

```bash
# After scraping, process the summary
cat ctf-data/summary.json | jq '.categories'

# Find all pwn challenges with netcat
cat ctf-data/summary.json | jq '.challenges[] | select(.category=="pwn" and .has_nc) | .name'

# List challenges by points
cat ctf-data/summary.json | jq '.challenges[] | "\(.value)pts: \(.name) [\(.category)]"'

# Find challenges with files
cat ctf-data/summary.json | jq '.challenges[] | select(.has_files) | "\(.name): \(.category)"'
```

## Troubleshooting

```bash
# Debug login issues
ctfscrapper -u https://ctf.example.com -U user -P pass -v --platform ctfd

# Test with single challenge
ctfscrapper -u https://ctf.example.com -U user -P pass --max 1 -v

# Skip problematic features
ctfscrapper -u https://ctf.example.com -U user -P pass --no-files --no-nc
```