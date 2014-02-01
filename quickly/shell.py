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

import argparse
import pkg_resources

from prettytable import PrettyTable

from quickly.deploy import DeploymentTool
from quickly.manage import ManagementTool


def main():
    """ Determine which quickly command to execute """
    version = pkg_resources.require('quickly')[0].version
    parser = argparse.ArgumentParser(
        version=version, description="Quickly deploy and manage cloud servers")
    parser.add_argument(
        "-n", "--no-action", dest='action', action='store_false',
        help="Perform no actions other than listing details")

    subparsers = parser.add_subparsers(dest='mode')

    deploy_parser = subparsers.add_parser(
        'deploy', help="Deploy and configure one or more servers in parallel")
    deploy_parser.add_argument(
        'plan', help="File containing deployment plan in YAML format")

    manage_parser = subparsers.add_parser(
        'manage', help="Manage one or more servers by executing commands")
    manage_parser.add_argument(
        'plan', help="Plan that determines servers to action against")
    manage_parser.add_argument('command', nargs=argparse.REMAINDER,
                               help="Command to execute on specified servers")

    args = parser.parse_args()

    if args.mode == 'deploy':
        try:
            deploy = DeploymentTool(args.plan)
        except Exception as exc:
            print("Shell exception: %s" % exc)
        else:
            todo = PrettyTable(["Server Name", "Roles", "Image", "Size"])
            todo.align = 'l'

            for d in deploy.deployments:
                todo.add_row([d.name, ', '.join(d.roles),
                              d.image.name, d.size.name])
            print(todo)

            if args.action:
                deploy.deploy()

    elif args.mode == 'manage':
        manage = ManagementTool(args.plan)

        todo = PrettyTable(["Server Name", "Access IP", "Device ID"])
        todo.align = 'l'

        for s in manage.servers:
            todo.add_row([s.name, s.extra.get('access_ip'), s.id])
        print(todo)

        if args.action:
            manage.execute(args.command)


if __name__ == "__main__":
    main()
