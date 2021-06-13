import pandas as pd

CPU_JIFFIES_HEADER = ['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest', 'guest_nice']

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

def parse_cpu_data(data):
    parsed_data = []
    for sample in data:
        df = pd.DataFrame.from_records(sample[1], columns=['cpu'] + CPU_JIFFIES_HEADER)
        df['timestamp'] = pd.to_datetime(sample[0], unit='s')
        parsed_data.append(df)

    return pd.concat(parsed_data).set_index(['timestamp', 'cpu'])[CPU_JIFFIES_HEADER]

def parse_rapl_data(data):
    parsed_data = []
    for sample in data:
        df = pd.DataFrame(data = zip(sample.pkg, sample.dram))
        df /= 1000000
        df.index = ['dram', 'package']
        df.columns.name = 'domain'
        df = df.stack().unstack(0).reset_index()
        df['cpu'] = 0
        df['gpu'] = 0
        df['timestamp'] = pd.to_datetime(sample.timestamp, unit='s')
        parsed_data.append(df)

    # rapl reports the instaneous different already, so we just cumsum
    # here so the data shape is the same
    return pd.concat(parsed_data).set_index(['timestamp', 'domain'])[['dram', 'cpu', 'package', 'gpu']].unstack().cumsum().stack()

def parse_yappi_data(data):
    parsed_data = []
    for sample in data:
        df = []
        for thread, traces in sample[1]:
            for trace in traces:
                df.append([thread, trace[15]])
        df = pd.DataFrame(df)
        df.columns = ['id', 'trace']
        df['timestamp'] = pd.to_datetime(sample[0], unit='s')
        parsed_data.append(df)

    return pd.concat(parsed_data).set_index(['timestamp', 'id'])
