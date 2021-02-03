import os
import re

from .base import TakeoutItem
from .base import UberspaceVersionMixin


class U6Mixin(UberspaceVersionMixin):
    uberspace_version = 6


class DomainItem(U6Mixin, TakeoutItem):
    flag = None
    storage_path = None

    def _find_domains(self):
        domains = self.run_command(["uberspace-list-domains", self.flag])
        domains = set(domains) - {
            self.username + "." + self.hostname,
            "*." + self.username + "." + self.hostname,
        }
        return domains

    def takeout(self):
        text = "\n".join(self._find_domains())
        self.storage.store_text(text, self.storage_path)

    def takein(self):
        text = self.storage.unstore_text(self.storage_path)

        for domain in (d for d in text.split("\n") if d):
            self.run_command(["uberspace-add-domain", self.flag, "-d", domain])


class WebDomains(DomainItem):
    description = "Web Domains"
    flag = "-w"
    storage_path = "conf/domains-web"

    def _find_domains(self):
        domains = super()._find_domains()

        try:
            for candidate in os.listdir('/var/www/virtual/' + self.username):
                if not re.search(r'\.[a-z0-9-]{2,}$', candidate):
                    continue

                domains.add(candidate)
        except OSError:
            pass

        return domains


class MailDomains(DomainItem):
    description = "Mail Domains"
    flag = "-m"
    storage_path = "conf/domains-mail"


class ToolVersion(TakeoutItem):
    storage_path = None
    version_regex = None
    software_command = None

    def _clean_version(self, version):
        return version

    def takeout(self):
        output = self.run_command(self.software_command)
        version = re.search(self.version_regex, output).groups()[0]
        version = self._clean_version(version)
        self.storage.store_text(version, self.storage_path)

    def takein(self):
        pass
        # TODO: print warning


class NodeVersion(ToolVersion):
    storage_path = "conf/tool-version/node"
    version_regex = r"^v([0-9]+)"
    software_command = "node --version"


class RubyVersion(ToolVersion):
    storage_path = "conf/tool-version/ruby"
    version_regex = r"^ruby ([0-9]+\.[0-9]+)"
    software_command = "ruby --version"


class PhpVersion(ToolVersion):
    storage_path = "conf/tool-version/php"
    version_regex = r"^PHP ([0-9]+\.[0-9]+)"
    software_command = "php --version"
