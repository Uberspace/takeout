import re

from .. import utils
from .base import TakeoutItem, UberspaceVersionMixin


class U7Mixin(UberspaceVersionMixin):
    uberspace_version = 7


class DomainItem(U7Mixin, TakeoutItem):
    kind = 'text'
    area = None

    def takeout(self):
        domains = utils.run_uberspace(self.area, 'domain', 'list')
        domains = set(domains) - {
            self.username + '.uber.space',
            self.username + '.' + self.hostname
        }
        return '\n'.join(domains)

    def takein(self):
        def process(data):
            domains = (d for d in data.split('\n') if d)
            for domain in domains:
                utils.run_uberspace(self.area, 'domain', 'add', domain)

        return process


class WebDomains(DomainItem):
    kind = 'text'
    description = 'Web Domains'
    area = 'web'
    tar_path = 'domains-web'


class MailDomains(DomainItem):
    kind = 'text'
    description = 'Mail Domains'
    area = 'mail'
    tar_path = 'domains-mail'


class FlagItem(U7Mixin, TakeoutItem):
    """
    A flag like "is the spamfilter enabled?". It provide a status/enable/disable
    interface via a uberspace sub-command. Provide the uberspace command without
    leading "uberspace" in `cmd` (e.g. ['web', 'log', 'access']).
    """
    kind = 'text'

    def takeout(self):
        out = utils.run_uberspace(*(self.cmd + ['status']))
        if 'enabled' in out:
            status = 'enable'
        else:
            status = 'disable'
        return status

    def takein(self):
        def process(data):
            if data not in ('enable', 'disable'):
                raise Exception(
                    'invalid "uberspace {}" value: {}, expected "enabled" or "disabled".'.format(
                        ' '.join(self.cmd),
                        data,
                    )
                )
            utils.run_uberspace(*(self.cmd + [data]))

        return process


class AccessLogItem(FlagItem):
    description = 'Setting: Access-Log'
    cmd = ['web', 'log', 'access']
    tar_path = 'log-access'


class ApacheErrorLogItem(FlagItem):
    description = 'Setting: Apache-Error-Log'
    cmd = ['web', 'log', 'apache_error']
    tar_path = 'log-apache_error'


class PhpErrorLogItem(FlagItem):
    description = 'Setting: PHP-Error-Log'
    cmd = ['web', 'log', 'php_error']
    tar_path = 'log-php_error'


class SpamfilterLogItem(FlagItem):
    description = 'Setting: Spamfilter'
    cmd = ['mail', 'spamfilter']
    tar_path = 'spamfilter-enabled'


class ToolVersions(U7Mixin, TakeoutItem):
    kind = 'text'
    description = 'Setting: Tool Versions'
    tar_path = 'tool-versions'

    def takeout(self):
        tools = utils.run_uberspace('tools', 'version', 'list')
        dump = ''
        for tool in tools:
            tool = tool.lstrip('- ')
            out = utils.run_uberspace('tools', 'version', 'show', tool)
            version = re.search(r"'([0-9\.]+)'", out[0]).groups()[0]
            dump += tool + '=' + version + '\n'
        return dump

    def takein(self):
        def process(data):
            tools = (l.split('=') for l in data.split('\n') if l)
            for tool, version in tools:
                utils.run_uberspace('tools', 'version', 'use', tool, version)

        return process
