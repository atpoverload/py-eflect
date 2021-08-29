""" Processing for /proc/[pid]/task/[tid]/stat csv data using pandas. """

import pandas as pd

from eflect.processing.preprocessing.util import bucket_timestamps
from eflect.processing.preprocessing.util import max_rolling_difference

def parse_proc_task(proc_task):
    """ Converts a collection of ProcTaskSamples to a DataFrame. """
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

def task_to_df(data):
    """ Converts a collection of ProcTaskSamples to a processed DataFrame. """
    return process_proc_task_data(parse_proc_task(data))
