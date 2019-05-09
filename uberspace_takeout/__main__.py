import sys

from . import TakeoutU7


def main():
    if sys.argv[1] == 'takeout':
        TakeoutU7().takeout(sys.argv[2])
    elif sys.argv[1] == 'takein':
        TakeoutU7().takein(sys.argv[3], sys.argv[2])


if __name__ == '__main__':
    main()
