import os
import threading

from time import time

import psutil
import pyRAPL
import yappi

MEASUREMENT = None

# TODO: figure out why I have to use direct implementation to read jiffies instead of psutil

def sample_tasks(pid=None):
    threads = []
    for thread in psutil.Process(pid).threads():
        try:
            with open(os.path.join('/proc', str(pid), 'task', str(thread.id), 'stat')) as f:
                stats = f.read().split(' ')
                offset = len(stats) - 52 + 2
                name = " ".join(stats[1:offset])[1:-1]
                threads.append((thread.id, name, stats[38], int(stats[13]), int(stats[14])))

            # p = psutil.Process(thread.id)
            # with p.oneshot():
            #     jiffies = p.cpu_times()
            #     threads.append((p.pid, p.name(), p.cpu_num(), jiffies.user, jiffies.system))
        except:
            print('process ' + str(thread.id) + ' terminated before being sampled!')
    return (time(), tuple(threads))

def sample_cpu():
    cpus = []
    with open(os.path.join('/proc', 'stat')) as f:
        f.readline()
        for cpu in range(os.cpu_count()):
            cpus.append([cpu] + list(map(int, f.readline().split(' ')[1:])))
    return (time(), tuple(cpus))

    # return (time(), tuple([i] + list(t) for i, t in enumerate(psutil.cpu_times(percpu=True))))

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
    threads = {thread.ident: thread.native_id for thread in threading.enumerate() if thread.native_id != threading.get_native_id()}
    for thread in yappi.get_thread_stats():
        if thread.tid not in threads:
            continue
        traces.append((threads[thread.tid], yappi.get_func_stats(ctx_id=thread.id)))
    yappi.start()
    return (time(), traces)
