import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def compute_metrics(accounted, total):
    gap = 1 - (accounted / total).replace(np.inf, 1).groupby('domain').mean()
    correlation = [accounted.unstack()[0].corr(total.unstack()[0]), accounted.unstack()[1].corr(total.unstack()[1])]
    df = pd.concat([
        100 * gap,
        pd.Series(name = 'correlation', data = correlation)
    ], axis = 1)
    df.columns = ['gap', 'corr']
    df.index.name = 'domain'

    return df

# def energy_accounting_plot(accounted, total, metrics = None):
#     fig, axs = plt.subplots(1, 2, figsize = (16, 5))
#     s = None
#     for (domain, run), df in accounted.groupby(['domain', 'run']):
#         ax = axs[domain]
#         if s is None:
#             s = df.reset_index().set_index(['timestamp', 'domain'])
#         else:
#             s += df.reset_index().set_index(['timestamp', 'domain'])
#         s.plot(legend = False, ax = ax)
#
#     for (domain, run), df in total.groupby(['domain', 'run']):
#         ax = axs[domain]
#         df.plot(color = 'k', linestyle = '--', alpha = 0.5, legend = False, ax = ax)
#
#         ts = df.reset_index().timestamp - df.reset_index().timestamp.min()
#         ax.set_xticklabels(ts.dt.microseconds // 100)
#
#     for domain, _ in accounted.groupby('domain'):
#         ax = axs[domain]
#
#         max_power = int(max(accounted[0].max(), total[0].max()) + 5)
#         ax.set_ylim(0, 100)
#         text = metrics.loc[domain].index + '=' + metrics.loc[domain].apply('{:.2f}'.format)
#         offset = 0.95
#         for t in text:
#             axs[domain].text(len(ts) * 0.02, max_power * offset, t)
#             offset -= 0.05
#         ax.set_xlabel('elapsed (s)', fontsize = 16)
#         ax.set_ylabel('Power (J/s)', fontsize = 16)
#         ax.set_title('Socket {}'.format(domain + 1), fontsize = 16)
#
#     return fig, axs

def energy_accounting_plot(accounted, total):
    fig, axs = plt.subplots(1, 2, figsize = (16, 5))
    for domain, df in accounted.groupby('domain'):
        ax = axs[domain]
        df.reset_index('domain').app.unstack().plot(stacked = True, ax = ax, legend = True if domain == 1 else False)

    for domain, df in total.groupby('domain'):
        ax = axs[domain]
        df.reset_index('domain').total.unstack().plot(color = 'k', alpha = 0.75, linestyle = '--', ax = ax, legend = False)

    for domain, _ in accounted.groupby('domain'):
        ax = axs[domain]

        ts = df.reset_index().timestamp - df.reset_index().timestamp.min()
        ax.set_xticklabels(ts.dt.microseconds // 100)

        max_power = int(max(accounted.max(), total.max()) + 5)
        ax.set_ylim(0, max_power)

        ax.set_xlabel('elapsed (s)', fontsize = 16)
        ax.set_ylabel('Power (J/s)', fontsize = 16)
        ax.set_title('Socket {}'.format(domain + 1), fontsize = 16)

    return fig, axs
