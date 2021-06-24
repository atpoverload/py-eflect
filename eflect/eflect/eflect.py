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

def periodic_sample_threads():
    threads = {}
    while not CHILD_PIPE.poll():
        start = time()
        threads.update({thread.ident: thread.native_id for thread in threading.enumerate()})
        sleep(max(0, PERIOD - (time() - start)))

    return threads

def periodic_sample(sample_func, parse_func, **kwargs):
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

            self.yappi_executor = ThreadPoolExecutor(1)
            self.yappi_future = self.executor.submit(periodic_sample_threads)
            yappi.start()

    def stop(self):
        if self.running:
            self.running = False

            PARENT_PIPE.send(1)
            self.executor.shutdown()
            yappi.stop()
            self.yappi_executor.shutdown()
            CHILD_PIPE.recv()

            parse_yappi_data(yappi.get_thread_stats(), self.yappi_future.result()).to_csv(os.path.join(self.output_dir, 'StackTraceSample.csv'), header=False)

def profile(workload, period=50, output_dir=None):
    eflect = Eflect(period = period, output_dir = output_dir)
    eflect.start()

    workload()

    eflect.stop()

def read(output_dir=None):
    return account_energy(output_dir)
