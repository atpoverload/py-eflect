""" A data collector that collects data needed for eflect """
import os
import subprocess
import threading

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Pipe
from subprocess import Popen
from time import sleep, time

import psutil
import yappi

from eflect.data.jiffies import sample_cpu, parse_cpu_data, sample_tasks, parse_tasks_data
from eflect.data.rapl import sample_rapl, parse_rapl_data
from eflect.data.yappi import parse_yappi_data
from eflect.processing import account_energy

PARENT_PIPE, CHILD_PIPE = Pipe()
PERIOD = 0.050

# this should be a submit() chain so we can stop with shutdown()
def periodic_sample(sample_func, parse_func, **kwargs):
    """ Collects data from a source periodically and writes it to a file """
    data = []
    while not CHILD_PIPE.poll():
        start = time()
        data.append(sample_func(*kwargs['sample_args']))
        if 'period' in kwargs:
            sleep(max(0, kwargs['period'] - (time() - start)))
        else:
            sleep(max(0, PERIOD - (time() - start)))
    parse_func(data).to_csv(kwargs['output_file'], header = False)

class Eflect:
    def __init__(self, period=50, output_dir=None):
        self.period = period / 1000
        if output_dir is None:
            self.output_dir = os.getcwd()
        else:
            self.output_dir = output_dir
        self.running = False

    def start(self):
        """ Starts data collection """
        if not self.running:
            self.running = True

            if not os.path.exists(self.output_dir):
                os.mkdir(self.output_dir)

            self.executor = ProcessPoolExecutor(3)

            id = psutil.Process().pid
            cwd = os.getcwd()

            # jiffies
            self.executor.submit(periodic_sample, sample_cpu, parse_cpu_data, sample_args = [], period = self.period, output_file = os.path.join(self.output_dir, 'ProcStatSample.csv'))
            self.executor.submit(periodic_sample, sample_tasks, parse_tasks_data, sample_args = [id], period = self.period, output_file = os.path.join(self.output_dir, 'ProcTaskSample.csv'))

            # energy
            self.executor.submit(periodic_sample, sample_rapl, parse_rapl_data, sample_args = [], period = self.period, output_file = os.path.join(self.output_dir, 'EnergySample.csv'))

            # yappi
            self.yappi_executor = ThreadPoolExecutor(1)
            self.yappi_future = self.yappi_executor.submit(self.periodic_sample_threads)
            yappi.start()

    def stop(self):
        """ Stops data collection """
        if self.running:
            self.running = False

            PARENT_PIPE.send(1)
            self.executor.shutdown()
            yappi.stop()
            self.yappi_executor.shutdown()
            CHILD_PIPE.recv()

            parse_yappi_data(yappi.get_thread_stats(), self.yappi_future.result()).to_csv(os.path.join(self.output_dir, 'YappiSample.csv'), header=False)

    def periodic_sample_threads(self):
        """ Samples the currently active threads """
        threads = {}
        while self.running:
            start = time()
            threads.update({thread.ident: thread.native_id for thread in threading.enumerate()})
            sleep(max(0, 1 - (time() - start)))

        return threads

def profile(workload, period=50, output_dir=None):
    """ Collects data for the workload """
    eflect = Eflect(period = period, output_dir = output_dir)
    eflect.start()

    workload()

    eflect.stop()

def read(output_dir=None):
    """ Reads data as footprints """
    return account_energy(output_dir)
