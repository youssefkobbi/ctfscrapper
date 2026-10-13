"""Setup script for ctfscrapper"""

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='ctfscrapper',
    version='1.0.0',
    author='CTF Player',
    author_email='ctfplayer@example.com',
    description='Universal CTF Challenge Scraper for CTFd, NoCTF, and generic platforms',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/ctfscrapper',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/ctfscrapper/issues',
        'Source': 'https://github.com/yourusername/ctfscrapper',
        'Documentation': 'https://github.com/yourusername/ctfscrapper/wiki',
    },
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Security',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-cov>=4.0',
            'black>=23.0',
            'flake8>=6.0',
            'mypy>=1.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'ctfscrapper=ctfscrapper.cli:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
