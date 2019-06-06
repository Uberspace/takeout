#!/opt/uberspace/python-venv/bin/python

import socket

import uberspace_takeout.items as items
import uberspace_takeout.storage as storage


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
        items.u6.WebDomains,
        items.u6.MailDomains,
    ]

    def get_items(self, username, storage):
        for item in self.takeout_menu:
            instance = item(username, socket.getfqdn(), storage)
            if instance.is_active():
                yield instance

    def takein(self, tar_path, username):
        with storage.TarStorage(tar_path) as stor:
            for item in self.get_items(username, stor):
                print('takein: ' + item.description)
                item.takein()

    def takeout(self, tar_path, username):
        with storage.TarStorage(tar_path) as stor:
            for item in self.get_items(username, stor):
                print('takeout: ' + item.description)
                item.takeout()
