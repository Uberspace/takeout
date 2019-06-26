import argparse
import datetime
import getpass

from . import TakeoutU7


def main():
    username = getpass.getuser()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
    default_tar_path = 'takeout_{}_{}.tar.bz2'.format(username, timestamp)

    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['takeout', 'takein'])
    p.add_argument('--tar-file', default=default_tar_path)
    args = p.parse_args()

    tar_path = args.tar_file

    if tar_path == '-':
        tar_path = '/dev/stdout'

    if args.action == 'takeout':
        TakeoutU7().takeout(tar_path, username)
    elif args.action == 'takein':
        TakeoutU7().takein(tar_path, username)
    else:
        raise NotImplementedError()


if __name__ == '__main__':
    main()
