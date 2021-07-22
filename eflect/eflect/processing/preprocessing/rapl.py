""" Processing for rapl csv data. """

from eflect.processing.preprocessing import bucket_timestamps, max_rolling_difference

WRAP_AROUND_VALUE = 16384

def check_wrap_around(value):
    if value < 0:
        return value + WRAP_AROUND_VALUE
    else:
        return value

def process_rapl_data(df):
    """ Computes the power of each 50ms bucket """
    df.timestamp = bucket_timestamps(df.timestamp)
    df = df.groupby(['timestamp', 'socket']).min()
    df.columns.name = 'component'

    energy, ts = max_rolling_difference(df.unstack())
    energy = energy.stack().stack().apply(check_wrap_around)
    energy = energy.groupby(['timestamp', 'socket']).sum().unstack().div(ts, axis = 0).stack()

    return energy
