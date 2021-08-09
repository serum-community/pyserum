"""setuptools module for PySerum."""

from setuptools import find_packages, setup

setup(
    name="pyserum",
    version="0.3.5a1",
    author="serum-community",
    description="""Python client library for interacting with the Project Serum DEX.""",
    install_requires=[
        "construct>=2.10.56, <3.0.0",
        "construct-typing>=0.5.1, <1.0.0",
        "solana>=0.11.3, <1.0.0",
    ],
    python_requires=">=3.7, <4",
    license="MIT",
    package_data={"pyserum": ["py.typed"]},
    packages=find_packages(exclude=("tests", "tests.*")),
    url="https://github.com/serum-community/pyserum",
    zip_safe=False,  # required per mypy
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
