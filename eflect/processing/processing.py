""" Methods that turn EflectDataSets into EflectFootprints. """

import os

from sys import argv

import numpy as np
import pandas as pd

from eflect.data.util import get_unixtime
from eflect.proto.footprint_pb2 import EflectFootprint, EflectFootprints
from eflect.processing.accounting import account_jiffies, account_rapl_energy, align_yappi_methods
from eflect.processing.preprocessing import parse_proc_stat
from eflect.processing.preprocessing import process_proc_stat_data
from eflect.processing.preprocessing import parse_proc_task
from eflect.processing.preprocessing import process_proc_task_data
from eflect.processing.preprocessing import parse_rapl
from eflect.processing.preprocessing import process_rapl_data
from eflect.processing.preprocessing import parse_yappi
from eflect.processing.preprocessing import process_yappi_data

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

def load_data(data_set_path):
    """ Loads a EflectDataSet from the path """
    with open(data_set_path, 'rb') as f:
        data_set = EflectDataSet()
        data_set.ParseFromString(f.read())
        return data_set

def compute_footprint(data):
    activity = account_jiffies(
        process_proc_task_data(parse_proc_task(data.proc_task)),
        process_proc_stat_data(parse_proc_stat(data.proc_stat))
    ).dropna()

    energy = account_rapl_energy(
        process_rapl_data(parse_rapl(data.rapl)),
        activity
    )

    energy = align_yappi_methods(
        energy,
        process_yappi_data(parse_yappi(data.yappi_stack_trace)),
    )

    footprints = EflectFootprints()
    for idx, s in energy.iteritems():
        footprints.footprint.add().CopyFrom(populate_footprint(idx, s))

    return footprints
