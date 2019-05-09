import re

from .. import utils
from .base import PathItem, TakeoutItem


class TakeoutMarker(TakeoutItem):
    kind = 'text'
    description = 'Takeout Marker (internal)'
    tar_path = '.uberspace_takeout'

    def takeout(self):
        return ''

    def takein(self):
        def noop(data):
            pass

        # just assert existance
        return noop


class Homedir(PathItem):
    kind = 'path'
    description = 'Homedirectory'
    tar_path = 'home/'

    def path(self):
        return '/home/' + self.username


class Www(PathItem):
    kind = 'path'
    description = 'Documentroot'
    tar_path = 'www/'

    def path(self):
        return '/var/www/virtual/' + self.username


class Cronjobs(TakeoutItem):
    kind = 'text'
    description = 'Cronjobs'
    tar_path = 'cronjobs'

    def takeout(self):
        cronjobs = utils.run_command(['crontab', '-l'])
        return '\n'.join(cronjobs) + '\n'

    def takein(self):
        def process(data):
            utils.run_command(['crontab', '-'], input_text=data)

        return process


class UberspaceVersionMixin():
    uberspace_version = None

    def is_active(self):
        with open('/etc/centos-release') as f:
            text = f.read()
            # looks like "CentOS release 6.10 (Final)"
            centos_release = re.search(r'release ([0-9])+\.', text).groups()[0]

        return int(centos_release) == int(self.uberspace_version)
