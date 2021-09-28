""" Methods that sample rapl data.

This module manages a pyRAPL Measurement to be sampled periodically.
"""

import pyRAPL

from eflect.util import get_unixtime
from eflect.sample.protos.rapl_pb2 import RaplSample

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
    sample = RaplSample()
    sample.timestamp = get_unixtime()
    energy = get_rapl_result()
    for socket, (pkg, dram) in enumerate(zip(energy.pkg, energy.dram)):
        # if there's no reading here, it's probably garbage
        if pkg == 0 or dram == 0:
            continue

        reading = RaplSample()
        reading.socket = socket
        reading.cpu = 0
        reading.dram = dram / 10 ** 3
        reading.package = pkg / 10 ** 3
        reading.gpu = 0

        sample.readings.add().CopyFrom(reading)
    return sample

def rapl_sources():
    return [{'sample_func': sample_rapl}]

COUNTER = 0

def sample_fake_rapl():
    global COUNTER
    COUNTER += 1

    sample = RaplSample()
    sample.timestamp = get_unixtime()

    reading = RaplSample.RaplReading()
    reading.socket = 0
    reading.cpu = COUNTER
    reading.dram = COUNTER
    reading.package = COUNTER
    reading.gpu = COUNTER
    sample.readings.add().CopyFrom(reading)

    return sample
