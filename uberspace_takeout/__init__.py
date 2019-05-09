#!/opt/uberspace/python-venv/bin/python

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import datetime
import socket
import tarfile

import uberspace_takeout.items as items


class TakeoutU7:
    takeout_menu = [
        items.common.TakeoutMarker,
        items.common.Homedir,
        items.common.Www,
        items.common.Cronjobs,
        items.u7.WebDomains,
        items.u7.MailDomains,
        items.u7.AccessLogItem,
        items.u7.ApacheErrorLogItem,
        items.u7.PhpErrorLogItem,
        items.u7.SpamfilterLogItem,
        items.u7.ToolVersions,
    ]

    def filter_members(self, tar, prefix, strip_prefix=False):
        for m in tar.getmembers():
            name = m.name

            if not name or '..' in name or name.startswith('/') or name.startswith('./'):
                raise Exception(
                    'illegal member name in tar file: ' + name
                )

            if m.type not in (tarfile.REGTYPE, tarfile.SYMTYPE, tarfile.DIRTYPE):
                raise Exception(
                    'illegal member tpye in tar file: {} (must be file, dir, or symlink; is {}'.format(name, m.type)
                )

            if m.name.startswith(prefix):
                if strip_prefix:
                    m.name = m.name[len(prefix):]
                yield m

    def get_items(self, username):
        for item in self.takeout_menu:
            yield item(username, socket.getfqdn())

    def takein(self, tar_path, username):
        with tarfile.open(tar_path, 'r:bz2') as tar:
            for item in self.get_items(username):
                print('takein: ' + item.description)
                data = item.takein()

                if item.kind == 'path':
                    path = data
                    tar.extractall(path, self.filter_members(tar, item.tar_path, strip_prefix=True))
                elif item.kind == 'text':
                    process = data
                    process(tar.extractfile(item.tar_path).read())

    def takeout(self, username):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        tar_path = 'takeout_{}_{}.tar.bz2'.format(username, timestamp)

        with tarfile.open(tar_path, 'w:bz2') as tar:
            for item in self.get_items(username):
                print('takeout: ' + item.description)
                data = item.takeout()

                if item.kind == 'path':
                    tar.add(data, item.tar_path)
                elif item.kind == 'text':
                    data = StringIO(data)
                    info = tarfile.TarInfo(item.tar_path)
                    info.size = data.len
                    info.mtime = int(datetime.datetime.now().strftime("%s"))
                    tar.addfile(info, data)

        return tar_path
