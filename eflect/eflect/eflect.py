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
        if 'sample_args' in kwargs:
            data.append(sample_func(kwargs['sample_args']))
        else:
            data.append(sample_func())
        sleep(max(0, PERIOD - (time() - start)))
    return parse_func(data), kwargs['output']

class Eflect:
    def __init__(self, output_dir=None):
        if output_dir is None:
            self.output_dir = os.getcwd()
        else:
            self.output_dir = output_dir
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
                sample_cpu,
                parse_cpu_data,
                output='ProcStatSample.csv'
            ))
            self.data_futures.append(self.executor.submit(
                periodic_sample,
                sample_tasks,
                parse_tasks_data,
                sample_args=psutil.Process().pid,
                output='ProcTaskSample.csv'
            ))

            # energy
            self.data_futures.append(self.executor.submit(
                periodic_sample,
                sample_rapl,
                parse_rapl_data,
                output='EnergySample.csv'
            ))

            # yappi
            self.yappi_executor = ThreadPoolExecutor(1)
            self.thread_future = self.yappi_executor.submit(self.periodic_sample_threads)
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

            if not os.path.exists(self.output_dir):
                os.mkdir(self.output_dir)
            output_file = lambda f: os.path.join(self.output_dir, f)

            for future in self.data_futures:
                data, output_name = future.result()
                data.to_csv(output_file(output_name))

            parse_yappi_data(
                yappi.get_thread_stats(),
                self.thread_future.result()
            ).to_csv(output_file('YappiSample.csv'))

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
    eflect = Eflect(output_dir = output_dir)
    eflect.start()

    workload()

    eflect.stop()

def read(output_dir=None):
    """ Reads data as footprints """
    return account_energy(output_dir)
