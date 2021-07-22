""" Methods that sample rapl data.

This module manages a pyRAPL Measurement to be sampled periodically.
"""
# TODO: try to remove the internally managed pyRAPL so it looks better

import pyRAPL

from eflect.data.util import get_unixtime
from eflect.proto.rapl_pb2 import RaplSample

MEASUREMENT = None

def get_rapl_result():
    """ Returns a rapl result. """
    global MEASUREMENT
    if MEASUREMENT is None:
        pyRAPL.setup()
        MEASUREMENT = pyRAPL.Measurement('bar')
        MEASUREMENT.begin()
    MEASUREMENT.end()
    energy = MEASUREMENT.result
    MEASUREMENT.begin()

    return energy

def sample_rapl():
    """ Returns a RaplSample. """
    data = []
    energy = get_rapl_result()
    for socket, (pkg, dram) in enumerate(zip(energy.pkg, energy.dram)):
        sample = RaplSample()
        sample.timestamp = get_unixtime(energy.timestamp)
        sample.socket = socket
        sample.cpu = 0
        sample.dram = dram
        sample.package = pkg
        sample.gpu = 0

        data.append(sample)

    return data
