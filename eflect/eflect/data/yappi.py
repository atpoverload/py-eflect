""" Methods that handle yappi data. """
import pandas as pd
import yappi

def parse_yappi_data(data, threads):
    """ Extracts all traces from the yappi and puts it into a DataFrame. """
    df = []
    for thread in data:
        for trace in yappi.get_func_stats(ctx_id=thread.id):
            df.append((threads[thread.tid], trace[15]))
    df = pd.DataFrame(df)

    return df
