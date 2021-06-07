import os

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Pipe
from time import sleep

import psutil
import yappi

from eflect.data import *
from eflect.processing import account_energy

PARENT_PIPE, CHILD_PIPE = Pipe()
PERIOD = 0.050

def periodic_sample(sample_func, parse_func, **kwargs):
    data = []
    while not CHILD_PIPE.poll():
        data.append(sample_func(*kwargs['sample_args']))
        if 'period' in kwargs:
            sleep(kwargs['period'])
        else:
            sleep(PERIOD)
    parse_func(data).to_csv(kwargs['output_file'], header = False)

class Eflect:
    def __init__(self, period = 50, output_dir = None):
        self.period = period / 1000
        if output_dir is None:
            self.output_dir = os.getcwd()
        else:
            self.output_dir = output_dir
        self.running = False

    def start(self):
        if not self.running:
            self.running = True
            self.executor = ProcessPoolExecutor(3)

            id = psutil.Process().pid
            cwd = os.getcwd()

            if not os.path.exists(self.output_dir):
                os.mkdir(self.output_dir)

            # jiffies
            self.executor.submit(periodic_sample, sample_tasks, parse_tasks_data, sample_args = [id], period = self.period, output_file = os.path.join(self.output_dir, 'ProcTaskSample.csv'))
            self.executor.submit(periodic_sample, sample_cpu, parse_cpu_data, sample_args = [], period = self.period, output_file = os.path.join(self.output_dir, 'ProcStatSample.csv'))

            # rapl
            self.executor.submit(periodic_sample, sample_rapl, parse_energy_data, sample_args = [], period = self.period, output_file = os.path.join(self.output_dir, 'EnergySample.csv'))

            # traces
            self.yappi_executor = ThreadPoolExecutor(1)
            yappi.start()
            self.yappi_executor.submit(periodic_sample, sample_yappi, parse_yappi_data, sample_args = [], period = self.period, output_file = os.path.join(self.output_dir, 'StackTraceSample.csv'))

    def stop(self):
        if self.running:
            self.running = False

            PARENT_PIPE.send(1)
            self.executor.shutdown()
            self.yappi_executor.shutdown()
            yappi.stop()
            CHILD_PIPE.recv()

def profile(workload, period = 50, output_dir = None):
    eflect = Eflect(period = period, output_dir = output_dir)
    eflect.start()

    workload()

    eflect.stop()
    return account_energy(output_dir)
