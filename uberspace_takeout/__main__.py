import argparse
import datetime
import getpass
import sys

from . import Takeout


def main():
    username = getpass.getuser()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
    default_tar_path = 'takeout_{}_{}.tar.bz2'.format(username, timestamp)

    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['takeout', 'takein', 'items'])
    p.add_argument('--username', default=username)
    p.add_argument('--skip-item', action='append', default=[])
    p.add_argument('--tar-file', default=default_tar_path)
    args = p.parse_args()

    tar_path = args.tar_file

    if args.action == 'takeout':
        if tar_path == '-':
            tar_path = '/dev/stdout'
            sys.stdout = sys.stderr

        print('writing ' + tar_path)
        Takeout().takeout(tar_path, args.username, args.skip_item)
    elif args.action == 'takein':
        if tar_path == '-':
            tar_path = '/dev/stdin'

        print('reading ' + tar_path)
        Takeout().takein(tar_path, args.username, args.skip_item)
    elif args.action == 'items':
        print(
            '\n'.join(
                i.__name__.ljust(25, ' ') + i.description for i in Takeout.takeout_menu
            )
        )
    else:
        raise NotImplementedError()


if __name__ == '__main__':
    main()
