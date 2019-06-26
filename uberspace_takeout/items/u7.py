import re

from .base import TakeoutItem, UberspaceVersionMixin


class U7Mixin(UberspaceVersionMixin):
    uberspace_version = 7


class DomainItem(U7Mixin, TakeoutItem):
    area = None

    def takeout(self):
        domains = utils.run_uberspace(self.area, 'domain', 'list')
        domains = set(domains) - {
            self.username + '.uber.space',
            self.username + '.' + self.hostname
        }
        self.storage.store_text('\n'.join(domains), self.storage_path)

    def takein(self):
        text = self.storage.unstore_text(self.storage_path)
        for domain in (d for d in text.split('\n') if d):
            utils.run_uberspace(self.area, 'domain', 'add', domain)


class WebDomains(DomainItem):
    description = 'Web Domains'
    area = 'web'
    storage_path = 'conf/domains-web'


class MailDomains(DomainItem):
    description = 'Mail Domains'
    area = 'mail'
    storage_path = 'conf/domains-mail'


class FlagItem(U7Mixin, TakeoutItem):
    """
    A flag like "is the spamfilter enabled?". It provide a status/enable/disable
    interface via a uberspace sub-command. Provide the uberspace command without
    leading "uberspace" in `cmd` (e.g. ['web', 'log', 'access']).
    """

    def takeout(self):
        out = utils.run_uberspace(*(self.cmd + ['status']))
        if 'enabled' in out:
            status = 'enable'
        else:
            status = 'disable'

        self.storage.store_text(status, self.storage_path)

    def takein(self):
        data = self.storage.unstore_text(self.storage_path)

        if data not in ('enable', 'disable'):
            raise Exception(
                'invalid "uberspace {}" value: {}, expected "enabled" or "disabled".'.format(
                    ' '.join(self.cmd),
                    data,
                )
            )

        utils.run_uberspace(*(self.cmd + [data]))


class AccessLogItem(FlagItem):
    description = 'Setting: Access-Log'
    cmd = ['web', 'log', 'access']
    storage_path = 'conf/log-access'


class ApacheErrorLogItem(FlagItem):
    description = 'Setting: Apache-Error-Log'
    cmd = ['web', 'log', 'apache_error']
    storage_path = 'conf/log-apache_error'


class PhpErrorLogItem(FlagItem):
    description = 'Setting: PHP-Error-Log'
    cmd = ['web', 'log', 'php_error']
    storage_path = 'conf/log-php_error'


class SpamfilterLogItem(FlagItem):
    description = 'Setting: Spamfilter'
    cmd = ['mail', 'spamfilter']
    storage_path = 'conf/spamfilter-enabled'


class ToolVersions(U7Mixin, TakeoutItem):
    description = 'Setting: Tool Versions'

    def takeout(self):
        tools = utils.run_uberspace('tools', 'version', 'list')
        dump = ''
        for tool in tools:
            tool = tool.lstrip('- ')
            out = utils.run_uberspace('tools', 'version', 'show', tool)
            version = re.search(r"'([0-9\.]+)'", out[0]).groups()[0]
            dump += tool + '=' + version + '\n'
        self.storage.store_text(dump, 'conf/tool-versions')

    def takein(self):
        text = self.storage.unstore_text('conf/tool-versions')
        for tool, version in (l.split('=') for l in text.split('\n') if l):
            utils.run_uberspace('tools', 'version', 'use', tool, version)
