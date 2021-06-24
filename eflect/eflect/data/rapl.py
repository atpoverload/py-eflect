""" Methods that handle rapl data.

This module manages a pyRAPL Measurement to be sampled periodically.
"""

import pandas as pd
import pyRAPL

MEASUREMENT = None

def sample_rapl():
    """ Gets a reading from the measurement. """
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
    """ Stops the measurement and puts the pyRAPL output into a DataFrame. """
    if MEASUREMENT is not None:
        MEASUREMENT.end()
        MEASUREMENT = None
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

    # rapl reports the instaneous difference, so we need cumsum
    return pd.concat(parsed_data).set_index(['timestamp', 'domain'])[['dram', 'cpu', 'package', 'gpu']].unstack().cumsum().stack()
