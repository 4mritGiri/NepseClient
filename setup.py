"""NEPSE Client - Nepal Stock Exchange Python Client - Setup configuration file."""

from pathlib import Path

from setuptools import find_packages, setup


# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = [
    "httpx>=0.24.0",
    "pywasm>=1.0.8",
    "tqdm>=4.65.0",
]

dev_requirements = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
    "pre-commit>=3.0.0",
]

setup(
    name="nepse-client",
    version="0.1.1",
    author="Amrit Giri",
    author_email="amritgiri.dev@gmail.com",
    description="A comprehensive Python client for Nepal Stock Exchange (NEPSE) API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/4mritgiri/NepseClient",
    project_urls={
        "Bug Reports": "https://github.com/4mritgiri/NepseClient/issues",
        "Source": "https://github.com/4mritgiri/NepseClient",
        "Documentation": "https://NepseClient.readthedocs.io",
    },
    packages=find_packages(exclude=["tests", "tests.*", "docs"]),
    package_data={
        "nepse_client": [
            "data/*.json",
            "data/*.wasm",
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "django": ["django>=3.2"],
    },
    keywords="NEPSE nepal stock exchange finance trading api client",
    zip_safe=False,
)
