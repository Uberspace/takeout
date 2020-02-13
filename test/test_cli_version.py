import subprocess

from uberspace_takeout import __version__


def test_cli_version(capfdbinary):
    command = ["uberspace-takeout", "--version"]
    res = subprocess.run(command)
    assert res.returncode == 0
    out, err = capfdbinary.readouterr()
    version = out.decode("utf-8").strip()
    assert version == __version__
