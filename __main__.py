from argparse import ArgumentParser
from time import time

import eflect

def add_eflect_args(parser):
    parser.add_argument(
        '-p',
        '--period',
        dest='period',
        default = 41,
        help='data collection period'
    )
    parser.add_argument(
        '-o',
        '--out',
        dest='output',
        default='eflect-' + str(time()),
        help='output file for footprints'
    )

def main():
    parser = ArgumentParser(description='Arguments for eflect')
    add_eflect_args(parser)
    parser.add_argument('-c', dest='code', help='code to execute')
    args = parser.parse_args()

    footprints = eflect.run(args.code, args.period)
    print(footprints)

if __name__=='__main__':
    main()
