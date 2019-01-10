"""Setup file for building/installing flake8-black."""

from __future__ import with_statement

from setuptools import setup


def get_version(fname="flake8_black.py"):
    """Parse our source code to get the current version number."""
    with open(fname) as f:
        for line in f:
            if line.startswith("__version__"):
                return eval(line.split("=")[-1])


setup(
    name="flake8-black",
    version=get_version(),
    description="flake8 plugin to call black as a code style validator",
    long_description=open("README.rst").read(),
    license="MIT",
    author="Peter J. A. Cock",
    author_email="p.j.a.cock@googlemail.com",
    url="https://github.com/peterjc/flake8-black",
    classifiers=[
        "Intended Audience :: Developers",
        "Framework :: Flake8",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    keywords="PEP8",
    py_modules=["flake8_black"],
    install_requires=["flake8 >= 3.0.0", "black"],
    entry_points={"flake8.extension": ["BLK = flake8_black:BlackStyleChecker"]},
)
