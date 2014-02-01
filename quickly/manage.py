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

import multiprocessing
import os
import paramiko
import sys
import yaml

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from quickly.deploy import DeploymentTool


KEY_PATH = os.path.expanduser('~/.ssh/id_rsa.pub')

RACKSPACE_USER = os.environ.get('RACKSPACE_USER')
RACKSPACE_APIKEY = os.environ.get('RACKSPACE_APIKEY')

DEFAULT_SIZE = 1024
DEFAULT_IMAGE = "Debian 7"
DEFAULT_REGION = "iad"


class ManagementTool(object):
    """ Management tool to run commands on desired servers """
    def __init__(self):
        try:
            with open(sys.argv[2]) as plan:
                self.config = yaml.safe_load(plan.read())

            self.deployment = DeploymentTool()

        except IndexError:
            raise Exception("You need to specify a deployment plan.")

        except IOError:
            raise Exception("Unable to read specified deployment plan.")

        except Exception as exc:
            print exc

        else:
            self.driver = get_driver(Provider.RACKSPACE)
            self.conn = self.driver(RACKSPACE_USER, RACKSPACE_APIKEY,
                                    region=self.config.get('region',
                                                           DEFAULT_REGION))
            self.servers = []
            self.nodes = self.conn.list_nodes()
            for depl in self.deployment.deployments:
                for node in self.nodes:
                    if depl.name == node.name:
                        self.servers.append(node)

    def execute(self):
        """ Execute specified commands on target servers """
        cmds = []

        command = ' '.join(sys.argv[3:])
        for server in self.servers:
            for ip in server.public_ips:
                if '.' in ip:
                    cmd = multiprocessing.Process(target=self.cmd,
                                                  args=[server.name,
                                                        ip, command])
                    cmd.start()
                    cmds.append(cmd)

        try:
            for cmd in cmds:
                cmd.join()

        except KeyboardInterrupt:
            for cmd in cmds:
                cmd.terminate()
                cmd.join()

    def cmd(self, name, ip, command):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username='root', key_filename=KEY_PATH)
        stdin, stdout, stderr = ssh.exec_command(command)
        for line in stdout:
            print "%s: %s" % (name, line.strip('\n'))


def main():
    """ Remote management of cloud servers """
    manage = ManagementTool()
    manage.execute()


if __name__ == "__main__":
    main()
