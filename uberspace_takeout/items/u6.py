from .base import TakeoutItem, UberspaceVersionMixin


class U6Mixin(UberspaceVersionMixin):
    uberspace_version = 6


class DomainItem(U6Mixin, TakeoutItem):
    flag = None
    storage_path = None

    def takeout(self):
        domains = utils.run_command(['uberspace-list-domains', self.flag])
        domains = set(domains) - {
            self.username + '.' + self.hostname,
            '*.' + self.username + '.' + self.hostname,
        }
        text = '\n'.join(domains)
        self.storage.store_text(text, self.storage_path)

    def takein(self):
        text = self.storage.unstore_text(self.storage_path)

        for domain in (d for d in text.split('\n') if d):
            utils.run_command(['uberspace-add-domain', self.flag, '-d', domain])


class WebDomains(DomainItem):
    description = 'Web Domains'
    flag = '-w'
    storage_path = 'domains-web'


class MailDomains(DomainItem):
    description = 'Mail Domains'
    flag = '-m'
    storage_path = 'domains-mail'
