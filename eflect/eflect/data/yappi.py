import threading

import pandas as pd
import yappi

def parse_yappi_data(data, threads):
    df = []
    for thread in data:
        for trace in yappi.get_func_stats(ctx_id=thread.id):
            df.append((threads[thread.tid], trace[15]))
    df = pd.DataFrame(df)

    return df
