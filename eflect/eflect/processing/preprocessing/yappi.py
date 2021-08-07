""" Processing for yappi csv data. """

from eflect.processing.preprocessing import bucket_timestamps

def process_yappi_data(df):
    """ Computes the method call rate of each 1s bucket """
    df.timestamp = bucket_timestamps(df.timestamp)

    # TODO(timurbey): this needs to be updated with eflect/eflect/data/yappi.py
    df = df.groupby(['timestamp', 'id', 'stack_trace']).sum()
    df = df / df.groupby(['timestamp', 'id']).sum()

    return df.duration
