"""Build script for Race Card."""

import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="racecard-krys",
    version="0.1.0",
    description="Race Card: An implementation of the game card game Mille Bornes",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/justkrys/racecard",
    author="Krys Lawrence",
    author_email="krys AT krys DOT ca",
    licence="AGPL-3.0-or-later",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: "
        + "GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Topic :: Games/Entertainment",
    ],
    keywords="game card cli mille bornes",
    project_urls={
        # 'Documentation': '',
        # 'Funding': '',
        # 'Say Thanks!': '',
        "Source": "https://github.com/justkrys/racecard",
        # 'Tracker': '',
    },
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    entry_points={"console_scripts": ["racecard = racecard.app.simplecli:main"]},
)
