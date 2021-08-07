""" Driver for a cli tool to profile code with eflect. """

import os

import eflect
from eflect.fake import fake_eflect

from args import parse_eflect_args
from eflect.processing import compute_footprint

def get_data(args):
    """ Runs the workload or, if there's no workload, load data from a path """
    if args.workload is not None:
        # profile the workload
        if args.fake:
            return fake_eflect.profile(args.workload, period = args.period)
        else:
            return eflect.profile(args.workload, period = args.period)
    elif os.path.exists(args.data):
        # load in an existing data_set
        return eflect.load_data(data_set_path=args.data)
    else:
        raise ArgumentError('specified output data {} was not found!'.format(args.data))

def write_data(args, data, footprint):
    """ Write the footprint and, if a workload was run, the raw data. """
    if args.workload is not None and args.data is not None:
        with open(os.path.join(args.data, 'eflect-data.pb'), 'wb') as f:
            f.write(data.SerializeToString())
        with open(os.path.join(args.data, 'eflect-footprint.pb'),'wb') as f:
            f.write(footprint.SerializeToString())
    elif args.data is not None:
        data_dir = os.path.dirname(args.data)
        with open(os.path.join(data_dir,'eflect-footprint.pb'),'wb') as f:
            f.write(footprint.SerializeToString())

def main():
    args = parse_eflect_args()

    data = get_data(args)
    footprint = compute_footprint(data)
    write_data(args, data, footprint)
    # we should have a human readable output
    print(footprint.footprint[-1])

if __name__ == '__main__':
    main()
