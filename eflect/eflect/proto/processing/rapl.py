""" Parses RaplSamples to csv records. """

import pandas as pd

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
