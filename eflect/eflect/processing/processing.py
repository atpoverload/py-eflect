import os

from sys import argv

import numpy as np
import pandas as pd

from eflect.processing.preprocessing import process_app_data
from eflect.processing.preprocessing import process_cpu_data
from eflect.processing.preprocessing import process_energy_data

def account_application_energy(app, cpu, energy):
    return energy * (app / cpu).replace(np.inf, 1).clip(0, 1)

def pre_process(data_dir):
    app = []
    cpu = []
    energy = []
    traces = []
    for f in os.listdir(os.path.join(data_dir)):
        df = pd.read_csv(os.path.join(data_dir, f), header = None)
        if 'ProcTaskSample' in f:
            app.append(process_app_data(df))
        elif 'ProcStatSample' in f:
            cpu.append(process_cpu_data(df))
        elif 'EnergySample' in f:
            energy.append(process_energy_data(df))

    return pd.concat(app), pd.concat(cpu), pd.concat(energy)

def account_energy(path):
    app, cpu, energy, traces = pre_process(path)

    footprints = account_application_energy(app, cpu, energy).dropna().reset_index()
    footprints = footprints.assign(id = footprints.id.str.split('-').str[0].astype(int)).set_index(['timestamp', 'id'])[0]
    footprints.name = 'energy'

    return footprints
