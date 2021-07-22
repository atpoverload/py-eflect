""" Methods that produce fake rapl data. """

import pyRAPL

from eflect.data.util import get_unixtime
from eflect.proto.rapl_pb2 import RaplSample

COUNTER = 0

def sample_fake_rapl():
    """ Returns a RaplSample that uses a fake counter for values. """
    global COUNTER
    sample = RaplSample()
    sample.timestamp = get_unixtime()
    sample.socket = 0
    sample.cpu = COUNTER
    sample.dram = COUNTER
    sample.package = COUNTER
    sample.gpu = COUNTER

    COUNTER += 1

    return [sample]
