""" A copy of eflect that uses a fake rapl source. """

import os

from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pipe
from time import sleep, time

from eflect.sample.sample_storage import SampleStorage

# default of 50ms
DEFAULT_PERIOD = 0.050

from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pipe
from time import sleep, time

# this should be a submit() chain so we can stop with shutdown()
def periodic_sample(period, pipe, sample_func, **kwargs):
    """ Collects data from a source periodically """
    data = []
    while not pipe.poll():
        start = time()
        if 'sample_args' in kwargs:
            data.append(sample_func(kwargs['sample_args']))
        else:
            data.append(sample_func())
        sleep(max(0, period - (time() - start)))
    return data

class Sampler:
    def __init__(self, sources, period=DEFAULT_PERIOD):
        self.running = False
        self.sources = sources
        self.period = period

    def start(self):
        """ Starts data collection """
        if not self.running:
            self.running = True
            self.executor = ProcessPoolExecutor(len(self.sources))

            self.parent_pipe, self.child_pipe = Pipe()
            self.data_futures = [
                self.executor.submit(
                    periodic_sample,
                    self.period,
                    self.child_pipe,
                    **source
                ) for source in self.sources
            ]

    def stop(self):
        """ Stops data collection """
        if self.running:
            self.running = False

            self.parent_pipe.send(1)
            self.storage = SampleStorage()
            for future in self.data_futures:
                list(map(self.storage.add, future.result()))
            self.child_pipe.recv()
            self.executor.shutdown()
            self.executor = None

    def read(self):
        """ Returns the stored data """
        return self.storage.read()
