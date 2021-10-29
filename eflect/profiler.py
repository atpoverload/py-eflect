""" A data collector for eflect. """

import os

from eflect.sample import Sampler
from eflect.sample.jiffies import jiffies_sources
from eflect.sample.rapl import rapl_sources, sample_fake_rapl

SOURCES = jiffies_sources() + [{'sample_func': sample_fake_rapl}] # + rapl_sources()

class Eflect:
    def __init__(self, period=None):
        self.running = False
        if period is None:
            self.sampler = Sampler(SOURCES)
        else:
            self.sampler = Sampler(SOURCES, period)

    def start(self):
        """ Starts data collection """
        if not self.running:
            self.running = True
            self.sampler.start()

    def stop(self):
        """ Stops data collection """
        if self.running:
            self.running = False
            self.sampler.stop()

    def read(self):
        """ Returns the stored data """
        return self.sampler.read()

def profile(workload, period=None):
    """ Returns a EflectDataSet of the workload """
    eflect = Eflect(period=period)
    eflect.start()

    workload()

    eflect.stop()
    return eflect.read()
