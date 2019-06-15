import re
import subprocess


class TakeoutItem():
    description = None

    def __init__(self, username, hostname, storage):
        self.username = username
        self.hostname = hostname
        self.storage = storage

    def takeout(self):
        raise NotImplementedError()

    def takein(self):
        raise NotImplementedError()

    def is_active(self):
        return True

    def run_command(cmd, input_text=None):
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE,
        )
        out, _ = p.communicate(input_text)

        return [l for l in out.split('\n') if l]

    def run_uberspace(*cmd):
        return run_command(['uberspace'] + list(cmd))


class PathItem(TakeoutItem):
    storage_path = None

    def takeout(self):
        self.storage.store_directory(self.path(), self.storage_path)

    def takein(self):
        self.storage.unstore_directory(self.storage_path, self.path())


class UberspaceVersionMixin():
    uberspace_version = None

    def is_active(self):
        with open('/etc/centos-release') as f:
            text = f.read()
            # looks like "CentOS release 6.10 (Final)"
            centos_release = re.search(r'release ([0-9])+\.', text).groups()[0]

        return int(centos_release) == int(self.uberspace_version)
