""" Processing for yappi csv data. """

import pandas as pd

from eflect.processing.preprocessing import bucket_timestamps

# TODO(timurbey): this needs to be updated with eflect/eflect/data/yappi.py
def parse_yappi(yappi_stack_trace):
    df = pd.DataFrame([[
        stack_trace.timestamp,
        stack_trace.thread_id,
        ';'.join(stack_trace.stack_trace),
        stack_trace.call_count
    ] for stack_trace in yappi_stack_trace])
    df.columns = ['timestamp', 'id', 'stack_trace', 'call_count']
    df.timestamp = pd.to_datetime(df.timestamp, unit='ms')
    return df

def process_yappi_data(df):
    """ Computes the method call rate of each 1s bucket """
    df.timestamp = bucket_timestamps(df.timestamp)

    # TODO(timurbey): this needs to be updated with eflect/eflect/data/yappi.py
    df = df.groupby(['timestamp', 'id', 'stack_trace']).sum()
    df = df / df.groupby(['timestamp', 'id']).sum()

    return df.call_count
