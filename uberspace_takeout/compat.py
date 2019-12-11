try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO  # noqa

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path  # noqa

try:
    FileExistsError = FileExistsError
    FileNotFoundError = FileNotFoundError
except NameError:
    FileExistsError = IOError
    FileNotFoundError = IOError
