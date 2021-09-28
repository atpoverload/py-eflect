""" Driver for a cli tool to profile code with eflect. """

import os
import sys

sys.path.append('.')

import eflect

from eflect.args import parse_eflect_args

def get_data(args):
    """ Runs the workload or, if there's no workload, load data from a path """
    if args.workload is not None:
        # profile the workload
        if args.fake:
            return fake_eflect.profile(args.workload, period=args.period)
        else:
            return eflect.profile(args.workload, period=args.period)
    elif os.path.exists(args.data):
        # load in an existing data_set
        return eflect.load_data_set(data_set_path=args.data)
    else:
        raise ArgumentError('specified output data {} was not found!'.format(args.data))

def write_data(args, data, footprint):
    """ Write the footprint and, if a workload was run, the raw data. """
    if args.workload is not None and args.data is not None:
        with open(os.path.join(args.data, 'eflect-data.pb'), 'wb') as f:
            f.write(data.SerializeToString())
        data_dir = os.path.dirname(args.data)
        footprint.to_csv(os.path.join(data_dir, 'eflect-footprint.csv'))
    elif not args.fake and args.data is not None:
        data_dir = os.path.dirname(args.data)
        footprint.to_csv(os.path.join(data_dir, 'eflect-footprint.csv'))

def main():
    args = parse_eflect_args()

    data = get_data(args)
    footprint = eflect.compute_footprint(data)
    write_data(args, data, footprint)

if __name__ == '__main__':
    main()
