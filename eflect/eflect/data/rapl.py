import pandas as pd
import pyRAPL

MEASUREMENT = None

def sample_rapl():
    global MEASUREMENT
    if MEASUREMENT is None:
        pyRAPL.setup()
        MEASUREMENT = pyRAPL.Measurement('bar')
        MEASUREMENT.begin()
    MEASUREMENT.end()
    energy = MEASUREMENT.result
    MEASUREMENT.begin()
    return energy

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
