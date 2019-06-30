import configparser
import os
import shutil
from pathlib import Path

import pytest
from pyfakefs.fake_filesystem_unittest import Pause

from uberspace_takeout import Takeout


def prefix_root(prefix):
    return Path(__file__).parent / 'uberspaces' / prefix


def current_prefix(fs):
    return fs.get_object('/last_prefix').contents


def current_prefix_root(fs):
    return prefix_root(current_prefix(fs))


def populate_root(fs, prefix):
    outside_root = prefix_root(prefix)

    with Pause(fs):
        for dir in os.listdir(outside_root):
            if not os.path.isdir(outside_root / dir):
                raise NotImplementedError("currently only directories are supported at root level")
            if dir == 'commands':
                continue

            try:
                fs.remove_object('/' + dir)
            except FileNotFoundError:
                pass

            fs.add_real_directory(outside_root / dir, lazy_read=False, read_only=False, target_path='/' + dir)

        try:
            fs.remove_object('/last_prefix')
        except FileNotFoundError:
            pass
        fs.create_file('/last_prefix', contents=prefix)


def clean_root(skip_dirs=['tmp', 'etc', 'last_prefix']):
    for path in os.listdir('/'):
        if path not in skip_dirs:
            shutil.rmtree('/' + path)

    Path('/home').mkdir()
    Path('/var/www/virtual').mkdir(parents=True)

    assert not os.listdir('/home')
    assert not os.listdir('/var/www/virtual')


@pytest.fixture
def mock_run_command(fs, mocker):
    called = {}

    def run_command(self, cmd, input_text=None, *args, **kwargs):
        cmd_str = " ".join(cmd)
        commands = current_prefix_root(fs) / 'commands'

        with Pause(fs):
            try:
                with open(commands / cmd_str, 'r') as f:
                    output = [l.rstrip() for l in f.readlines() if l.rstrip()]
            except FileNotFoundError:
                raise Exception('not ouput provided for command "{}"'.format(cmd_str))
            else:
                called[cmd_str] = input_text
                return output

    mocker.patch('uberspace_takeout.items.base.TakeoutItem.run_command', run_command)

    return called


def content(path):
    with open(path) as f:
        return f.read()


def assert_in_file(path, text):
    assert text in content(path)


def assert_files_equal(path1, path2):
    assert content(path1) == content(path2)


def assert_file_unchanged(path, fs):
    with Pause(fs):
        original = content(current_prefix_root(fs) / path.lstrip('/'))

    assert original == content(path)


def test_takeout_u6_to_u6(fs, mock_run_command):
    populate_root(fs, 'u6/isabell')

    takeout = Takeout(hostname='andromeda.uberspace.de')

    takeout.takeout('/tmp/test.tar.gz', 'isabell')

    clean_root()

    mock_run_command.clear()

    takeout.takein('/tmp/test.tar.gz', 'isabell')

    assert "mysql --defaults-group-suffix= -e SET PASSWORD = PASSWORD('Lei4eengekae3iet4Ies')" in mock_run_command
    assert_in_file('/home/isabell/.my.cnf', 'Lei4eengekae3iet4Ies')
    assert "mysql --defaults-group-suffix=readonly -e SET PASSWORD = PASSWORD('eeruaSooch6iereequoo')" in mock_run_command
    assert_in_file('/home/isabell/.my.cnf', 'eeruaSooch6iereequoo')

    assert "uberspace-add-domain -w -d *.example.com" in mock_run_command
    assert "uberspace-add-domain -w -d example.com" in mock_run_command
    assert "uberspace-add-domain -w -d foo.example.com" in mock_run_command
    assert "uberspace-add-domain -m -d mail.example.com" in mock_run_command

    assert "crontab -" in mock_run_command
    assert mock_run_command["crontab -"] == "@daily echo good morning\n"

    assert_file_unchanged('/var/www/virtual/isabell/html/index.html', fs)
    assert_file_unchanged('/var/www/virtual/isabell/html/blog/index.html', fs)
    assert os.path.islink('/home/isabell/html')
    assert_file_unchanged('/home/isabell/html/index.html', fs)
    assert_file_unchanged('/home/isabell/Maildir/cur/mail-888', fs)
