""" Processing for yappi csv data. """

from eflect.processing.preprocessing import bucket_timestamps

def process_yappi_data(df):
    """ Computes the method call rate of each 1s bucket """
    df.timestamp = bucket_timestamps(df.timestamp)

    df = df.groupby(['timestamp', 'id', 'stack_trace']).count()
    df = df / df.groupby(['timestamp', 'id']).sum()

    return df.duration
