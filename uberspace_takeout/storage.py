import datetime
import errno
import os
import tarfile

try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO


class Storage:
    def __init__(self, destination, mode):
        if mode not in ("takein", "takeout"):
            raise Exception(
                'Invalid mode {}, expected "takein" or "takeout".'.format(mode)
            )

        self.destination = str(destination)
        self.mode = mode

    def __enter__(self):
        raise NotImplementedError()

    def __exit__(self, exception_type, exception_value, traceback):
        raise NotImplementedError()

    def list_files(self, storage_path):
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
        mode = "w:bz2" if self.mode == "takeout" else "r:bz2"
        self.tar = tarfile.open(self.destination, mode)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.tar.close()

    def _check_member_type(self, member):
        if member.type not in (tarfile.REGTYPE, tarfile.SYMTYPE, tarfile.DIRTYPE):
            raise Exception(
                "tar member has illegal type: {}. "
                "Must be tarfile.REGTYPE/file, SYMTYPE/symlink or DIRTYPE/directory, "
                "but is {}".format(member.name, member.type)
            )

    def clone_tarinfo(self, tarinfo):
        # "clone" the object so we don't modify names inside the tar
        tarinfo2 = tarfile.TarInfo()
        for attr in (*tarinfo.get_info().keys(), "offset", "offset_data"):
            setattr(tarinfo2, attr, getattr(tarinfo, attr))
        return tarinfo2

    def get_members_in(self, directory):
        directory = directory.rstrip("/") + "/"

        for m in self.tar.getmembers():
            if ".." in m.name:
                raise Exception(
                    'tar member has illegal name (contains ".."): ' + m.name
                )
            if m.name.startswith("/"):
                raise Exception(
                    'tar member has illegal name (starts with "/"): ' + m.name
                )
            if m.name.startswith("./"):
                raise Exception(
                    'tar member has illegal name (starts with "./"): ' + m.name
                )

            self._check_member_type(m)

            if m.name.startswith(directory):
                m = self.clone_tarinfo(m)
                # files might be stored as /www/domain.com/something.html, but need to be extracted
                # as domain.com/something.html.
                m.name = m.name[len(directory) :]
                yield m

    def has_member(self, path):
        for m in self.tar.getmembers():
            self._check_member_type(m)

            if m.name == path:
                return True

        return False

    def get_member(self, path):
        matching = []

        for m in self.tar.getmembers():
            self._check_member_type(m)

            if m.name == path:
                matching.append(m)

        if len(matching) == 0:
            raise FileNotFoundError()
        if len(matching) > 1:
            raise Exception(
                "There are {} files matching the path {}. Expected only one.".format(
                    len(matching), path
                )
            )

        return self.clone_tarinfo(matching[0])

    @classmethod
    def _len(cls, f):
        old_position = f.tell()
        f.seek(0, os.SEEK_END)
        length = f.tell()
        f.seek(old_position)
        return length

    def list_files(self, storage_path):
        members = list(self.get_members_in(storage_path))
        if not members:
            raise FileNotFoundError()
        return [m.name for m in members if "/" not in m.name]

    def store_text(self, content, storage_path):
        storage_path = str(storage_path).lstrip("/")
        content = BytesIO(content.encode("utf-8"))
        info = tarfile.TarInfo(storage_path)
        info.size = self._len(content)
        info.mtime = int(datetime.datetime.now().strftime("%s"))
        self.tar.addfile(info, content)

    def unstore_text(self, storage_path):
        storage_path = str(storage_path).lstrip("/")
        if not self.has_member(storage_path):
            raise FileNotFoundError()
        return self.tar.extractfile(storage_path).read().decode("utf-8")

    def store_file(self, system_path, storage_path):
        storage_path = str(storage_path).lstrip("/")
        if self.has_member(storage_path):
            raise FileExistsError()
        self.tar.add(str(system_path), storage_path)

    def unstore_directory(self, storage_path, system_path):
        storage_path = str(storage_path).lstrip("/")
        members = list(self.get_members_in(storage_path))
        if not members:
            raise FileNotFoundError()
        self.tar.extractall(system_path, members)

    def unstore_file(self, storage_path, system_path):
        storage_path = str(storage_path).lstrip("/")
        member = self.get_member(storage_path)
        member.name = os.path.basename(system_path)
        self.tar.extractall(os.path.dirname(system_path), [member])


class LocalMoveStorage(Storage):
    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass

    def _storage_path(self, storage_path):
        storage_path = str(storage_path).lstrip("/")
        return self.destination + "/" + storage_path

    def _mkdir_p(self, path):
        if not path:
            return

        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def list_files(self, storage_path):
        storage_path = self._storage_path(storage_path)
        if not os.path.exists(storage_path):
            raise FileNotFoundError()
        return os.listdir(storage_path)

    def store_text(self, content, storage_path):
        storage_path = self._storage_path(storage_path)
        if os.path.exists(storage_path):
            raise FileExistsError()
        self._mkdir_p(os.path.dirname(storage_path))
        with open(storage_path, "w") as f:
            f.write(content)

    def unstore_text(self, storage_path):
        with open(self._storage_path(storage_path)) as f:
            return f.read()

    def store_file(self, system_path, storage_path):
        storage_path = self._storage_path(storage_path)
        if os.path.exists(storage_path):
            raise FileExistsError()
        self._mkdir_p(os.path.dirname(storage_path))
        os.rename(system_path, storage_path)

    def unstore_file(self, storage_path, system_path):
        storage_path = self._storage_path(storage_path)
        if not os.path.exists(storage_path):
            raise FileNotFoundError()
        self._mkdir_p(os.path.dirname(system_path))
        os.rename(storage_path, system_path)
