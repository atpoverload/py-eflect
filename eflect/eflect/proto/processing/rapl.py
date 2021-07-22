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
    return df
