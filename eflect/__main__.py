import importlib
import os

from argparse import ArgumentParser, ArgumentError

import eflect

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

    # check if there is a workload to run
    if args.file is not None and args.code is not None:
        raise ArgumentError('only one of --file or --code can be specified!')
    elif args.file is not None:
        spec = importlib.util.spec_from_file_location('module.name', args.file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        args.workload = lambda: module.run()
    elif args.code is not None:
        args.workload = lambda: exec(args.code)
    else:
        args.workload = None

    return args

def main():
    args = parse_eflect_args()

    # profile the workload
    if args.workload is not None:
        eflect.profile(args.workload, period = args.period, output_dir = args.output)

    if not os.path.exists(args.output):
        raise ArgumentError('specified output directory {} was not found!'.format(args.output))

    # get the footprints
    footprint, ranking, footprint2, ranking2 = eflect.read(output_dir = args.output)

    footprint.to_csv(os.path.join(args.output, 'footprint.csv'))
    ranking.to_csv(os.path.join(args.output, 'ranking.csv'))

    footprint2.to_csv(os.path.join(args.output, 'footprint-gpu.csv'))
    ranking2.to_csv(os.path.join(args.output, 'ranking-gpu.csv'))

if __name__ == '__main__':
    main()
