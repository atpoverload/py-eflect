""" Processing for /proc/stat and /proc/[pid]/task/[tid]/stat csv data. """

import pandas as pd

from eflect.processing.preprocessing import bucket_timestamps, max_rolling_difference

def parse_proc_stat(proc_stat):
    df = pd.DataFrame([[
        sample.timestamp,
        sample.cpu,
        sample.user,
        sample.nice,
        sample.system,
        sample.idle,
        sample.iowait,
        sample.irq,
        sample.softirq,
        sample.steal,
        sample.guest,
        sample.guest_nice
    ] for sample in proc_stat])
    df.columns = [
        'timestamp',
        'cpu',
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
    df.timestamp = pd.to_datetime(df.timestamp, unit='ms')
    return df

def parse_proc_task(proc_task):
    df = pd.DataFrame([[
        sample.timestamp,
        sample.thread_id,
        sample.thread_name,
        sample.cpu,
        sample.user,
        sample.system
    ] for sample in proc_task])
    df.columns = [
        'timestamp',
        'id',
        'name',
        'cpu',
        'user',
        'system',
    ]
    df.timestamp = pd.to_datetime(df.timestamp, unit='ms')
    return df

def process_proc_stat_data(df):
    """ Computes the cpu jiffy rate of each 50ms bucket """
    df['jiffies'] = df.drop(columns = ['timestamp', 'cpu', 'idle', 'iowait']).sum(axis = 1)
    df.timestamp = bucket_timestamps(df.timestamp)

    jiffies, ts = max_rolling_difference(df.groupby(['timestamp', 'cpu']).jiffies.min().unstack())
    jiffies = jiffies.stack().reset_index()
    jiffies = jiffies.groupby(['timestamp', 'cpu']).sum().unstack()
    jiffies = jiffies.div(ts, axis = 0).stack()

    return jiffies[0]

def process_proc_task_data(df):
    """ Computes the app jiffy rate of each 50ms bucket """
    df['jiffies'] = df.user + df.system
    df = df[~df.name.str.contains('eflect-')]

    df.timestamp = bucket_timestamps(df.timestamp)
    df['id'] = df.id.astype(str) + '-' + df.name
    cpu = df.groupby(['timestamp', 'id']).cpu.max()

    jiffies, ts = max_rolling_difference(df.groupby(['timestamp', 'id']).jiffies.min().unstack())
    jiffies = jiffies.stack().to_frame()
    jiffies['cpu'] = cpu
    jiffies = jiffies.groupby(['timestamp', 'id', 'cpu'])[0].sum().unstack().unstack().div(ts, axis = 0).stack().stack(0)

    return jiffies
