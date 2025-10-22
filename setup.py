#!/usr/bin/env python3
"""
Setup script for Amazon Connect Migration Scripts
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="amazon-connect-migration-scripts",
    version="1.0.0",
    author="Amazon Connect Migration Scripts Contributors",
    description="Comprehensive Python scripts for migrating Amazon Connect resources between instances",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/amazon-connect-migration-scripts",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "Topic :: System :: Systems Administration",
        "Topic :: Communications :: Telephony",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    keywords="amazon-connect, aws, migration, contact-center, telephony",
    project_urls={
        "Bug Reports": "https://github.com/your-username/amazon-connect-migration-scripts/issues",
        "Source": "https://github.com/your-username/amazon-connect-migration-scripts",
        "Documentation": "https://github.com/your-username/amazon-connect-migration-scripts#readme",
    },
)