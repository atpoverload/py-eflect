from time import time

def get_unixtime(timestamp=None):
    if timestamp is None:
        return int(10 ** 3 * time())
    else:
        return int(10 ** 3 * timestamp)

from eflect.data.proc_stat import sample_proc_stat
from eflect.data.proc_task import sample_proc_task
from eflect.data.rapl import sample_rapl
from eflect.data.yappi import sample_yappi

from eflect.data.sample_storage import SampleStorage
