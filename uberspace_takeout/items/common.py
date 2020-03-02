import configparser
import pathlib

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
    def mycnf_path(self):
        return pathlib.Path("/home", self.username, ".my.cnf")

    @property
    def mycnf_parser(self):
        cp = configparser.ConfigParser(interpolation=None)
        cp.read(self.mycnf_path, encoding="utf-8")
        return cp

    def _read_mycnf_password(self, section):
        password = self.mycnf_parser[section]["password"]
        # remove possible inline comment (` # …`)
        password = password.partition("#")[0].strip()
        # remove possible quotes
        password = password.strip('"')
        return password

    def _write_mycnf_password(self, section, password):
        cp = self.mycnf_parser
        cp[section]["password"] = password
        with open(self.mycnf_path, "w") as f:
            cp.write(f)

    def _check_password(self, password):
        if len(password) < 16:
            msg = (
                "Your current MySQL password does not satisfy our policy requirements:"
                " it is shorter than 16 characters."
                " Please set a sufficiently long one - as described under"
                " https://wiki.uberspace.de/database:mysql#passwort_aendern"
                " - or run this script with '--skip-item MySQLPassword'."
            )
            raise TakeoutError(msg)

    def _get_password(self, suffix):
        password = self._read_mycnf_password(f"client{suffix}")
        self._check_password(password)
        self.storage.store_text(password, f"conf/mysql-password-client{suffix}")

    def _set_password(self, suffix):
        password = self.storage.unstore_text(f"conf/mysql-password-client{suffix}")
        self._check_password(password)
        self.run_command(
            [
                "mysql",
                f"--defaults-group-suffix={suffix}",
                "-e",
                f"SET PASSWORD = PASSWORD('{password}')",
            ]
        )
        self._write_mycnf_password(f"client{suffix}", password)

    def takeout(self):
        self._get_password("")

    def takein(self):
        self._set_password("")
