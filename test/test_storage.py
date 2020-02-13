import pytest

from uberspace_takeout.storage import LocalMoveStorage
from uberspace_takeout.storage import Storage
from uberspace_takeout.storage import TarStorage


@pytest.mark.parametrize("mode", ["takeout", "takein",])
def test_storage_ctor(mode):
    s = Storage("dest.tar.gz", mode)
    assert s.destination == "dest.tar.gz"
    assert s.mode == mode


def test_storage_ctor_mode():
    with pytest.raises(Exception) as ex:
        Storage("dest.tar.gz", "foo")

    assert "Invalid mode foo" in str(ex)


@pytest.fixture
def test_file(tmp_path):
    path = tmp_path / "some_file.txt"

    with path.open("w") as f:
        f.write(u"some file text")

    return path


@pytest.fixture
def test_file2(tmp_path):
    path = tmp_path / "some_file2.txt"

    with path.open("w") as f:
        f.write(u"some file text2")

    return path


@pytest.fixture
def test_dir(tmp_path):
    (tmp_path / "some_dir/some_subdir").mkdir(parents=True)

    with (tmp_path / "some_dir/file.txt").open("w") as f:
        f.write(u"some file text")

    with (tmp_path / "some_dir/some_subdir/file2.txt").open("w") as f:
        f.write(u"some file text 2")

    return tmp_path / "some_dir"


storages = [
    TarStorage,
    LocalMoveStorage,
]


@pytest.mark.parametrize("storage", storages)
def test_storage_text(storage, tmp_path):
    with storage(tmp_path / "test.tar.gz", "takeout") as s:
        s.store_text("some text 1", "simple_text.txt")
        s.store_text("some text 2", "subdir/bla/simple_text.txt")

    with storage(tmp_path / "test.tar.gz", "takein") as s:
        assert s.unstore_text("simple_text.txt") == "some text 1"
        assert s.unstore_text("subdir/bla/simple_text.txt") == "some text 2"


@pytest.mark.parametrize("storage", storages)
def test_storage_file(storage, tmp_path, test_file, test_file2):
    with storage(tmp_path / "test.tar.gz", "takeout") as s:
        s.store_file(test_file, "simple_file.txt")
        s.store_file(test_file2, "subdir/bla/simple_file.txt")

    with storage(tmp_path / "test.tar.gz", "takein") as s:
        assert s.unstore_text("simple_file.txt") == "some file text"
        # read twice to check hat we don't break the tarinfo objects
        assert s.unstore_text("subdir/bla/simple_file.txt") == "some file text2"
        assert s.unstore_text("subdir/bla/simple_file.txt") == "some file text2"

        s.unstore_file("simple_file.txt", tmp_path / "extracted.txt")

        with (tmp_path / "extracted.txt").open() as f:
            assert f.read() == "some file text"


@pytest.mark.parametrize("storage", storages)
def test_storage_file_eexists(storage, tmp_path, test_file):
    with storage(tmp_path / "test.tar.gz", "takeout") as s:
        s.store_file(test_file, "simple_file.txt")

        test_file.touch()

        with pytest.raises(FileExistsError):
            s.store_file(test_file, "simple_file.txt")


@pytest.mark.parametrize("storage", storages)
def test_storage_file_noent(storage, tmp_path, test_file):
    with storage(tmp_path / "test.tar.gz", "takeout") as s:
        pass

    with storage(tmp_path / "test.tar.gz", "takein") as s:
        with pytest.raises(FileNotFoundError):
            s.unstore_file("simple_file.txt", tmp_path / "somefile")


@pytest.mark.parametrize("storage", storages)
def test_storage_directory(storage, tmp_path, test_dir):
    with storage(tmp_path / "test.tar.gz", "takeout") as s:
        s.store_directory(test_dir, "dir")

    with storage(tmp_path / "test.tar.gz", "takein") as s:
        assert s.unstore_text("dir/some_subdir/file2.txt") == "some file text 2"

        s.unstore_directory("dir", tmp_path / "new_dir")

        with (tmp_path / "new_dir" / "file.txt").open() as f:
            assert f.read() == "some file text"

        with (tmp_path / "new_dir" / "some_subdir/file2.txt").open() as f:
            assert f.read() == "some file text 2"


@pytest.mark.parametrize("storage", storages)
def test_storage_directory_eexists(storage, tmp_path, test_dir):
    with storage(tmp_path / "test.tar.gz", "takeout") as s:
        s.store_directory(test_dir, "dir")

        test_dir.mkdir(exist_ok=True)

        with pytest.raises(FileExistsError):
            s.store_directory(test_dir, "dir")


@pytest.mark.parametrize("storage", storages)
def test_storage_directory_noent(storage, tmp_path):
    with storage(tmp_path / "test.tar.gz", "takeout") as s:
        pass

    with storage(tmp_path / "test.tar.gz", "takein") as s:
        with pytest.raises(FileNotFoundError):
            s.unstore_directory("dir", tmp_path / "new_dir")


@pytest.mark.parametrize("storage", storages)
def test_storage_list_files(storage, tmp_path, test_dir):
    with storage(tmp_path / "test.tar.gz", "takeout") as s:
        s.store_directory(test_dir, "dir")
        assert sorted(s.list_files("dir")) == ["file.txt", "some_subdir"]
        assert sorted(s.list_files("dir/some_subdir")) == ["file2.txt"]


@pytest.mark.parametrize("storage", storages)
def test_storage_list_files_noent(storage, tmp_path, test_dir):
    with storage(tmp_path / "test.tar.gz", "takeout") as s:
        pass

    with storage(tmp_path / "test.tar.gz", "takeout") as s:
        with pytest.raises(FileNotFoundError):
            s.list_files("dir")


@pytest.mark.parametrize("storage", storages)
def test_storage_slashes(storage, tmp_path, test_file):
    with storage(tmp_path / "test.tar.gz", "takeout") as s:
        s.store_text("some text 3", "/subdir/bla/simple_text2.txt")
        s.store_file(test_file, "/subdir/bla/simple_file2.txt")

    with storage(tmp_path / "test.tar.gz", "takein") as s:
        assert s.unstore_text("/subdir/bla/simple_text2.txt") == "some text 3"
        assert s.unstore_text("/subdir/bla/simple_file2.txt") == "some file text"
        assert s.unstore_text("subdir/bla/simple_text2.txt") == "some text 3"
        assert s.unstore_text("subdir/bla/simple_file2.txt") == "some file text"


def test_localmovestorage_file_removed(tmp_path, test_file):
    with LocalMoveStorage(tmp_path / "test.tar.gz", "takeout") as s:
        assert test_file.exists()
        s.store_file(test_file, "simple_file.txt")
        assert not test_file.exists()


def test_localmovestorage_directory_removed(tmp_path, test_dir):
    with LocalMoveStorage(tmp_path / "test.tar.gz", "takeout") as s:
        assert test_dir.exists()
        s.store_directory(test_dir, "dir")
        assert not test_dir.exists()
