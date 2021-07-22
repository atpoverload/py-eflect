import importlib
import os

from argparse import ArgumentParser, ArgumentError

import eflect

from eflect.processing import compute_footprint

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
        default=os.getcwd(),
        help='path to output the data set to'
    )
    parser.add_argument(
        '-d',
        '--data',
        dest='data_set',
        default=None,
        help='path to the data set'
    )

    args = parser.parse_args()

    # check if there is a workload to run
    if args.file is not None and args.code is not None:
        raise ArgumentError('only one of --file or --code can be provided!')
    elif args.file is not None:
        spec = importlib.util.spec_from_file_location('module.name', args.file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        args.workload = lambda: module.run()
    elif args.code is not None:
        args.workload = lambda: exec(args.code)
    else:
        args.workload = None

    if args.workload is not None and args.data_set is not None:
        print('workload found; ignoring --data argument')
    elif args.workload is None and args.data_set is None:
        raise ArgumentError('one of --file, --code, or --data must be provided!')

    return args

def get_data(args):
    if args.workload is not None:
        # profile the workload
        data = eflect.profile(args.workload, period = args.period)
        with open(os.path.join(args.output, 'eflect-data.pb'), 'wb') as f:
            f.write(data.SerializeToString())
    elif os.path.exists(args.data_set):
        # load in an existing data_set
        data = eflect.load_data(data_set_path=args.data_set)
    else:
        raise ArgumentError('specified output data {} was not found!'.format(args.data_set))

    return data

def create_footprint(data, args):
    footprint = compute_footprint(data)
    with open(os.path.join(args.output, 'eflect-footprint.pb'), 'wb') as f:
        f.write(data.SerializeToString())
    return footprint
def main():
    args = parse_eflect_args()

    data = get_data(args)
    footprint = create_footprint(data, args)
    # we should have a user output customization somewhere here

if __name__ == '__main__':
    main()
