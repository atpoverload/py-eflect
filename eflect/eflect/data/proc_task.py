""" Methods that sample /proc/[pid]/task/[tid]/stat jiffies data.

Refer to https://man7.org/linux/man-pages/man5/proc.5.html for details about
the proc system and jiffies.
"""

import os

from time import time

from eflect.data.util import get_unixtime
from eflect.proto.proc_task_pb2 import ProcTaskSample

def get_tasks(pid):
    """ Returns pid's current tasks """
    return os.listdir(os.path.join('/proc', str(pid), 'task'))

def get_task_stat_file(pid, tid):
    """ Returns the stat for a task """
    return os.path.join('/proc', str(pid), 'task', str(tid), 'stat')

def parse_task_stat(timestamp, stat):
    """ Returns a ProcTaskSample for the given stat """
    stats = stat.split(' ')
    offset = len(stats) - 52 + 2

    sample = ProcTaskSample()
    sample.timestamp = timestamp
    sample.thread_id = int(stats[0])
    sample.thread_name = " ".join(stats[1:offset])[1:-1]
    sample.cpu = int(stats[38])
    sample.user = int(stats[13])
    sample.system = int(stats[14])

    return sample

def sample_proc_task(pid=None):
    """ Returns the ProcTaskSamples for all tasks of pid """
    if pid is None:
        pid = os.getpid()
    data = []
    timestamp = get_unixtime()
    for task in get_tasks(pid):
        try:
            with open(get_task_stat_file(pid, task)) as f:
                data.append(parse_task_stat(timestamp, f.readline()))
        except:
            print('process ' + task + ' terminated before being sampled!')
    return data
