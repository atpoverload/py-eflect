""" Driver for a cli tool to profile code with eflect. """

import os
import sys

sys.path.append('.')

import eflect
import eflect.processing

from eflect.args import parse_eflect_args
from eflect.fake import fake_eflect

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
        return eflect.load_data_set(data_set_path=args.data)
    else:
        raise ArgumentError('specified output data {} was not found!'.format(args.data))

def write_data(args, data, footprint):
    """ Write the footprint and, if a workload was run, the raw data. """
    if args.workload is not None and args.data is not None:
        with open(os.path.join(args.data, 'eflect-data.pb'), 'wb') as f:
            f.write(data.SerializeToString())
        # with open(os.path.join(args.data, 'eflect-footprint.pb'),'wb') as f:
        #     f.write(footprint.SerializeToString())
        footprint.to_csv(os.path.join(args.data, 'eflect-footprint.csv'))
    elif not args.fake and args.data is not None:
        data_dir = os.path.dirname(args.data)
        # with open(os.path.join(data_dir,'eflect-footprint.pb'),'wb') as f:
        #     f.write(footprint.SerializeToString())
        footprint.to_csv(os.path.join(args.data, 'eflect-footprint.csv'))

def main():
    args = parse_eflect_args()

    data = get_data(args)

    # TODO(timur): this output is huge! we should figure out something better
    #   to do along the way; i'm dealing with a csv right now but it's not what
    #   i want to be doing.
    footprint = eflect.processing.compute_footprint(data)
    # print(footprint.groupby('stack_trace').sum().sort_values(ascending=False).head(50))

    # we should do the summary here
    write_data(args, data, footprint)

if __name__ == '__main__':
    main()
