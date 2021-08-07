""" Methods that sample yappi data. """

import threading

from time import time

import yappi

from eflect.data.util import get_unixtime
from eflect.proto.yappi_pb2 import YappiSample

def sample_yappi():
    """ Returns YappiSamples for each thread's traces including children """
    timestamp = get_unixtime()
    data = []
    threads = {thread.ident: thread.native_id for thread in threading.enumerate()}
    for thread in yappi.get_thread_stats():
        if thread.tid not in threads.keys() or thread.tid == threading.current_thread().ident:
            continue
        for trace in yappi.get_func_stats(ctx_id=thread.id):
            # TODO(timurbey): i'm not getting a meaningful number from tsub
            # with the sampled slices; we have calls but i'm not a fan of them
            # TODO(timurbey): this needs to be updated with eflect/eflect/data/yappi.py
            if len(trace[9]) > 0:
                for child_trace in trace[9]:
                    sample = YappiSample()
                    sample.timestamp = timestamp
                    sample.call_count = child_trace[1]
                    sample.thread_id = threads[thread.tid]
                    sample.stack_trace.append(child_trace[7])
                    sample.stack_trace.append(trace[15])

                    data.append(sample)
            else:
                sample = YappiSample()
                sample.timestamp = timestamp
                sample.call_count = trace[3]
                sample.thread_id = threads[thread.tid]
                sample.stack_trace.append(trace[15])

                data.append(sample)
    return data
