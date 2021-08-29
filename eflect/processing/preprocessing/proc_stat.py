""" Processing for /proc/stat data using pandas. """

import pandas as pd

from eflect.processing.preprocessing.util import bucket_timestamps
from eflect.processing.preprocessing.util import max_rolling_difference

def parse_proc_stat(proc_stat):
    """ Converts a collection of ProcStatSamples to a DataFrame. """
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

def process_proc_stat_data(df):
    """ Computes the cpu jiffy rate of each 50ms bucket """
    df['jiffies'] = df.drop(columns = ['timestamp', 'cpu', 'idle', 'iowait']).sum(axis = 1)
    df.timestamp = bucket_timestamps(df.timestamp)

    jiffies, ts = max_rolling_difference(df.groupby(['timestamp', 'cpu']).jiffies.min().unstack())
    jiffies = jiffies.stack().reset_index()
    jiffies = jiffies.groupby(['timestamp', 'cpu']).sum().unstack()
    jiffies = jiffies.div(ts, axis = 0).stack()

    return jiffies[0]

def stat_to_df(data):
    """ Converts a collection of ProcStatSamples to a processed DataFrame. """
    return process_proc_stat_data(parse_proc_stat(data))
