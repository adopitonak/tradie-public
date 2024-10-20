import os
from setuptools import setup, find_packages     # type: ignore

base_packages = ["rich>=13.6", "typer>=0.9", "structlog>=23.2", "python-dotenv>=1.0.1",
                 "python-telegram-bot>=21.4.0", "prettytable>=3.10.2", "numpy<=1.26.4",
                 "pydantic>=2.8.2"]
dev_packages = ["pytest", "autopep8", "mypy"]
mt5_packages = ["MetaTrader5"]


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="tradie",
    version="1.0.0",
    packages=find_packages(where="app/src"),
    package_dir={"": "app/src"},
    install_requires=base_packages,
    extras_require={
        "dev": dev_packages,
        "mt5": mt5_packages
    },
    description="Trade easily with MT4/MT5",
    author="Adrian Pitonak",
    long_description=read("README.md"),
    long_description_content_type="text/markdown"
)
