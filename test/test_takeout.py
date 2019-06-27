from pathlib import Path
import os
import configparser
import shutil

import pytest

from uberspace_takeout import Takeout


def populate_root(fs, new_root):
    outside_root = Path(__file__).parent / 'uberspaces' / new_root

    # copy into memory-fs as /rootcontent, because we cannot replace / directly
    fs.add_real_directory(outside_root, lazy_read=False, target_path='/rootcontent')

    # add each root-dir individually
    for path in os.listdir('/rootcontent'):
        fs.add_real_directory(outside_root / path, lazy_read=False, read_only=False, target_path='/' + path)


def clean_root(skip_dirs=['commands', 'tmp', 'etc']):
    for path in os.listdir('/'):
        if path not in skip_dirs:
            shutil.rmtree('/' + path)

    Path('/home').mkdir()
    Path('/var/www/virtual').mkdir(parents=True)


@pytest.fixture
def mock_run_command(mocker):
    called = []

    def run_command(self, cmd, *args, **kwargs):
        called.append(" ".join(cmd))
        try:
            with open('/commands/' + ' '.join(cmd), 'r') as f:
                return [l.rstrip() for l in f.readlines() if l.rstrip()]
        except FileNotFoundError:
            raise Exception('not ouput provided for command "{}"'.format(" ".join(cmd)))

    mocker.patch('uberspace_takeout.items.base.TakeoutItem.run_command', run_command)

    return called


def test_takeout_u6(fs, mock_run_command):
    populate_root(fs, 'u6/isabell')

    takeout = Takeout(hostname='andromeda.uberspace.de')

    takeout.takeout('/tmp/test.tar.gz', 'isabell')

    clean_root()

    takeout.takein('/tmp/test.tar.gz', 'isabell')
    assert "mysql --defaults-group-suffix= -e SET PASSWORD = PASSWORD('Lei4eengekae3iet4Ies')" in mock_run_command
    assert "mysql --defaults-group-suffix=readonly -e SET PASSWORD = PASSWORD('eeruaSooch6iereequoo')" in mock_run_command
    assert "uberspace-add-domain -w -d *.example.com" in mock_run_command
    assert "uberspace-add-domain -w -d example.com" in mock_run_command
    assert "uberspace-add-domain -w -d foo.example.com" in mock_run_command
    assert "uberspace-add-domain -m -d mail.example.com" in mock_run_command
