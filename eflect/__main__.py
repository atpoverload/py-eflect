import os

from argparse import ArgumentParser, ArgumentError

from eflect import profile

def parse_eflect_args():
    parser = ArgumentParser()
    parser.add_argument(
        '-f',
        '--file',
        dest='file',
        default=None,
        help='name of file to be profiled'
    )
    parser.add_argument(
        '-c',
        '--code',
        dest='code',
        default=None,
        help='code to be profiled'
    )
    parser.add_argument(
        '-p',
        '--period',
        dest='period',
        type=int,
        default = 50,
        help='data collection period'
    )
    parser.add_argument(
        '-o',
        '--out',
        dest='output',
        default=os.path.join(os.getcwd(), 'data'),
        help='output file for footprints'
    )

    args = parser.parse_args()
    if args.file is None and args.code is None:
        raise ArgumentError('one of file or code must be provided')

    if args.file is not None:
        args.workload = lambda: exec(args.file)
    else:
        args.workload = lambda: exec(args.code)

    return args

def main():
    args = parse_eflect_args()
    footprints = profile(args.workload, period = args.period, output_dir = args.output)
    footprints.to_csv(os.path.join(args.output, 'accounted-energy'))

if __name__ == '__main__':
    main()
