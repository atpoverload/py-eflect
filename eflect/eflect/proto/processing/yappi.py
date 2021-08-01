""" Parses YappiSamples to csv records. """

import pandas as pd

# TODO(timurbey): this needs to be updated with eflect/eflect/data/yappi.py
def parse_yappi(yappi_stack_trace):
    df = pd.DataFrame([[
        stack_trace.timestamp,
        stack_trace.thread_id,
        ';'.join(stack_trace.stack_trace),
        stack_trace.duration
    ] for stack_trace in yappi_stack_trace])
    df.columns = ['timestamp', 'id', 'stack_trace', 'duration']
    df.timestamp = pd.to_datetime(df.timestamp, unit='ms')
    return df
