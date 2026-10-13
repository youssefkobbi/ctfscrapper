# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security
vulnerability in ctfscrapper, please report it responsibly.

**Please do NOT open a public issue for security vulnerabilities.**

Instead, please email us at **security@example.com** with:

- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Any suggested fixes (if you have them)

We will acknowledge receipt within 48 hours and provide a more detailed
response within 7 days. We will work with you to understand and resolve
the issue promptly.

## Security Best Practices for Users

When using ctfscrapper:

1. **Never commit credentials** to version control
   - Use environment variables (`CTFSCRAPPER_USER`, `CTFSCRAPPER_PASS`)
   - Or use the interactive mode which prompts for credentials

2. **Use SSL verification** (enabled by default)
   - Only disable with `--no-verify-ssl` for self-signed certs in trusted environments

3. **Be cautious with netcat connections**
   - The tool connects to remote services specified in challenge data
   - Only use on trusted CTF platforms

4. **Review downloaded files**
   - Challenge files may contain binaries, scripts, or other executables
   - Analyze in isolated environments (VMs, containers)

## Scope

This security policy covers the ctfscrapper tool itself. It does not cover:
- The CTF platforms you connect to
- Challenge files downloaded from CTF platforms
- Your local environment security

## Disclosure Timeline

1. **Day 0**: Vulnerability reported privately
2. **Day 1-2**: Acknowledgment and initial assessment
3. **Day 3-7**: Detailed analysis and fix development
4. **Day 7-14**: Testing and preparation of release
5. **Day 14+**: Public release and advisory (coordinated with reporter)

We aim to release fixes within 14 days of verified reports.
