import pandas as pd

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
