from eflect.processing.preprocessing import bucket_timestamps, max_rolling_difference

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
