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

from __future__ import with_statement

import os
from os.path import join

import multiprocessing
import yaml

from libcloud.compute.types import Provider
from libcloud.compute.types import DeploymentError
from libcloud.compute.providers import get_driver
from libcloud.compute.deployment import MultiStepDeployment
from libcloud.compute.deployment import FileDeployment
from libcloud.compute.deployment import ScriptFileDeployment
from libcloud.compute.deployment import SSHKeyDeployment


KEY_PATH = os.path.expanduser('~/.ssh/id_rsa.pub')

RACKSPACE_USER = os.environ.get('RACKSPACE_USER')
RACKSPACE_APIKEY = os.environ.get('RACKSPACE_APIKEY')

DEFAULT_SIZE = 1024
DEFAULT_IMAGE = "Debian 7"
DEFAULT_REGION = "iad"


def normalize_image_name(image_name):
    """ Convert friendly names to something generic """
    return image_name.replace(' ', '-').lower()


class Deployment(object):
    """ Cloud server deployment """
    def __init__(self, name, image, size, roles):
        self.name = name
        self.image = image
        self.size = size
        self.roles = roles

        with open(KEY_PATH) as ssh_key:
            self.public_key = ssh_key.read()

    def __repr__(self):
        return "<%s>" % self.name

    def deploy(self, conn):
        """ Deploy a cloud server """
        steps = []
        steps.append(SSHKeyDeployment(self.public_key))

        for role in self.roles:
            start = 'roles/%s/files' % role
            for root, _, files in os.walk(start):
                for f in files:
                    source = join(root, f)
                    target = source.replace(start, '', 1)
                    steps.append(FileDeployment(source, target))

            start = 'roles/%s/scripts' % role
            for root, _, files in os.walk(start):
                for f in files:
                    source = join(root, f)
                    steps.append(ScriptFileDeployment(source,
                                                      delete=True))

        try:
            print "Deploying %s" % self.name
            node = conn.deploy_node(
                name=self.name, image=self.image, size=self.size,
                deploy=MultiStepDeployment(steps))
            print node

        except DeploymentError as exc:
            print "Error: %s" % exc
            print dir(exc)
            print exc.error

        except KeyboardInterrupt:
            return


class DeploymentTool(object):
    """ Main deployment tool with multiprocessing built-in """
    def __init__(self, plan_file):
        try:
            with open(plan_file) as plan:
                self.config = yaml.safe_load(plan.read())

        except IndexError:
            raise Exception("You need to specify a deployment plan.")

        except IOError:
            raise Exception("Unable to read specified deployment plan.")

        else:
            self.driver = get_driver(Provider.RACKSPACE)
            self.conn = self.driver(RACKSPACE_USER, RACKSPACE_APIKEY,
                                    region=self.config.get('region',
                                                           DEFAULT_REGION))

            self.sizes = self.conn.list_sizes()
            self.sizes.sort(key=lambda size: size.price)

            self.images = self.conn.list_images()

            self.roles = self.config.get('role', [])
            if type(self.roles) is not list:
                self.roles = [self.roles]

            self.deployments = []

            servers = self.config.get('servers', [{}])
            if type(servers) is not list:
                servers = [servers]

            for server in servers:
                image = None
                for i in self.images:
                    image_name = server.get(
                        'image', self.config.get('image', DEFAULT_IMAGE))
                    image_name = normalize_image_name(image_name)
                    if image_name in normalize_image_name(i.name):
                        image = i
                        break

                size = None
                for s in self.sizes:
                    ram_size = server.get(
                        'size', self.config.get('size', DEFAULT_SIZE))
                    if s.ram == ram_size or s.ram > ram_size:
                        size = s
                        break

                server_roles = server.get('role', [])
                if type(server_roles) is not list:
                    server_roles = [server_roles]
                roles = self.roles + server_roles

                count = server.get('count', self.config.get('count', 1))
                for i in range(count):
                    name = server.get('name', self.config.get('name'))
                    if not name:
                        if len(server_roles):
                            name = server_roles[0]
                        else:
                            continue

                    if '%' in name:
                        name = name % (i + 1)
                    elif count > 1:
                        name = "%s%02d" % (name, i + 1)

                    self.deployments.append(
                        Deployment(name, image, size, roles))

    def deploy(self):
        """ Go ahead and deploy all ready deployments """
        deployments = []
        for depl in self.deployments:
            deployment = multiprocessing.Process(target=depl.deploy,
                                                 args=[self.conn])
            deployment.start()
            deployments.append(deployment)

        try:
            for depl in deployments:
                depl.join()

        except KeyboardInterrupt:
            for depl in deployments:
                depl.terminate()
                depl.join()
