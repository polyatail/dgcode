from setuptools import setup, find_packages

with open("audioserver/version.py") as version_file:
    exec(version_file.read())

setup(
    name="audioserver",
    version=__version__,
    packages=find_packages(exclude=["*test*"]),
    install_requires=[
        "aiohttp>=3.6.1",
        "click>=7.0.0",
    ],
    extras_require={
        "all": [
            "black>=19.3b0",
            "flake8>=3.7.8",
            "pip-tools>=4.0.0",
            "pydocstyle>=4.0.0",
            "pytest>=5.1.0",
            "pytest-asyncio>=0.10.0",
        ]
    },
    entry_points={"console_scripts": ["audioserver = audioserver.cli:audioserver_cli"]},
)
