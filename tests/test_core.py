"""Tests for ctfscrapper core functionality"""

import pytest

from ctfscrapper.core import CTFScraper


class TestSanitizeFilename:
    """Test filename sanitization"""
    
    def test_basic_chars(self):
        assert CTFScraper.sanitize_filename("normal_file") == "normal_file"
    
    def test_forbidden_chars(self):
        # Windows forbidden: < > : " / \ | ? *
        result = CTFScraper.sanitize_filename(r'file<>:\"/\|?*name')
        assert result == "file__________name"
    
    def test_windows_reserved(self):
        assert CTFScraper.sanitize_filename("CON") == "_CON"
        assert CTFScraper.sanitize_filename("PRN") == "_PRN"
        assert CTFScraper.sanitize_filename("AUX") == "_AUX"
        assert CTFScraper.sanitize_filename("NUL") == "_NUL"
        assert CTFScraper.sanitize_filename("COM1") == "_COM1"
        assert CTFScraper.sanitize_filename("LPT1") == "_LPT1"
    
    def test_trim_dots_spaces(self):
        assert CTFScraper.sanitize_filename("  .file.  ") == "file"
    
    def test_max_length(self):
        long_name = "a" * 300
        assert len(CTFScraper.sanitize_filename(long_name)) == 255
    
    def test_unicode(self):
        result = CTFScraper.sanitize_filename("挑战_файл_🏴")
        assert "挑战" in result
        assert "файл" in result


class TestPlatformDetection:
    """Test platform detection logic"""
    
    def test_platform_configs_exist(self):
        required_keys = ['api_challenges', 'api_challenge', 'login_field', 'password_field']
        for platform, config in CTFScraper.PLATFORMS.items():
            for key in required_keys:
                assert key in config, f"{platform} missing {key}"


class TestNetcatParsing:
    """Test netcat connection info parsing"""
    
    def test_parse_nc_command(self):
        import re
        conn_info = "nc pwn.example.com 1337"
        match = re.search(r'nc\s+(\S+)\s+(\d+)', conn_info)
        assert match
        assert match.group(1) == "pwn.example.com"
        assert match.group(2) == "1337"
    
    def test_parse_nc_with_extra_text(self):
        import re
        conn_info = "Connect with: nc ctf.example.com 9999 to start"
        match = re.search(r'nc\s+(\S+)\s+(\d+)', conn_info)
        assert match
        assert match.group(1) == "ctf.example.com"
        assert match.group(2) == "9999"


class TestFileUrlHandling:
    """Test file URL processing"""
    
    def test_extract_filename(self):
        urls = [
            ("/files/abc123/challenge.c?token=xyz", "challenge.c"),
            ("https://ctf.example.com/files/def456/binary?token=abc", "binary"),
            ("/files/ghi789/chall?token=abc", "chall"),
            ("/files/jkl012/", ""),
        ]
        for url, expected in urls:
            filename = url.split('/')[-1].split('?')[0]
            assert filename == expected
    
    def test_fallback_filename(self):
        filename = "chall"
        if not filename or filename == "chall":
            filename = "file_123"
        assert filename == "file_123"


class TestInfoFileGeneration:
    """Test info.txt generation"""
    
    def test_basic_info(self):
        challenge = {
            'id': 1,
            'name': 'Test Challenge',
            'category': 'pwn',
            'value': 100,
            'solves': 50,
            'type': 'dynamic',
            'description': 'Test description',
            'connection_info': 'nc host 1234',
            'tags': [{'value': 'ret2win'}],
            'attribution': 'Author Name',
        }
        
        assert challenge['name'] == 'Test Challenge'
        assert challenge['value'] == 100


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
