""" A copy of eflect that uses a fake rapl source. """

import os

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Pipe
from time import sleep, time

import yappi

from eflect.data import SampleStorage
from eflect.data import sample_proc_stat
from eflect.data import sample_proc_task
from eflect.fake import sample_fake_rapl
from eflect.data import sample_yappi
from eflect.proto.data_set_pb2 import EflectDataSet

# used to sync with ProcessPoolExecutor
PARENT_PIPE, CHILD_PIPE = Pipe()
# default of 50ms
DEFAULT_PERIOD = 0.050

# this should be a submit() chain so we can stop with shutdown()
def periodic_sample(sample_func, **kwargs):
    """ Collects data from a source periodically """
    data = []
    while not CHILD_PIPE.poll():
        start = time()
        if 'sample_args' in kwargs:
            data.extend(sample_func(kwargs['sample_args']))
        else:
            data.extend(sample_func())
        sleep(max(0, DEFAULT_PERIOD - (time() - start)))
    return data

class Eflect:
    def __init__(self, period=DEFAULT_PERIOD):
        self.period = period
        self.running = False

    def start(self):
        """ Starts data collection """
        if not self.running:
            self.running = True

            self.executor = ProcessPoolExecutor(3)
            self.data_futures = []

            # jiffies
            self.data_futures.append(self.executor.submit(
                periodic_sample,
                sample_proc_stat
            ))
            self.data_futures.append(self.executor.submit(
                periodic_sample,
                sample_proc_task,
                sample_args=os.getpid()
            ))

            # energy
            self.data_futures.append(self.executor.submit(
                periodic_sample,
                sample_fake_rapl
            ))

            # yappi
            self.yappi_executor = ThreadPoolExecutor(1)
            yappi.start()
            self.data_futures.append(self.yappi_executor.submit(self.__periodic_sample_yappi))

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

def profile(workload, period=DEFAULT_PERIOD):
    """ Returns a EflectDataSet of the workload """
    eflect = Eflect(period=period)
    eflect.start()

    workload()

    eflect.stop()
    return eflect.read()
