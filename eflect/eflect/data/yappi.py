""" Methods that handle yappi data. """
import pandas as pd
import yappi

# def parse_yappi_data(data, threads):
#     """ Extracts all traces from yappi and puts it into a DataFrame. """
#     df = []
#     for thread in data:
#         for trace in yappi.get_func_stats(ctx_id=thread.id):
#             # grabs tsub from yappi YStats
#             df.append((threads[thread.tid], trace[7], trace[15]))
#     df = pd.DataFrame(df)
#     df.columns = ['id', 'calls', 'method']
#
#     return df.set_index(['id', 'method'])

def parse_yappi_data(data):
    """ Extracts all traces from yappi and puts it into a DataFrame. """
    df = pd.DataFrame(data)
    df.columns = ['timestamp', 'id', 'calls', 'method']
    print(df.sort_values(by = ['calls']).tail(50))

    return df.set_index(['timestamp', 'id', 'method'])
