import configparser

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


class MySQLPassword(TakeoutItem):
    description = 'MySQL password'

    @property
    def _my_cnf_path(self):
        return '/home/' + self.username + '/.my.cnf'

    def _open_my_cnf(self, section):
        config = configparser.ConfigParser()
        config.read(self._my_cnf_path)
        return config

    def _read_my_cnf_password(self, section):
        return self._open_my_cnf()[section]['password']

    def _write_my_cnf_password(self, section, password):
        config = self._open_my_cnf()
        config[section]['password'] = password

        with open(self._my_cnf_path) as f:
            config.write(f)

    def _set_password(self, suffix):
        password = self.storage.unstore_text('conf/mysql-password-client' + suffix)
        self.run_command(['mysql', '--defaults-group-suffix=' + suffix, '-e', "SET PASSWORD = PASSWORD('" + password + "')"])
        _write_my_cnf_password('client' + suffix, password)

    def takeout(self):
        self.storage.store_text(self._read_mysql_password('client'), 'conf/mysql-password-client')
        self.storage.store_text(self._read_mysql_password('clientreadonly'), 'conf/mysql-password-clientreadonly')

    def takein(self):
        self._set_password('client')
        self._set_password('clientreadonly')
