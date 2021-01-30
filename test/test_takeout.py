import os
import shutil
from pathlib import Path

import pytest
from pyfakefs.fake_filesystem_unittest import Pause

from uberspace_takeout import Takeout


def prefix_root(prefix):
    return Path(__file__).parent / "uberspaces" / prefix


def populate_root(fs, prefix):
    outside_root = prefix_root(prefix)

    with Pause(fs):
        for dir in os.listdir(outside_root):
            if not os.path.isdir(outside_root / dir):
                raise NotImplementedError(
                    "currently only directories are supported at root level"
                )
            if dir == "commands":
                continue

            try:
                fs.remove_object("/" + dir)
            except FileNotFoundError:
                pass

            fs.add_real_directory(
                outside_root / dir,
                lazy_read=False,
                read_only=False,
                target_path="/" + dir,
            )


def clean_root(skip_dirs=["tmp", "etc"]):
    for path in os.listdir("/"):
        if path not in skip_dirs:
            shutil.rmtree("/" + path)

    Path("/home").mkdir()
    Path("/var/www/virtual").mkdir(parents=True)

    assert not os.listdir("/home")
    assert not os.listdir("/var/www/virtual")


@pytest.fixture
def mock_run_command(fs, mocker):
    class Commands:
        def __init__(self, *args, **kwargs):
            self.called = {}
            self.commands = {}

            self._mock()

        def clear(self):
            self.called.clear()
            self.commands.clear()

        def add_prefix_commands(self, prefix):
            commands = prefix_root(prefix) / "commands"

            with Pause(fs):
                for cmd in os.listdir(commands):
                    with open(commands / cmd) as f:
                        self.add_command(cmd, f.read())

        def add_command(self, command, output=""):
            if command in self.commands:
                raise Exception("Command '{}' is already defined.".format(command))
            if isinstance(command, list):
                command = " ".join(command)

            self.commands[command] = output

        def assert_called(self, command, input_text=None):
            if isinstance(command, list):
                command = " ".join(command)

            assert command in self.called

            if input_text:
                assert self.called[command] == input_text

            del self.called[command]

        def assert_no_unexpected(self):
            assert not self.called, "unexpected commands executed"

        def _mock(self):
            def _run_command(_, cmd, input_text=None, *args, **kwargs):
                cmd_str = " ".join(cmd)
                self.called[cmd_str] = input_text

                if cmd_str in self.commands:
                    output = self.commands[cmd_str]
                    return [l.rstrip() for l in output.split("\n") if l.rstrip()]
                else:
                    return []

            mocker.patch(
                "uberspace_takeout.items.base.TakeoutItem.run_command", _run_command
            )

    return Commands()


def content(path):
    with open(path) as f:
        return f.read()


def assert_in_file(path, text):
    assert text in content(path)


def assert_files_equal(path1, path2):
    assert content(path1) == content(path2)


def assert_file_unchanged(path, fs, prefix):
    with Pause(fs):
        original = content(prefix_root(prefix) / path.lstrip("/"))

    assert original == content(path)


def test_takeout_u6_to_u6(fs, mock_run_command):
    populate_root(fs, "u6/isabell")
    mock_run_command.add_prefix_commands("u6/isabell")

    takeout = Takeout(hostname="andromeda.uberspace.de")

    takeout.takeout("/tmp/test.tar.gz", "isabell")

    clean_root()

    mock_run_command.clear()

    takeout.takein("/tmp/test.tar.gz", "isabell")

    mock_run_command.assert_called(
        "mysql --defaults-group-suffix= -e SET PASSWORD = PASSWORD('Lei4e%ngekäe3iÖt4Ies')"
    )
    assert_in_file("/home/isabell/.my.cnf", "Lei4e%ngekäe3iÖt4Ies")

    mock_run_command.assert_called("uberspace-add-domain -w -d *.example.com")
    mock_run_command.assert_called("uberspace-add-domain -w -d example.com")
    mock_run_command.assert_called("uberspace-add-domain -w -d foo.example.com")
    mock_run_command.assert_called("uberspace-add-domain -m -d mail.example.com")

    mock_run_command.assert_called("crontab -", "@daily echo good morning\n")

    mock_run_command.assert_no_unexpected()

    assert_file_unchanged("/var/www/virtual/isabell/html/index.html", fs, "u6/isabell")
    assert_file_unchanged(
        "/var/www/virtual/isabell/html/blog/index.html", fs, "u6/isabell"
    )
    assert os.path.islink("/home/isabell/html")
    assert_file_unchanged("/home/isabell/html/index.html", fs, "u6/isabell")
    assert_file_unchanged("/home/isabell/Maildir/cur/mail-888", fs, "u6/isabell")


def test_takeout_u6_to_u7(fs, mock_run_command):
    populate_root(fs, "u6/isabell")
    mock_run_command.add_prefix_commands("u6/isabell")

    takeout = Takeout(hostname="andromeda.uberspace.de")

    takeout.takeout("/tmp/test.tar.gz", "isabell")

    clean_root()
    mock_run_command.clear()
    populate_root(fs, "u7/empty")

    takeout.takein("/tmp/test.tar.gz", "isabell")

    mock_run_command.assert_called(
        "mysql --defaults-group-suffix= -e SET PASSWORD = PASSWORD('Lei4e%ngekäe3iÖt4Ies')"
    )
    assert_in_file("/home/isabell/.my.cnf", "Lei4e%ngekäe3iÖt4Ies")

    mock_run_command.assert_called("uberspace web domain add example.com")
    mock_run_command.assert_called("uberspace web domain add foo.example.com")
    mock_run_command.assert_called("uberspace web domain add ep.isabell.uber.space")
    mock_run_command.assert_called("uberspace mail domain add mail.example.com")

    mock_run_command.assert_called("crontab -", "@daily echo good morning\n")

    mock_run_command.assert_no_unexpected()

    assert_file_unchanged("/var/www/virtual/isabell/html/index.html", fs, "u6/isabell")
    assert_file_unchanged(
        "/var/www/virtual/isabell/html/blog/index.html", fs, "u6/isabell"
    )
    assert os.path.islink("/home/isabell/html")
    assert_file_unchanged("/home/isabell/html/index.html", fs, "u6/isabell")
    assert_file_unchanged("/home/isabell/Maildir/cur/mail-888", fs, "u6/isabell")
