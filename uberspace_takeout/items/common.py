from .. import utils
from .base import PathItem, TakeoutItem


class TakeoutMarker(TakeoutItem):
    description = 'Takeout Marker (internal)'

    def takeout(self):
        self.storage.store_text('uberspace_takeout', '.uberspace_takeout')

    def takein(self):
        content = self.storage.unstore_text('.uberspace_takeout')

        if content != 'uberspace_takeout':
            raise Exception('input is not a takeout.')


class Homedir(PathItem):
    description = 'Homedirectory'
    storage_path = 'home/'

    def path(self):
        return '/home/' + self.username


class Www(PathItem):
    description = 'Documentroot'
    storage_path = 'www/'

    def path(self):
        return '/var/www/virtual/' + self.username


class Cronjobs(TakeoutItem):
    description = 'Cronjobs'

    def takeout(self):
        cronjobs = utils.run_command(['crontab', '-l'])
        text = '\n'.join(cronjobs) + '\n'
        self.storage.store_text(text, 'cronjobs')

    def takein(self):
        text = self.storage.unstore_text('cronjobs')
        utils.run_command(['crontab', '-'], input_text=text)
