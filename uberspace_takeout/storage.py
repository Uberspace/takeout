import datetime
import tarfile

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class Storage():
    def __init__(self, destination):
        self.destination = destination

    def __enter__(self):
        raise NotImplementedError()

    def __exit__(self):
        raise NotImplementedError()

    def store_text(self, content, storage_path):
        raise NotImplementedError()

    def unstore_text(self, storage_path):
        raise NotImplementedError()

    def store_file(self, system_path, storage_path):
        raise NotImplementedError()

    def unstore_file(self, storage_path, system_path):
        raise NotImplementedError()

    def store_directory(self, system_path, storage_path):
        return self.store_file(system_path, storage_path)

    def unstore_directory(self, storage_path, system_path):
        return self.unstore_file(storage_path, system_path)


class TarStorage(Storage):

    def __enter__(self):
        self.tar = tarfile.open(self.destination, 'w:bz2')
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.tar.close()

    def get_members_in(self, directory):
        directory = directory.rstrip('/') + '/'

        for m in self.tar.getmembers():
            if '..' in m.name:
                raise Exception('tar member has illegal name (contains ".."): ' + m.name)
            if m.name.startswith('/'):
                raise Exception('tar member has illegal name (starts with "/"): ' + m.name)
            if m.name.startswith('./'):
                raise Exception('tar member has illegal name (starts with "./"): ' + m.name)

            if m.type not in (tarfile.REGTYPE, tarfile.SYMTYPE, tarfile.DIRTYPE):
                raise Exception(
                    'tar member has illegal type: {}.'
                    'Must be tarfile.REGTYPE/file, SYMTYPE/symlink or DIRTYPE/directory, '
                    'but is {}'.format(m.name, m.type)
                )

            if m.name.startswith(directory):
                # files might be stored as /www/domain.com/something.html, but need to be extracted
                # as domain.com/something.html.
                m.name = m.name[len(directory):]
                yield m

    def store_text(self, content, storage_path):
        content = StringIO(content)
        info = tarfile.TarInfo(storage_path)
        info.size = content.len
        info.mtime = int(datetime.datetime.now().strftime("%s"))
        self.tar.addfile(info, content)

    def unstore_text(self, storage_path):
        return self.tar.extractfile(storage_path).read()

    def store_file(self, system_path, storage_path):
        self.tar.add(system_path, storage_path)

    def unstore_file(self, storage_path, system_path):
        self.tar.extractall(system_path, self.get_members_in(storage_path))
