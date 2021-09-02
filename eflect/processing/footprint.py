""" Methods that turn EflectDataSets into EflectFootprints. """

from eflect.data.util import get_unixtime
from eflect.processing.accounting import account_jiffies, account_rapl_energy, align_yappi_methods
from eflect.proto.footprint_pb2 import EflectFootprint, EflectFootprints
from eflect.processing.preprocessing import stat_to_df, task_to_df, rapl_to_df, yappi_to_df

def populate_footprint(idx, energy):
    footprint = EflectFootprint()
    footprint.timestamp = get_unixtime(10 ** 3 * idx[0].timestamp())
    footprint.thread_id = idx[1]
    footprint.thread_name = idx[2]
    footprint.component = idx[3]
    footprint.energy = energy
    for method in idx[4].split(';'):
        footprint.stack_trace.append(method)

    return footprint

def compute_footprint(data):
    """ Produces a csv footprint from the data set. """
    # all these turn the protobuf data into pandas data frames
    activity = account_jiffies(task_to_df(data.proc_task), stat_to_df(data.proc_stat))
    energy = account_rapl_energy(rapl_to_df(data.rapl), activity.dropna())
    # TODO(timur): the methods and components being reported separately is causing
    #   lots of unnecessary bloat since there may be multiple methods per thread
    #   we probably need name mappings to simplify this
    footprints = align_yappi_methods(energy, yappi_to_df(data.yappi_stack_trace))

    # footprints = EflectFootprints()
    # for idx, s in energy.iteritems():
    #     footprints.footprint.add().CopyFrom(populate_footprint(idx, s))

    return footprints
