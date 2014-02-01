"""
Quickly, quickly deploy and configure cloud servers
Copyright (C) 2014 Trey Tabner <trey@tabner.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from setuptools import setup

setup(
    name="quickly",
    version="0.1",
    author="Trey Tabner",
    author_email="trey@tabner.com",
    description=("Quickly deploy and configure cloud servers"),
    license="GPL3",
    url="https://github.com/treytabner/quickly",
    packages=['quickly'],
    entry_points={
        'console_scripts': [
            'quickly=quickly.shell:main',
        ],
    }
)
