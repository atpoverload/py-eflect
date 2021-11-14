""" Object that collects eflect samples into an EflectDataSet. """

from google.protobuf import text_format

from eflect.protos.sample.sample_pb2 import DataSet
from eflect.protos.sample.jiffies_pb2 import CpuSample, CpuStat
from eflect.protos.sample.jiffies_pb2 import TaskSample, TaskStat
from eflect.protos.sample.rapl_pb2 import RaplReading, RaplSample

def load_data_set(data_set_path):
    """ Loads an DataSet from the path. """
    with open(data_set_path, 'rb') as f:
        data_set = DataSet()
        data_set.ParseFromString(f.read())
        return data_set

# TODO(timur): should all of this live in sampler.py?
class SampleStorage:
    def __init__(self):
        self.data_set = DataSet()
        self.data = {
            'cpu': add_cpu,
            'task': add_task,
            'rapl': add_rapl,
        }

    def add(self, data):
        """ Adds a sample to the field. """
        try:
            self.data[data[0]](self.data_set, data)
        except:
            print('invalid sample type passed')

    def read(self):
        """ Returns the stored data set. """
        return self.data_set

def add_cpu(data_set, cpus):
    sample = CpuSample()

    sample.timestamp = cpus[1]
    for data in cpus[2]:
        stat = CpuStat()
        stat.cpu = data[0]
        stat.user = data[1]
        stat.nice = data[2]
        stat.system = data[3]
        stat.idle = data[4]
        stat.iowait = data[5]
        stat.irq = data[6]
        stat.softirq = data[7]
        stat.steal = data[8]
        stat.guest = data[9]
        stat.guest_nice = data[10]

        sample.stat.add().CopyFrom(stat)

    data_set.cpu.add().CopyFrom(sample)

def add_task(data_set, tasks):
    sample = TaskSample()

    sample.timestamp = tasks[1]
    for data in tasks[2]:
        stat = TaskStat()
        stat.task_id = data[0]
        # we don't need this right now
        # stat.thread_name = data[1]
        stat.cpu = data[2]
        stat.user = data[3]
        stat.system = data[4]

        sample.stat.add().CopyFrom(stat)

    data_set.task.add().CopyFrom(sample)

def add_rapl(data_set, rapl):
    sample = RaplSample()

    sample.timestamp = rapl[1]
    for data in rapl[2]:
        reading = RaplReading()
        reading.socket = data[0]
        reading.cpu = data[1]
        reading.dram = data[2]
        reading.package = data[3]
        reading.gpu = data[4]

        sample.reading.add().CopyFrom(reading)

    data_set.rapl.add().CopyFrom(sample)
