""" A data collector for eflect. """

import os

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Pipe
from time import sleep, time

import yappi

from eflect.data import SampleStorage
# TODO(timur): it would be nice to import a collection of "sources" instead
from eflect.data import sample_cpu_freq
from eflect.data import sample_proc_stat
from eflect.data import sample_proc_task
from eflect.data import sample_rapl
from eflect.data import sample_yappi
from eflect.proto.data_set_pb2 import EflectDataSet

# used to sync with ProcessPoolExecutor
PARENT_PIPE, CHILD_PIPE = Pipe()
DEFAULT_PERIOD_MS = 0.050

# TODO(timur): should there be some sort of collector? currently we have to
# pass the pipe around, which isn't ideal
# TODO(timur): this doesn't reschedule, so the thread/process isn't shared
def periodic_sample(sample_func, **kwargs):
    """ Collects data from a source periodically """
    data = []
    while not CHILD_PIPE.poll():
        start = time()
        if 'sample_args' in kwargs:
            data.extend(sample_func(kwargs['sample_args']))
        else:
            data.extend(sample_func())
        sleep(max(0, DEFAULT_PERIOD_MS - (time() - start)))
    return data

class Eflect:
    def __init__(self, period=DEFAULT_PERIOD_MS):
        self.period = period
        self.running = False

    def start(self, pid=None):
        """ Starts data collection """
        if not self.running:
            self.running = True

            self.executor = ProcessPoolExecutor(4)
            self.data_futures = []

            # jiffies
            self.data_futures.append(self.executor.submit(
                periodic_sample,
                sample_proc_stat
            ))
            self.data_futures.append(self.executor.submit(
                periodic_sample,
                sample_proc_task,
                sample_args=os.getpid() if pid is None else pid
            ))

            # energy
            self.data_futures.append(self.executor.submit(
                periodic_sample,
                sample_rapl
            ))

            # yappi
            self.yappi_executor = ThreadPoolExecutor(1)
            yappi.start()
            self.data_futures.append(self.yappi_executor.submit(self.__periodic_sample_yappi))

            # freqs
            self.data_futures.append(self.executor.submit(
                periodic_sample,
                sample_cpu_freq
            ))

    def stop(self):
        """ Stops data collection """
        if self.running:
            self.running = False

            PARENT_PIPE.send(1)
            self.executor.shutdown()
            self.yappi_executor.shutdown()
            CHILD_PIPE.recv()
            yappi.stop()

            self.storage = SampleStorage()
            for future in self.data_futures:
                list(map(self.storage.add, future.result()))

    def read(self):
        """ Returns the stored data """
        return self.storage.process()

    def __periodic_sample_yappi(self):
        """ Samples yappi every 1s """
        data = []
        while self.running:
            start = time()
            yappi.stop()
            data.extend(sample_yappi())
            yappi.start()
            sleep(max(0, 1 - (time() - start)))

        return data

def profile(workload, period=DEFAULT_PERIOD_MS):
    """ Returns a EflectDataSet of the workload """
    eflect = Eflect(period=period)
    eflect.start()

    workload()

    eflect.stop()
    return eflect.read()

def load_data_set(data_set_path):
    """ Loads an EflectDataSet from the path. """
    with open(data_set_path, 'rb') as f:
        data_set = EflectDataSet()
        data_set.ParseFromString(f.read())
        return data_set
