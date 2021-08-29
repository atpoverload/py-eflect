""" Arguments for the eflect cli tool. """

import importlib
import os

from argparse import ArgumentParser

def parse_eflect_args():
    parser = ArgumentParser()
    # experiment args
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
        default=0.050,
        help='data collection period'
    )
    parser.add_argument(
        '--fake',
        dest='fake',
        action='store_true',
        help='whether to use a fake rapl source'
    )
    parser.add_argument(
        '-d',
        '--data',
        dest='data',
        default=None,
        help='path to write the data set in profiling mode; path of the data set otherwise'
    )

    args = parser.parse_args()

    # check if there is a workload to run
    if args.file is not None and args.code is not None:
        raise RuntimeError('only one of --file or --code can be provided!')
    elif args.file is not None:
        spec = importlib.util.spec_from_file_location('module.name', args.file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        args.workload = lambda: module.main()
    elif args.code is not None:
        args.workload = lambda: exec(args.code)
    else:
        args.workload = None

    if args.workload is None and args.data is None:
        raise RuntimeError('one of --file, --code, or --data must be provided!')

    return args
