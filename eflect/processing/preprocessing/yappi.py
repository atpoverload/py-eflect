""" Processing for yappi csv data. """

import pandas as pd

from eflect.processing.preprocessing.util import bucket_timestamps

def parse_yappi(yappi_stack_trace):
    """ Converts a collection of ProcStatSamples to a DataFrame. """
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

    df = df.groupby(['timestamp', 'id', 'stack_trace']).sum()
    df = df / df.groupby(['timestamp', 'id']).sum()

    return df.call_count

def yappi_to_df(data):
    """ Converts a collection of ProcStatSamples to a processed DataFrame. """
    return process_yappi_data(parse_yappi(data))
