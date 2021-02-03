#!/opt/uberspace/python-venv/bin/python
import socket

import uberspace_takeout.items as items
import uberspace_takeout.storage as storage
from uberspace_takeout.exc import TakeoutError


__version__ = "0.2.0"


class Takeout:
    takeout_menu = [
        items.common.TakeoutMarker,
        items.common.Homedir,
        items.common.Www,
        items.common.Cronjobs,
        items.common.MySQLPassword,
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

    def __init__(self, hostname=None):
        if not hostname:
            hostname = socket.getfqdn()

        self.hostname = hostname
        self.errors = {}

    def get_items(self, username, storage):
        for item in self.takeout_menu:
            instance = item(username, self.hostname, storage)
            if instance.is_active():
                yield instance

    def takein(self, tar_path, username, skipped_items=None):
        if skipped_items is None:
            skipped_items = []
        with storage.TarStorage(tar_path, "takein") as stor:
            for item in self.get_items(username, stor):
                if item.__class__.__name__ in skipped_items:
                    print("skip: " + item.description)
                    continue

                print("takein: " + item.description)
                try:
                    item.takein()
                except TakeoutError as exc:
                    self.errors[item.__class__.__name__] = exc.args

    def takeout(self, tar_path, username, skipped_items=None):
        if skipped_items is None:
            skipped_items = []
        with storage.TarStorage(tar_path, "takeout") as stor:
            for item in self.get_items(username, stor):
                if item.__class__.__name__ in skipped_items:
                    print("skip: " + item.description)
                    continue

                print("takeout: " + item.description)
                try:
                    item.takeout()
                except TakeoutError as exc:
                    self.errors[item.__class__.__name__] = exc.args
