import configparser

from .base import PathItem
from .base import TakeoutItem
from uberspace_takeout.exc import TakeoutError


class TakeoutMarker(TakeoutItem):
    description = "Takeout Marker (internal)"

    def takeout(self):
        self.storage.store_text("uberspace_takeout", ".uberspace_takeout")

    def takein(self):
        content = self.storage.unstore_text(".uberspace_takeout")

        if content != "uberspace_takeout":
            raise Exception("input is not a takeout.")


class Homedir(PathItem):
    description = "Homedirectory"
    storage_path = "home/"

    def path(self):
        return "/home/" + self.username


class Www(PathItem):
    description = "Documentroot"
    storage_path = "www/"

    def path(self):
        return "/var/www/virtual/" + self.username


class Cronjobs(TakeoutItem):
    description = "Cronjobs"

    def takeout(self):
        cronjobs = self.run_command(["crontab", "-l"])

        if len(cronjobs) == 1 and cronjobs[0].startswith("no crontab for"):
            text = ""
        else:
            text = "\n".join(cronjobs) + "\n"

        self.storage.store_text(text, "conf/cronjobs")

    def takein(self):
        text = self.storage.unstore_text("conf/cronjobs")
        self.run_command(["crontab", "-"], input_text=text)


class MySQLPassword(TakeoutItem):
    description = "MySQL password"

    @property
    def _my_cnf_path(self):
        return "/home/" + self.username + "/.my.cnf"

    def _open_my_cnf(self, section):
        config = configparser.ConfigParser(interpolation=None)
        config.read(self._my_cnf_path, encoding="utf-8")
        return config

    def _read_my_cnf_password(self, section):
        raw_pw = self._open_my_cnf(section)[section]["password"]
        return raw_pw.partition("#")[0].strip().strip('"')

    def _check_password(self, password):
        if len(password) < 12:
            msg = (
                "Your current MySQL password does not satisfy our policy requirements:"
                " it is shorter than 12 characters."
                " Please set a sufficiently long one - as described under"
                " https://wiki.uberspace.de/database:mysql#passwort_aendern"
                " - or run this script with '--skip-item MySQLPassword'."
            )
            raise TakeoutError(msg)

    def _write_my_cnf_password(self, section, password):
        config = self._open_my_cnf(section)
        config[section]["password"] = password

        with open(self._my_cnf_path, "w") as f:
            config.write(f)

    def _set_password(self, suffix):
        password = self.storage.unstore_text("conf/mysql-password-client" + suffix)
        self.run_command(
            [
                "mysql",
                "--defaults-group-suffix=" + suffix,
                "-e",
                "SET PASSWORD = PASSWORD('" + password + "')",
            ]
        )
        self._write_my_cnf_password("client" + suffix, password)

    def takeout(self):
        password = self._read_my_cnf_password("client")
        self.storage.store_text(password, "conf/mysql-password-client")
        self._check_password(password)

    def takein(self):
        self._set_password("")
