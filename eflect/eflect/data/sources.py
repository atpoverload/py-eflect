from time import time

import psutil
import pyRAPL
import yappi

MEASUREMENT = None

def sample_tasks(pid = None):
    threads = []
    for thread in psutil.Process(pid).threads():
        try:
            p = psutil.Process(thread.id)
            with p.oneshot():
                jiffies = p.cpu_times()
                threads.append((p.pid, p.name(), p.cpu_num(), jiffies.user, jiffies.system))
        except:
            print('process ' + str(thread.id) + ' terminated before being sampled!')
    return (time(), tuple(threads))

def sample_cpu():
    return (time(), tuple([i] + list(t) for i, t in enumerate(psutil.cpu_times(percpu=True))))

def sample_rapl():
    global MEASUREMENT
    if MEASUREMENT is None:
        pyRAPL.setup()
        MEASUREMENT = pyRAPL.Measurement('bar')
        MEASUREMENT.begin()
    MEASUREMENT.end()
    energy = MEASUREMENT.result
    MEASUREMENT.begin()
    return energy

def sample_yappi():
    yappi.stop()
    traces = []
    for thread in yappi.get_thread_stats():
        traces.append((thread.tid, yappi.get_func_stats(ctx_id=thread.id)))
    yappi.start()
    return (time(), traces)