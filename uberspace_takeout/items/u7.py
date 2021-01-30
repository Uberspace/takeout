import re

from .base import TakeoutItem
from .base import UberspaceVersionMixin


class U7Mixin(UberspaceVersionMixin):
    uberspace_version = 7


def convert_legacy_domain(domain):
    """
    convert legacy domains to new .uber.space ones, e.g.

         luto.cygnus.uberspace.de   =>      luto.uber.space
      ep.luto.cygnus.uberspace.de   =>   ep.luto.uber.space
    """

    if domain.endswith('.uberspace.de'):
        # strip suffix off a full domain, e.g.
        #   luto.cygnus.uberspace.de  =>  luto
        domain = re.sub(r'\.[a-z]+\.uberspace\.de$', '', domain) + '.uber.space'

    return domain

class DomainItem(U7Mixin, TakeoutItem):
    area = None

    def takeout(self):
        domains = self.run_uberspace(self.area, "domain", "list")
        domains = set(domains) - {
            self.username + ".uber.space",
            self.username + "." + self.hostname,
        }
        self.storage.store_text("\n".join(domains), self.storage_path)

    def takein(self):
        text = self.storage.unstore_text(self.storage_path)
        for domain in (d for d in text.split("\n") if d):
            if domain.startswith("*."):
                print("cannot add wildcard domain on: " + domain)
                continue
            if domain.endswith('.uberspace.de'):
                print("user.host.uberspace.de domains are not supported, rewriting to .uber.space")
                domain = convert_legacy_domain(domain)
            self.run_uberspace(self.area, "domain", "add", domain)


class WebDomains(DomainItem):
    description = "Web Domains"
    area = "web"
    storage_path = "conf/domains-web"


class MailDomains(DomainItem):
    description = "Mail Domains"
    area = "mail"
    storage_path = "conf/domains-mail"


class FlagItem(U7Mixin, TakeoutItem):
    """
    A flag like "is the spamfilter enabled?". It provide a status/enable/disable
    interface via a uberspace sub-command. Provide the uberspace command without
    leading "uberspace" in `cmd` (e.g. ['web', 'log', 'access']).
    """

    def takeout(self):
        out = self.run_uberspace(*(self.cmd + ["status"]))
        if "enabled" in out:
            status = "enable"
        else:
            status = "disable"

        self.storage.store_text(status, self.storage_path)

    def takein(self):
        try:
            data = self.storage.unstore_text(self.storage_path)
        except FileNotFoundError:
            return

        if data not in ("enable", "disable"):
            raise Exception(
                'invalid "uberspace {}" value: {}, expected "enabled" or "disabled".'.format(
                    " ".join(self.cmd), data,
                )
            )

        self.run_uberspace(*(self.cmd + [data]))


class AccessLogItem(FlagItem):
    description = "Setting: Access-Log"
    cmd = ["web", "log", "access"]
    storage_path = "conf/log-access"


class ApacheErrorLogItem(FlagItem):
    description = "Setting: Apache-Error-Log"
    cmd = ["web", "log", "apache_error"]
    storage_path = "conf/log-apache_error"


class PhpErrorLogItem(FlagItem):
    description = "Setting: PHP-Error-Log"
    cmd = ["web", "log", "php_error"]
    storage_path = "conf/log-php_error"


class SpamfilterLogItem(FlagItem):
    description = "Setting: Spamfilter"
    cmd = ["mail", "spamfilter"]
    storage_path = "conf/spamfilter-enabled"


class ToolVersions(U7Mixin, TakeoutItem):
    description = "Setting: Tool Versions"

    def takeout(self):
        tools = self.run_uberspace("tools", "version", "list")

        for tool in tools:
            tool = tool.lstrip("- ")
            out = self.run_uberspace("tools", "version", "show", tool)
            version = re.search(r"'([0-9\.]+)'", out[0]).groups()[0]
            self.storage.store_text(version, "conf/tool-version/" + tool)

    def takein(self):
        try:
            tools = self.storage.list_files("conf/tool-versions")
        except FileNotFoundError:
            return

        for tool in tools:
            version = self.storage.unstore_text("conf/tool-versions/" + tool)
            self.run_uberspace("tools", "version", "use", tool, version)
