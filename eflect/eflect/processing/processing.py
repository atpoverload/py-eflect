import os

from sys import argv

import numpy as np
import pandas as pd

from eflect.processing.preprocessing import read_app_data, read_cpu_data, read_energy_data, read_async_data

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
            app.append(read_app_data(df))
        elif 'ProcStatSample' in f:
            cpu.append(read_cpu_data(df))
        elif 'EnergySample' in f:
            energy.append(read_energy_data(df))
        elif 'AsyncProfilerSample' in f:
            traces.append(read_async_data(df))
        elif 'StackTraceSample' in f:
            traces.append(read_async_data(df))

    return pd.concat(app), pd.concat(cpu), pd.concat(energy), pd.concat(traces)

def account_energy(path):
    app, cpu, energy, traces = pre_process(path)
    return account_application_energy(app, cpu, energy)
