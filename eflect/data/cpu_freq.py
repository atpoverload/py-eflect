""" Methods that sample the cpu frequencies. """

import os

from eflect.data.util import get_unixtime
from eflect.proto.cpu_freq_pb2 import CpuFreqSample

CPU_FREQ = os.path.sep.join(['/sys', 'devices', 'system', 'cpu'])
CPU_FREQ_DATA = os.path.sep.join(['cpufreq', 'cpuinfo_cur_freq'])

def sample_cpu_freq():
    """ Returns CpuFreqSamples for each cpu. """
    data = []
    timestamp = get_unixtime()
    for cpu in range(os.cpu_count()):
        with open(os.path.sep.join([CPU_FREQ, 'cpu' + str(cpu), CPU_FREQ_DATA])) as f:
            sample = CpuFreqSample()
            sample.timestamp = timestamp
            sample.cpu = cpu
            sample.freq = int(f.readline())
            data.append(sample)
    return data
