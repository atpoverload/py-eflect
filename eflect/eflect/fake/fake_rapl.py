""" Methods that produce fake rapl data. """

import pyRAPL

from eflect.data.util import get_unixtime
from eflect.proto.rapl_pb2 import RaplSample

def sample_fake_rapl():
    """ Returns a RaplSample that uses a fake counter for values. """
    global COUNTER
    sample = RaplSample()
    sample.timestamp = get_unixtime()
    sample.socket = 0
    sample.cpu = 1
    sample.dram = 1
    sample.package = 1
    sample.gpu = 1

    return [sample]
