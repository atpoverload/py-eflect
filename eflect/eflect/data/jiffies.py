import os

from time import time

import pandas as pd
import psutil

CPU_JIFFIES_HEADER = ['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest', 'guest_nice']
PROC_STAT = os.path.join('/proc', 'stat')

def get_task_stat_file(pid, tid):
    return os.path.join('/proc', str(pid), 'task', str(tid), 'stat')

def sample_cpu():
    cpus = []
    with open(PROC_STAT) as f:
        f.readline()
        for cpu in range(os.cpu_count()):
            cpus.append([cpu] + list(map(int, f.readline().split(' ')[1:])))

    return (time(), tuple(cpus))

    # return (time(), tuple([i] + list(t) for i, t in enumerate(psutil.cpu_times(percpu=True))))

def parse_cpu_data(data):
    parsed_data = []
    for sample in data:
        df = pd.DataFrame.from_records(sample[1], columns=['cpu'] + CPU_JIFFIES_HEADER)
        df['timestamp'] = pd.to_datetime(sample[0], unit='s')
        parsed_data.append(df)

    return pd.concat(parsed_data).set_index(['timestamp', 'cpu'])[CPU_JIFFIES_HEADER]

# TODO: figure out why I have to use direct implementation to read jiffies instead of psutil
def sample_tasks(pid=None):
    threads = []
    for thread in psutil.Process(pid).threads():
        try:
            with open(get_task_stat_file(pid, thread.id)) as f:
                stats = f.read().split(' ')
                offset = len(stats) - 52 + 2
                name = " ".join(stats[1:offset])[1:-1]
                threads.append((thread.id, name, stats[38], int(stats[13]), int(stats[14])))

            # p = psutil.Process(thread.id)
            # with p.oneshot():
            #     jiffies = p.cpu_times()
            #     threads.append((p.pid, p.name(), p.cpu_num(), jiffies.user, jiffies.system))
        except:
            print('process ' + str(thread.id) + ' terminated before being sampled!')
    return (time(), tuple(threads))

def parse_tasks_data(data):
    parsed_data = []
    for sample in data:
        df = pd.DataFrame(
            data = sample[1],
            columns = ['id', 'name', 'cpu', 'user', 'system']
        )
        df['timestamp'] = pd.to_datetime(sample[0], unit='s')
        parsed_data.append(df)

    return pd.concat(parsed_data).set_index(['timestamp', 'id', 'name'])[['cpu', 'user', 'system']]
