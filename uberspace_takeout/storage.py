import datetime
import tarfile
import os

try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO


class Storage():
    def __init__(self, destination, mode):
        if mode not in ('takein', 'takeout'):
            raise Exception('Invalid mode {}, expected "takein" or "takeout".'.format(mode))

        self.destination = str(destination)
        self.mode = mode

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
        mode = 'w:bz2' if self.mode == 'takeout' else 'r:bz2'
        self.tar = tarfile.open(self.destination, mode)
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

    @classmethod
    def _len(cls, f):
        old_position = f.tell()
        f.seek(0, os.SEEK_END)
        length = f.tell()
        f.seek(old_position)
        return length

    def store_text(self, content, storage_path):
        storage_path = str(storage_path).lstrip('/')
        content = BytesIO(content.encode('utf-8'))
        info = tarfile.TarInfo(storage_path)
        info.size = self._len(content)
        info.mtime = int(datetime.datetime.now().strftime("%s"))
        self.tar.addfile(info, content)

    def unstore_text(self, storage_path):
        storage_path = str(storage_path).lstrip('/')
        return self.tar.extractfile(storage_path).read().decode('utf-8')

    def store_file(self, system_path, storage_path):
        storage_path = str(storage_path).lstrip('/')
        self.tar.add(str(system_path), storage_path)

    def unstore_file(self, storage_path, system_path):
        storage_path = str(storage_path).lstrip('/')
        self.tar.extractall(system_path, self.get_members_in(storage_path))
