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
    elif os.path.exists(args.data_set):
        # load in an existing data_set
        return eflect.load_data(data_set_path=args.data_set)
    else:
        raise ArgumentError('specified output data {} was not found!'.format(args.data_set))

def main():
    args = parse_eflect_args()

    data = get_data(args)
    footprint = compute_footprint(data)

    # we should have a user output customization somewhere here
    with open(os.path.join(args.output, 'eflect-data.pb'), 'wb') as f:
        f.write(data.SerializeToString())
    with open(os.path.join(args.output, 'eflect-footprint.pb'), 'wb') as f:
        f.write(footprint.SerializeToString())

    # print(footprint)

if __name__ == '__main__':
    main()
