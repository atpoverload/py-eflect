import os

from sys import argv

import numpy as np
import pandas as pd

from eflect.processing.preprocessing import process_app_data
from eflect.processing.preprocessing import process_cpu_data
from eflect.processing.preprocessing import process_energy_data
from eflect.processing.preprocessing import process_smi_data

def account_application_energy(app, cpu, energy):
    return energy * (app / cpu).replace(np.inf, 1).clip(0, 1)

def pre_process(data_dir):
    app = []
    cpu = []
    energy = []
    traces = []
    nvidia = []
    for f in os.listdir(os.path.join(data_dir)):
        df = pd.read_csv(os.path.join(data_dir, f), header = None)
        if 'ProcTaskSample' in f:
            app.append(process_app_data(df))
        elif 'ProcStatSample' in f:
            cpu.append(process_cpu_data(df))
        elif 'EnergySample' in f:
            energy.append(process_energy_data(df))
        elif 'NvidiaSmiSample' in f:
            nvidia.append(process_smi_data(df))

    return {
        'app': pd.concat(app) if len(app) > 0 else None,
        'cpu': pd.concat(cpu) if len(cpu) > 0 else None,
        'energy': pd.concat(energy) if len(energy) > 0 else None,
        'nvidia': pd.concat(nvidia) if len(nvidia) > 0 else None,
        'trace': pd.concat(traces) if len(traces) > 0 else None
    }

def account_energy(path):
    data = pre_process(path)

    df = pd.concat([data['nvidia'].reset_index().assign(domain = i) for i in data['app'].reset_index().domain.unique()]).set_index(['timestamp', 'domain'])
    footprints = account_application_energy(data['app'], data['cpu'], df.sum(axis = 1)).dropna().reset_index()
    footprints = footprints.assign(id = footprints.id.str.split('-').str[0].astype(int)).set_index(['timestamp', 'id'])[0]
    footprints.name = 'energy'
    print(footprints.groupby('id').sum())

    # footprints = account_application_energy(data['app'], data['cpu'], data['energy']).dropna().reset_index()
    # footprints = footprints.assign(id = footprints.id.str.split('-').str[0].astype(int)).set_index(['timestamp', 'id'])[0]
    # footprints.name = 'energy'

    return footprints
