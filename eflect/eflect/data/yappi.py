""" Methods that handle yappi data. """
import pandas as pd
import yappi

def parse_yappi_data(data):
    """ Extracts all traces from yappi and puts it into a DataFrame. """
    df = pd.DataFrame([[ts, id, trace[3], trace[7], trace[15]] for ts, id, trace in data])
    df.columns = ['timestamp', 'id', 'calls', 'tsub', 'method']
    
    return df.set_index(['timestamp', 'id', 'method'])
