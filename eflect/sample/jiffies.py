""" Methods that sample /proc/stat jiffies data.

Refer to https://man7.org/linux/man-pages/man5/proc.5.html for details about
the proc system and jiffies.
"""

import os

from eflect.util import get_unixtime

PROC_STAT = os.path.join('/proc', 'stat')

def parse_cpu_stat(cpu, stats):
    """ Returns a CpuStat for the given stat. """
    return list(map(int, [cpu] + stats.replace(os.linesep, '').split(' ')[1:]))

def sample_cpus():
    """ Returns a CpuSample for each cpu. """
    sample = []
    timestamp = get_unixtime()
    with open(PROC_STAT) as f:
        # throw away the first line, which is the sum of all cpus; we want by cpu
        f.readline()
        for cpu in range(os.cpu_count()):
            sample.append(parse_cpu_stat(cpu, f.readline()))
    return ['cpu', timestamp, sample]

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

    return [
        int(stats[0]),
        " ".join(stats[1:offset])[1:-1],
        int(stats[38 + offset - 2]),
        int(stats[13 + offset - 2]),
        int(stats[14 + offset - 2])
    ]

def sample_tasks(pid):
    """ Returns a TaskSample for all tasks of pid. """
    sample = []
    timestamp = get_unixtime()
    for task in get_tasks(pid):
        try:
            with open(get_task_stat_file(pid, task)) as f:
                sample.append((parse_task_stat(f.readline())))
        except:
            print('process ' + task + ' terminated before being sampled!')
    return ['task', timestamp, sample]

def jiffies_sources():
    return [
        {'sample_func': sample_cpus},
        {
            'sample_func': sample_tasks,
            'sample_args': os.getpid()
        }
    ]
