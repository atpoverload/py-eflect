""" Methods that sample /proc/stat jiffies data.

Refer to https://man7.org/linux/man-pages/man5/proc.5.html for details about
the proc system and jiffies.
"""

import os

from eflect.data.util import get_unixtime
from eflect.proto.proc_stat_pb2 import ProcStatSample

PROC_STAT = os.path.join('/proc', 'stat')

def sample_proc_stat():
    """ Returns ProcStatSamples for each cpu. """
    data = []
    timestamp = get_unixtime()
    with open(PROC_STAT) as f:
        f.readline()
        for cpu in range(os.cpu_count()):
            stat = list(map(int, f.readline().replace(os.linesep, '').split(' ')[1:]))
            sample = ProcStatSample()
            sample.timestamp = timestamp
            sample.cpu = cpu
            sample.user = stat[0]
            sample.nice = stat[1]
            sample.system = stat[2]
            sample.idle = stat[3]
            sample.iowait = stat[4]
            sample.irq = stat[5]
            sample.softirq = stat[6]
            sample.steal = stat[7]
            sample.guest = stat[8]
            sample.guest_nice = stat[9]

            data.append(sample)
    return data
