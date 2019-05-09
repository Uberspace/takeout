import re


class TakeoutItem():
    kind = None
    tar_path = None
    description = None

    def __init__(self, username, hostname):
        self.username = username
        self.hostname = hostname

    def takeout(self):
        raise NotImplementedError()

    def takein(self):
        raise NotImplementedError()

    def is_active(self):
        return True


class PathItem(TakeoutItem):
    kind = 'path'

    def takeout(self):
        return self.path()

    def takein(self):
        return self.path()


class UberspaceVersionMixin():
    uberspace_version = None

    def is_active(self):
        with open('/etc/centos-release') as f:
            text = f.read()
            # looks like "CentOS release 6.10 (Final)"
            centos_release = re.search(r'release ([0-9])+\.', text).groups()[0]

        return int(centos_release) == int(self.uberspace_version)
