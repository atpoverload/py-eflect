""" Parses ProcTaskSamples to csv records. """

import pandas as pd

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
