import os

from sys import argv

import numpy as np
import pandas as pd

from eflect.proto.footprint_pb2 import EnergyFootprint, EnergyFootprints
from eflect.proto.processing import parse_proc_stat
from eflect.proto.processing import parse_proc_task
from eflect.proto.processing import parse_rapl
from eflect.proto.processing import parse_yappi
from eflect.processing.preprocessing import process_proc_stat_data
from eflect.processing.preprocessing import process_proc_task_data
from eflect.processing.preprocessing import process_rapl_data
from eflect.processing.preprocessing import process_yappi_data

DOMAIN_CONVERSION = lambda x: 0 if int(x) < 20 else 1

def account_jiffies(proc_task, proc_stat):
    return (proc_task / proc_stat.replace(0, 1)).replace(np.inf, 1).clip(0, 1)

def account_energy(energy, activity):
    activity = activity.reset_index()
    activity['socket'] = activity.cpu.apply(DOMAIN_CONVERSION)
    activity = activity.set_index(['timestamp', 'id', 'socket'])[0]

    return energy * activity

def align_yappi_methods(energy, yappi_methods):
    energy = energy.reset_index()
    energy['name'] = energy.id.str.split('-').str[1]
    energy.id = energy.id.str.split('-').str[0].replace(np.nan, 0).astype(int)
    energy = energy.set_index(['timestamp', 'id', 'name', 'socket'])[0]
    df = energy.groupby(['timestamp', 'id', 'name']).sum() * yappi_methods
    df = df.groupby(['timestamp', 'id', 'name', 'stack_trace']).sum().sort_values(ascending=False)

    return df

def populate_footprint(idx, energy):
    footprint = EnergyFootprint()
    footprint.timestamp = int(10 ** 3 * idx[0].timestamp())
    footprint.thread_id = idx[1]
    footprint.thread_name = idx[2]
    footprint.energy = energy
    for method in idx[3].split(';'):
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

    footprints = EnergyFootprints()
    for idx, s in energy.iteritems():
        footprints.footprint.add().CopyFrom(populate_footprint(idx, s))

    return footprints
