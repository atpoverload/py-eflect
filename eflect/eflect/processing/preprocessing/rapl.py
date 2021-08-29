""" Processing for rapl csv data. """

import pandas as pd

from eflect.processing.preprocessing import bucket_timestamps, max_rolling_difference

WRAP_AROUND_VALUE = 16384

def parse_rapl(rapl):
    df = pd.DataFrame([[
        sample.timestamp,
        sample.socket,
        sample.cpu,
        sample.package,
        sample.dram,
        sample.gpu
    ] for sample in rapl])
    df.columns = [
        'timestamp',
        'socket',
        'cpu',
        'package',
        'dram',
        'gpu'
    ]
    df.timestamp = pd.to_datetime(df.timestamp, unit='ms')
    df[['cpu', 'package', 'dram', 'gpu']] /= 10 ** 3
    return df

def check_wrap_around(value):
    if value < 0:
        return value + WRAP_AROUND_VALUE
    else:
        return value

def process_rapl_data(df):
    """ Computes the power of each 50ms bucket """
    df.timestamp = bucket_timestamps(df.timestamp)
    df = df.groupby(['timestamp', 'socket']).min()
    df.columns.name = 'component'

    energy, ts = max_rolling_difference(df.unstack())
    energy = energy.stack().stack().apply(check_wrap_around)
    energy = energy.groupby(['timestamp', 'socket', 'component']).sum().div(ts, axis = 0)

    return energy
