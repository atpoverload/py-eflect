import os

from sys import argv

import numpy as np
import pandas as pd

from eflect.processing.preprocessing import process_app_data
from eflect.processing.preprocessing import process_cpu_data
from eflect.processing.preprocessing import process_energy_data
from eflect.processing.preprocessing import process_yappi_data
from eflect.processing.preprocessing import process_nvidia_data

def account_rapl_application_energy(app, cpu, energy):
    return energy * (app / cpu).replace(np.inf, 1).clip(0, 1)

def account_nvidia_application_energy(app, cpu, energy):
    df = (app / cpu).replace(np.inf, 1).clip(0, 1).groupby(['timestamp', 'id']).sum()
    return df * energy

def pre_process(data_dir):
    app = []
    cpu = []
    energy = []
    nvidia = []
    for f in os.listdir(os.path.join(data_dir)):
        if 'ProcTaskSample' in f:
            df = pd.read_csv(os.path.join(data_dir, f))
            app.append(process_app_data(df))
        elif 'ProcStatSample' in f:
            df = pd.read_csv(os.path.join(data_dir, f))
            cpu.append(process_cpu_data(df))
        elif 'EnergySample' in f:
            df = pd.read_csv(os.path.join(data_dir, f))
            energy.append(process_energy_data(df))
        elif 'NvidiaSmiSample' in f:
            df = pd.read_csv(os.path.join(data_dir, f))
            nvidia.append(process_nvidia_data(df))

    return pd.concat(app), pd.concat(cpu), pd.concat(energy), pd.concat(nvidia)

def align_methods(footprints, data_dir):
        energy = []
        for f in os.listdir(os.path.join(data_dir)):
            if 'YappiSample' in f:
                df = pd.read_csv(os.path.join(data_dir, f))
                df = footprints.groupby('id').sum() * process_yappi_data(df)
                df = df.groupby('method').sum().sort_values(ascending=False)
                energy.append(df)

        return pd.concat(energy)

def account_energy(path):
    app, cpu, energy, nvidia = pre_process(path)

    footprint = account_rapl_application_energy(app, cpu, energy).dropna().reset_index()
    footprint = footprint.assign(id = footprint.id.str.split('-').str[0].astype(int)).set_index(['timestamp', 'id'])[0]
    footprint.name = 'energy'
    footprint.sort_values(ascending = True)

    ranking = align_methods(footprint, path)
    ranking.name = 'energy'
    ranking = ranking / ranking.sum()
    ranking.sort_values(ascending = True)

    footprint2 = account_nvidia_application_energy(app, cpu, nvidia).dropna().reset_index()
    footprint2 = footprint2.assign(id = footprint2.id.str.split('-').str[0].astype(int)).set_index(['timestamp', 'id'])[0]
    footprint2.name = 'energy'
    footprint2.sort_values(ascending = True)

    ranking2 = align_methods(footprint2, path)
    ranking2.name = 'energy'
    ranking2 = ranking2 / ranking2.sum()
    ranking2.sort_values(ascending = True)

    return footprint, ranking, footprint2, ranking2
