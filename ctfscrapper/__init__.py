"""ctfscrapper - Universal CTF Challenge Scraper"""

from .core import CTFScraper
from .interactive import run_interactive

__version__ = "1.0.0"
__author__ = "CTF Player"
__description__ = "Scrape challenges from CTFd, NoCTF, and generic CTF platforms"

__all__ = ["CTFScraper", "run_interactive"]
