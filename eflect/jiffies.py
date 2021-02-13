import os

from multiprocessing import cpu_count
from time import time

CPU_COUNT = cpu_count()
PROC_STAT = os.path.join('/proc', 'stat')

def current_tasks():
    return os.listdir(os.path.join('/proc', str(os.getpid()), 'task'))

def task_stat(task):
    return os.path.join(
        '/proc',
        str(os.getpid()),
        'task',
        str(task),
        'stat'
    )

def read_tasks():
    l = []
    for task in current_tasks():
        with open(task_stat(task)) as f:
            l.append(f.read())
    return (time(), l)

def read_cpu():
    l = []
    with open(PROC_STAT) as f:
        f.readline()
        for _ in range(CPU_COUNT):
            l.append(f.readline())
    return (time(), l)
