""" Methods that turn EflectDataSets into EflectFootprints. """

import os

from sys import argv

import numpy as np
import pandas as pd

from eflect.data.util import get_unixtime
from eflect.proto.footprint_pb2 import EflectFootprint, EflectFootprints
from eflect.proto.processing import parse_proc_stat
from eflect.proto.processing import parse_proc_task
from eflect.proto.processing import parse_rapl
from eflect.proto.processing import parse_yappi
from eflect.processing.preprocessing import process_proc_stat_data
from eflect.processing.preprocessing import process_proc_task_data
from eflect.processing.preprocessing import process_rapl_data
from eflect.processing.preprocessing import process_yappi_data

# TODO: find out if there's a general conversion formula
DOMAIN_CONVERSION = lambda x: 0 if int(x) < 20 else 1

def account_jiffies(proc_task, proc_stat):
    """ Returns the ratio of the jiffies with a correction for overaccounting. """
    return (proc_task / proc_stat.replace(0, 1)).replace(np.inf, 1).clip(0, 1)

def account_energy(energy, activity):
    """ Returns the product of the energy and the cpu-aligned activity data. """
    activity = activity.reset_index()
    activity['socket'] = activity.cpu.apply(DOMAIN_CONVERSION)
    activity = activity.set_index(['timestamp', 'id', 'socket'])[0]

    # i don't like merging
    activity = activity.reset_index()
    energy = energy.reset_index()
    df = pd.merge(activity, energy, on=['timestamp', 'socket'])
    df[0] = df['0_x'] * df['0_y']
    df = df.set_index(['timestamp', 'id', 'component', 'socket'])[0]

    return df

def align_yappi_methods(energy, yappi_methods):
    """ Aligns yappi traces to timestamp-id pairs. """
    energy = energy.reset_index()
    energy['name'] = energy.id.str.split('-').str[1]
    energy.id = energy.id.str.split('-').str[0].replace(np.nan, 0).astype(int)

    energy = energy.groupby(['timestamp', 'id', 'name', 'component'])[0].sum() * yappi_methods
    energy = energy.groupby(['timestamp', 'id', 'name', 'component', 'stack_trace']).sum().sort_values(ascending=False)

    return energy

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
    activity = account_jiffies(
        process_proc_task_data(parse_proc_task(data.proc_task)),
        process_proc_stat_data(parse_proc_stat(data.proc_stat))
    ).dropna()

    energy = account_energy(
        process_rapl_data(parse_rapl(data.rapl)),
        activity
    )

    energy = align_yappi_methods(
        energy,
        process_yappi_data(parse_yappi(data.yappi_stack_trace)),
    )

    print(energy.sort_values(ascending=False).head(50))

    footprints = EflectFootprints()
    for idx, s in energy.iteritems():
        footprints.footprint.add().CopyFrom(populate_footprint(idx, s))

    print(footprints.footprint[0])
    return footprints
