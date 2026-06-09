"""
Setup configuration for Argus
Educational Application for Network Security Learning
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Argus",
    version="1.0.0",
    author="Argus",
    author_email="education@example.com",
    description="Educational MITM Attack Tool for Learning Network Security",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BH-Unknown/Argus",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Topic :: Education :: Computer Science",
        "Topic :: System :: Networking",
        "Topic :: Security :: Cryptography",
        "License :: Free for Educational Use",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.7",
    install_requires=[
        "PySide6>=6.0.0",
        "scapy>=2.4.5",
        "psutil>=5.8.0",
        "matplotlib>=3.3.0",
        "networkx>=2.5",
    ],
    entry_points={
        "console_scripts": [
            "mitm-tool=mitm_gui:main",
        ],
    },
    keywords="MITM ARP-Spoof Network-Security Education Cybersecurity",
    project_urls={
        "Documentation": "https://github.com/BH-Unknown/Argus/docs",
        "Source": "https://github.com/BH-Unknown/Argus",
        "Tracker": "https://github.com/BH-Unknown/Argus/issues",
    },
    zip_safe=False,
)
