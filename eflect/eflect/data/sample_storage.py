""" Object that collects eflect samples into an EflectDataSet. """

from eflect.proto import EflectDataSet
from eflect.proto import CpuFreqSample
from eflect.proto import ProcStatSample
from eflect.proto import ProcTaskSample
from eflect.proto import RaplSample
from eflect.proto import YappiSample

class SampleStorage:
    def __init__(self):
        self.data_set = EflectDataSet()
        self.data = {
            CpuFreqSample: self.data_set.cpu_freq,
            ProcStatSample: self.data_set.proc_stat,
            ProcTaskSample: self.data_set.proc_task,
            RaplSample: self.data_set.rapl,
            YappiSample: self.data_set.yappi_stack_trace,
        }

    def add(self, data):
        """ Adds a sample to the field. """
        for sample_type in self.data.keys():
            if isinstance(data, sample_type):
                self.data[sample_type].add().CopyFrom(data)

    def process(self):
        """ Returns the stored data set. """
        return self.data_set
