# Uberspace Takeout

Import and export _uberspaces_ to and from special `.tar` files.

## Items

Takeout is organized in **TakeoutItems**, which handle the import and export of
a single topic. `Homedir` takes care of all files in the users home directory,
`MySQLPassword` gets and sets the MySQL passwords.

Implementations can be found in `uberspace_takeout/items/{common,u6,u7}.py`.

## Usage

To get ready, install takeout using git and pip:

```console
$ git clone https://github.com/Uberspace/takeout.git
$ cd takeout
$ pip install --user -e .
```

After pip is done, you can access the tool by calling `uberspace-takeout`:

```console
$ uberspace-takeout --help
```

### Tasks

Use `uberspace-takeout items` to list all tasks, which can be executed.

```console
$ uberspace-takeout items
TakeoutMarker            Takeout Marker (internal)
Homedir                  Homedirectory
Www                      Documentroot
Cronjobs                 Cronjobs
MailDomains              Mail Domains
(...)
```

Note that some items will be duplicated (once for U6 and once for U7) and that
some might not run at all, because they aren't available for uberspace version
takeout is running on.

### Exporting: Takeout

Takeout creates an archive of everything that makes up an uberspace. This
includes files, software versions, mysql passwords and much more. Exporting
MySQL databases is not yet implemented.

```console
$ uberspace-takeout takeout
writing takeout_luto_2019-09-04_14_44_30.tar.bz2
takeout: TakeoutMarker
takeout: Homedir
takeout: Www
takeout: Cronjobs
takeout: MySQLPassword
takeout: AccessLogItem
takeout: ApacheErrorLogItem
takeout: PhpErrorLogItem
takeout: SpamfilterLogItem
takeout: ToolVersions
takeout: WebDomains
takeout: MailDomains
$ ll *.tar.bz2
-rw-r--r-- 1 luto luto 132 Sep  4 14:44 takeout_luto_2019-09-04_14_44_30.tar.bz2
```

### Importing: Takein

You can read an archive created by `uberspace-takeout takeout` using
`... takein`. It will, to the best of its ability, restore all settings and
files exported earlier. Importing MySQL databases is not yet implemented.

```console
$ uberspace-takeout takein --tar-file takeout_luto_2019-09-04_14_44_30.tar.bz2
reading takeout_luto_2019-09-04_14_44_30.tar.bz2
takein: TakeoutMarker
takein: Homedir
takein: Www
takein: Cronjobs
takein: MySQLPassword
takein: AccessLogItem
takein: ApacheErrorLogItem
takein: PhpErrorLogItem
takein: SpamfilterLogItem
takein: ToolVersions
takein: WebDomains
takein: MailDomains
```

## Development

After cloning, create a _virtual environment_:

```console
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

Install the development-requirements:

```
pip install -r requirements.txt
```

And run some setup:

```
pre-commit install
```

After that you can…

### Lint

```console
pre-commit run --all-files
```

### Test

```console
tox
```

### Release

Assuming you have been handed the required credentials, a new version
can be released as follows.

1. adapt the `__version__` in `uberspace_takeout/__init__.py`, according to [semver][].
2. commit this change as `Version 1.2.3`
3. tag the resulting commit as `v1.2.3`
4. push the new tag as well as the `master` branch
5. update the package on PyPI:

```console
$ rm dist/*
$ python setup.py sdist bdist_wheel
$ twine upload dist/*
```

[semver]: https://semver.org/
