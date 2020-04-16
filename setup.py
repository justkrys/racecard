#    Race Card - An implementation of the card game Mille Bornes
#    Copyright (C) 2020  Krys Lawrence <krys AT krys DOT ca>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Build script for Race Card."""


import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="racecard",
    version="0.0.1",
    description="Race Card: An implementation of the game card game Mille Bornes",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/justkrys/racecard",
    author="Krys Lawrence",
    author_email="code@krys.ca",
    license="GNU AGPLv3+",
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
    entry_points={
        "console_scripts": [
            "racecard = racecard.app.simplecli:main",
            "racecard-rest = racecard.server.rest:main [REST]",
        ]
    },
    extras_require={
        "REST": [
            "connexion[swagger-ui]",
            "Flask",
            "python-dotenv",
            "jsonschema[format]",
        ]
    },
)
