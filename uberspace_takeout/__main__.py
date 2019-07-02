import argparse
import datetime
import getpass

from . import Takeout


def main():
    username = getpass.getuser()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
    default_tar_path = 'takeout_{}_{}.tar.bz2'.format(username, timestamp)

    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['takeout', 'takein'])
    p.add_argument('--username', default=username)
    p.add_argument('--tar-file', default=default_tar_path)
    args = p.parse_args()

    tar_path = args.tar_file

    if tar_path == '-':
        tar_path = '/dev/stdout'

    if args.action == 'takeout':
        Takeout().takeout(tar_path, args.username)
    elif args.action == 'takein':
        Takeout().takein(tar_path, args.username)
    else:
        raise NotImplementedError()


if __name__ == '__main__':
    main()
