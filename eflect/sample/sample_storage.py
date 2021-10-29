""" Object that collects eflect samples into an EflectDataSet. """

from eflect.protos.sample.data_set_pb2 import EflectDataSet
from eflect.protos.sample.jiffies_pb2 import CpuSample, TaskSample
from eflect.protos.sample.rapl_pb2 import RaplSample

# TODO(timur): should all of this live in sampler.py?
class SampleStorage:
    def __init__(self):
        self.data_set = EflectDataSet()
        self.data = {
            CpuSample: self.data_set.cpu,
            TaskSample: self.data_set.task,
            RaplSample: self.data_set.rapl,
        }

    def add(self, data):
        """ Adds a sample to the field. """
        for sample_type in self.data.keys():
            if isinstance(data, sample_type):
                self.data[sample_type].add().CopyFrom(data)

    def read(self):
        """ Returns the stored data set. """
        return self.data_set

def load_data_set(data_set_path):
    """ Loads an EflectDataSet from the path. """
    with open(data_set_path, 'rb') as f:
        data_set = EflectDataSet()
        data_set.ParseFromString(f.read())
        return data_set
