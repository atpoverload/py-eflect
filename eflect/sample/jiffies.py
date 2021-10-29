""" Methods that sample /proc/stat jiffies data.

Refer to https://man7.org/linux/man-pages/man5/proc.5.html for details about
the proc system and jiffies.
"""

import os

from eflect.util import get_unixtime
from eflect.protos.sample.jiffies_pb2 import CpuSample, TaskSample

PROC_STAT = os.path.join('/proc', 'stat')

def parse_cpu_stat(cpu, stats):
    """ Returns a CpuStat for the given stat. """
    stats = list(map(int, stats.replace(os.linesep, '').split(' ')[1:]))

    stat = CpuSample.CpuStat()
    stat.cpu = cpu
    stat.user = stats[0]
    stat.nice = stats[1]
    stat.system = stats[2]
    stat.idle = stats[3]
    stat.iowait = stats[4]
    stat.irq = stats[5]
    stat.softirq = stats[6]
    stat.steal = stats[7]
    stat.guest = stats[8]
    stat.guest_nice = stats[9]

    return stat

def sample_cpus():
    """ Returns a CpuSample for each cpu. """
    sample = CpuSample()
    sample.timestamp = get_unixtime()
    with open(PROC_STAT) as f:
        # throw away the first line, which is the sum of all cpus; we want by cpu
        f.readline()
        for cpu in range(os.cpu_count()):
            sample.stats.add().CopyFrom(parse_cpu_stat(cpu, f.readline()))
    return sample

def get_tasks(pid):
    """ Returns pid's current tasks. """
    return os.listdir(os.path.join('/proc', str(pid), 'task'))

def get_task_stat_file(pid, tid):
    """ Returns the stat for a task. """
    return os.path.join('/proc', str(pid), 'task', str(tid), 'stat')

def parse_task_stat(stat):
    """ Returns a TaskStat for the given stat. """
    stats = stat.split(' ')
    offset = len(stats) - 52 + 2

    stat = TaskSample.TaskStat()
    stat.thread_id = int(stats[0])
    # we don't need this right now
    # stat.thread_name = " ".join(stats[1:offset])[1:-1]
    stat.cpu = int(stats[38 + offset - 2])
    stat.user = int(stats[13 + offset - 2])
    stat.system = int(stats[14 + offset - 2])

    return stat

def sample_tasks(pid):
    """ Returns a TaskSample for all tasks of pid. """
    sample = TaskSample()
    sample.timestamp = get_unixtime()
    for task in get_tasks(pid):
        try:
            with open(get_task_stat_file(pid, task)) as f:
                sample.stats.add().CopyFrom(parse_task_stat(f.readline()))
        except:
            print('process ' + task + ' terminated before being sampled!')
    return sample

def jiffies_sources():
    return [
        {'sample_func': sample_cpus},
        {
            'sample_func': sample_tasks,
            'sample_args': os.getpid()
        }
    ]
