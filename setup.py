"""Pioneer AVR API (async) setup.py."""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aiopioneer",
    version="0.1.1",
    author="Crowbar Z",
    author_email="crowbarz@outlook.com",
    description="Asyncio Python library for controlling a Pioneer AVR via its API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/crowbarz/aiopioneer.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Topic :: Home Automation",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
)
