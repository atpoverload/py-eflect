""" Methods that sample rapl data.

This module manages a pyRAPL Measurement to be sampled periodically.
"""

import pyRAPL

from eflect.data.util import get_unixtime
from eflect.proto.rapl_pb2 import RaplSample

MEASUREMENT = None

# TODO(timur): the internal management of pyRAPL instead of directly reading
#   the register is annoying; we can try breaking into pyRAPL's Sensor so
#   we can directly get the energy
def get_rapl_result():
    """ Returns a rapl result. """
    global MEASUREMENT
    try:
        if MEASUREMENT is None:
            pyRAPL.setup()
            MEASUREMENT = pyRAPL.Measurement('bar')
            MEASUREMENT.begin()
        MEASUREMENT.end()
        energy = MEASUREMENT.result
        MEASUREMENT.begin()
    except:
        raise pyRAPL.PyRAPLException('rapl not available on this system')

    return energy

def sample_rapl():
    """ Returns RaplSamples for each socket. """
    data = []
    energy = get_rapl_result()
    for socket, (pkg, dram) in enumerate(zip(energy.pkg, energy.dram)):
        if pkg == 0 or dram == 0:
            continue

        # TODO(timur): i made this millijoules but we actually will want joules eventually
        sample = RaplSample()
        sample.timestamp = get_unixtime(energy.timestamp)
        sample.socket = socket
        sample.cpu = 0
        sample.dram = dram / 10 ** 3
        sample.package = pkg / 10 ** 3
        sample.gpu = 0

        data.append(sample)

    return data
