from concurrent.futures import ThreadPoolExecutor
from threading import Timer
from time import time, sleep

from eflect import read_tasks, read_cpu

class Eflect:
    def __init__(self, period):
        self.running = False
        self.period = period
        self.executor = ThreadPoolExecutor(
            max_workers=2,
            thread_name_prefix='eflect'
        )

    def start(self):
        self.running = True
        self.task = []
        self.cpu = []
        self.energy = []
        self.executor.submit(
            self.__reschedule,
            lambda: self.task.append(read_tasks())
        )
        self.executor.submit(
            self.__reschedule,
            lambda: self.cpu.append(read_cpu())
        )
        self.executor.submit(
            self.__reschedule,
            lambda: self.energy.append(read_energy)
        )

    def stop(self):
        self.running = False

    def read(self):
        return [self.task, self.cpu]

    def __reschedule(self, func):
        if not self.running:
            return
        start = time()
        func()
        end = time()

        remaining = self.period - end - start
        if remaining > 0:
            sleep(remaining)

        self.executor.submit(
            self.__reschedule,
            func
        )

def run(code, period = 41):
    eflect = Eflect(period)
    eflect.start()
    exec(code)
    eflect.stop()
    return eflect.read()
