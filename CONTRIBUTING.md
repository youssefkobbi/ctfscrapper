# Contributing to ctfscrapper

Thank you for your interest in contributing! 🎉

## Ways to Contribute

- 🐛 **Bug Reports** - Found an issue? Let us know!
- 💡 **Feature Requests** - Have an idea? Open a discussion!
- 🔧 **Code Contributions** - Fix bugs, add features
- 📚 **Documentation** - Improve docs, add examples
- 🧪 **Testing** - Test on different platforms/CTFs

## Getting Started

### Prerequisites

- Python 3.8+
- Git
- A CTF account for testing (or use a local CTFd instance)

### Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/ctfscrapper.git
cd ctfscrapper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest
```

## Code Style

We use:
- **Black** for formatting
- **Flake8** for linting
- **MyPy** for type checking
- **Conventional Commits** for commit messages

```bash
# Format
black ctfscrapper/

# Lint
flake8 ctfscrapper/

# Type check
mypy ctfscrapper/
```

## Adding a New Platform

1. Add platform config to `PLATFORMS` dict in `core.py`
2. Implement platform-specific auth in `login()` method
3. Add detection logic in `detect_platform()`
4. Add tests in `tests/`
5. Update documentation

Example platform config:
```python
'myplatform': {
    'api_challenges': '/api/v1/challenges',
    'api_challenge': '/api/v1/challenges/{id}',
    'login_field': 'email',
    'password_field': 'password',
    'nonce_field': 'csrf_token',
    'nonce_patterns': [
        r'csrf_token["\']?\s*:\s*["\']([^"\']+)["\']',
    ],
}
```

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=ctfscrapper

# Specific test
pytest tests/test_ctfd.py -v
```

### Writing Tests

```python
# tests/test_core.py
import pytest
from ctfscrapper.core import CTFScraper

def test_sanitize_filename():
    assert CTFScraper.sanitize_filename("test<>file") == "test__file"
    assert CTFScraper.sanitize_filename("CON") == "_CON"  # Windows reserved

def test_detect_platform(mocker):
    # Mock requests and test detection
    pass
```

## Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** with conventional commits: `git commit -m "feat: add amazing feature"`
4. **Push** to your fork: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat(ctfd): add support for CTFd v3.5 API changes`
- `fix(nc): handle timeout on slow connections`
- `docs(readme): add Windows installation instructions`

## Reporting Issues

### Bug Report Template

```markdown
**Platform**: CTFd / NoCTF / Generic / Other
**ctfscrapper version**: 
**Python version**: 
**OS**: Linux / Windows / macOS

**Description**:
Clear description of the bug

**Steps to Reproduce**:
1. Run `ctfscrapper -u ...`
2. Observe error

**Expected Behavior**:
What should happen

**Actual Behavior**:
What actually happens (include error traceback)

**Logs**:
```
paste relevant logs here
```
```

## Security

If you discover a security vulnerability, please email security@example.com instead of opening a public issue.

## Code of Conduct

Be respectful, inclusive, and constructive. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Questions?

- Open a [Discussion](https://github.com/yourusername/ctfscrapper/discussions)
- Check existing [Issues](https://github.com/yourusername/ctfscrapper/issues)
- Read the [Wiki](https://github.com/yourusername/ctfscrapper/wiki)

Thank you for contributing! 🙏
