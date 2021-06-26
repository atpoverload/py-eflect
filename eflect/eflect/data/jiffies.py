""" Methods that handle jiffies data.

Refer to https://man7.org/linux/man-pages/man5/proc.5.html for details about
the proc system and jiffies.
"""
import os

from time import time

import pandas as pd

CPU_HEADER = [
    'user',
    'nice',
    'system',
    'idle',
    'iowait',
    'irq',
    'softirq',
    'steal',
    'guest',
    'guest_nice'
]
PROC_STAT = os.path.join('/proc', 'stat')

def get_tasks(pid):
    """ Returns pid's current tasks """
    return os.listdir(os.path.join('/proc', str(pid), 'task'))

def get_task_stat_file(pid, tid):
    """ Returns the stat for a task """
    return os.path.join('/proc', str(pid), 'task', str(tid), 'stat')

def parse_task_stat(stat):
    """ Returns a task's id, name, cpu, user jiffies, and system jiffies """
    stats = stat.split(' ')
    offset = len(stats) - 52 + 2
    name = " ".join(stats[1:offset])[1:-1]
    return int(stats[0]), name, stats[38], int(stats[13]), int(stats[14])

def sample_cpu():
    """ Returns the current time and by-cpu jiffies """
    cpus = []
    with open(PROC_STAT) as f:
        f.readline()
        for cpu in range(os.cpu_count()):
            cpus.append([cpu] + f.readline().replace(os.linesep, '').split(' ')[1:])
    return {'timestamp': time(), 'data': cpus}

def parse_cpu_data(data):
    """ Packs the contents of sample_cpu into a DataFrame """
    parsed_data = []
    for sample in data:
        df = pd.DataFrame.from_records(
            sample['data'],
            columns=['cpu'] + CPU_HEADER
        )
        df['timestamp'] = pd.to_datetime(sample['timestamp'], unit='s')
        parsed_data.append(df)

    return pd.concat(parsed_data).set_index(['timestamp', 'cpu'])[CPU_HEADER]

def sample_tasks(pid=None):
    """ Returns the current time and the stats for all tasks of pid """
    tasks = []
    for task in get_tasks(pid):
        try:
            with open(get_task_stat_file(pid, task)) as f:
                tasks.append(parse_task_stat(f.readline()))
        except:
            print('process ' + task + ' terminated before being sampled!')
    return {'timestamp': time(), 'data': tasks}

def parse_tasks_data(data):
    """ Packs the contents of sample_tasks into a DataFrame """
    parsed_data = []
    for sample in data:
        df = pd.DataFrame(
            data = sample['data'],
            columns = ['id', 'name', 'cpu', 'user', 'system']
        )
        df['timestamp'] = pd.to_datetime(sample['timestamp'], unit='s')
        parsed_data.append(df)

    return pd.concat(parsed_data).set_index(['timestamp', 'id', 'name'])[['cpu', 'user', 'system']]
