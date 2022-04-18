from pathlib import Path

from setuptools import setup


readme = Path("README.md").read_text(encoding="utf-8")
version = Path("sec_edgar_downloader/_version.py").read_text(encoding="utf-8")
with open('requirements.txt') as f:
    required = f.read().splitlines()
about = {}
exec(version, about)


setup(
    name='sec-edgar-extractor',
    version='0.1.0',
    author="Jason Beach",
    description="Extract information from unstructured SEC filings, such as 8-K",
    long_description=readme,
    url="https://github.com/IMTorgOpenDataTools/sec-edgar-extractor",
    packages=['sec_edgar_extractor'],
    python_requires=">=3.10",
    install_reqs = required
)