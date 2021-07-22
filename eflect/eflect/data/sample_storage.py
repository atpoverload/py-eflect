""" Object that collects eflect samples into an EflectDataSet. """

from eflect.proto.data_set_pb2 import EflectDataSet
from eflect.proto.proc_stat_pb2 import ProcStatSample
from eflect.proto.proc_task_pb2 import ProcTaskSample
from eflect.proto.rapl_pb2 import RaplSample
from eflect.proto.yappi_pb2 import YappiSample

class SampleStorage:
    def __init__(self):
        self.data_set = EflectDataSet()
        self.data = {
            ProcStatSample: self.data_set.proc_stat,
            ProcTaskSample: self.data_set.proc_task,
            RaplSample: self.data_set.rapl,
            YappiSample: self.data_set.yappi_stack_trace,
        }

    def add(self, data):
        """ Adds a sample to the field. """
        for sample_type in [ProcStatSample, ProcTaskSample, RaplSample, YappiSample]:
            if isinstance(data, sample_type):
                self.data[sample_type].add().CopyFrom(data)

    def process(self):
        """ Returns the stored data set. """
        return self.data_set
