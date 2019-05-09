from .. import utils
from .base import TakeoutItem, UberspaceVersionMixin


class U6Mixin(UberspaceVersionMixin):
    uberspace_version = 6


class DomainItem(TakeoutItem, U6Mixin):
    kind = 'text'
    flag = None

    def takeout(self):
        domains = utils.run_command(['uberspace-list-domains', self.flag])
        domains = set(domains) - {
            self.username + '.' + self.hostname,
            '*.' + self.username + '.' + self.hostname,
        }
        return '\n'.join(domains)

    def takein(self):
        def process(data):
            domains = (d for d in data.split('\n') if d)
            for domain in domains:
                utils.run_command(['uberspace-add-domain', self.flag, '-d', domain])

        return process


class WebDomains(DomainItem):
    kind = 'text'
    description = 'Web Domains'
    flag = '-w'
    tar_path = 'domains-web'


class MailDomains(DomainItem):
    kind = 'text'
    description = 'Mail Domains'
    flag = '-m'
    tar_path = 'domains-mail'
    # TODO: save namespaces?
