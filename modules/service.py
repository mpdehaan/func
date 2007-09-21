#!/usr/bin/python

## func
##
## Copyright 2007, Red Hat, Inc
## Michael DeHaan <mdehaan@redhat.com>
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##
##


from codes import *
from modules import func_module

import subprocess
import os

class Service(func_module.FuncModule):

    def __init__(self):
        self.methods = {
            "service_start"   : self.start,
            "service_stop"    : self.stop,
            "service_restart" : self.restart,
            "service_reload"  : self.reload,
            "service_status"  : self.status
        }
        func_module.FuncModule.__init__(self)

    def __command(self, service_name, command):

        filename = os.path.join("/etc/rc.d/init.d/",service_name)
        if os.path.exists(filename):
            return subprocess.call(["/sbin/service", service_name, command])
        else:
            raise FuncException("Service not installed: %s" % service_name)

    def start(self, service_name):
        return self.__command(service_name, "start")

    def stop(self, service_name):
        return self.__command(service_name, "start")

    def restart(self, service_name):
        return self.__command(service_name, "restart")

    def reload(self, service_name):
        return self.__command(service_name, "reload")

    def status(self, service_name):
        return self.__command(service_name, "status")

methods = Service()
register_rpc = methods.register_rpc
