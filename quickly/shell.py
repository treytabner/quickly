"""
Quickly, quickly deploy and manage cloud servers
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

import sys

from os.path import basename

from quickly.deploy import main as deploy
from quickly.manage import main as manage


def main():
    """ Determine which quickly command to execute """
    try:
        if sys.argv[1] == 'deploy':
            deploy()

        elif sys.argv[1] == 'manage':
            manage()

        else:
            raise Exception("Unknown command")

    except IndexError:
        print "Usage: %s deploy|manage ..." % basename(sys.argv[0])


if __name__ == "__main__":
    main()
