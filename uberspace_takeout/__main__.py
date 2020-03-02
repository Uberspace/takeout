import argparse
import datetime
import getpass
import sys

from . import __version__ as version
from . import Takeout


def main():
    username = getpass.getuser()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    default_tar_path = f"takeout_{username}_{timestamp}.tar.bz2"

    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["takeout", "takein", "items"])
    p.add_argument("--username", default=username)
    p.add_argument("--skip-item", action="append", default=[])
    p.add_argument("--tar-file", default=default_tar_path)
    p.add_argument("--version", action="version", version=version)
    args = p.parse_args()

    tar_path = args.tar_file
    t = Takeout()

    if args.action == "takeout":
        if tar_path == "-":
            tar_path = "/dev/stdout"
            sys.stdout = sys.stderr

        print(f"writing {tar_path}")
        t.takeout(tar_path, args.username, args.skip_item)

    elif args.action == "takein":
        if tar_path == "-":
            tar_path = "/dev/stdin"

        print(f"reading {tar_path}")
        t.takein(tar_path, args.username, args.skip_item)

    elif args.action == "items":
        items = (f"{i.__name__: <25}{i.description}" for i in Takeout.takeout_menu)
        print("\n".join(items))
        return 0

    else:
        raise NotImplementedError()

    if t.errors:
        print()
        for item_class, errors in t.errors.items():
            print(f"[ERROR] {item_class}:")
            for error in errors:
                print(f"- {error}")
        print()
        return 1

    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
