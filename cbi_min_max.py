#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  6 13:44:12 2025

@author: kfrench
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# === Load and process data ===
dirname = '/Users/kfrench/Desktop/LASCO_CBI/'
fname = 'cbi_wedge_40_sum_markedAR.xlsx'
no_cme_threshold = 0

f = dirname + fname
orig_df = pd.read_excel(f)
orig_df['Date'] = pd.to_datetime(orig_df['Date'])
orig_df.rename(columns={'Corrected Velocity': 'Vel', 'Median Brightness': 'CBI'}, inplace=True)

# Convert flare class to intensity
flare_intensities = np.zeros(len(orig_df), dtype='float')
for idx, each_flare in enumerate(orig_df['Cls']):
    fclass = each_flare[0]
    mult = 10.0 if fclass == 'X' else 1.0
    fval = float(each_flare[1:])
    flare_intensities[idx] = mult * fval
orig_df['F_Intensity'] = flare_intensities

# === Define expanded solar cycle and phase periods ===
sc23_min = ('1996-05-01', '1998-12-31')
sc23_max = ('1999-01-01', '2003-12-31')
sc24_min = ('2008-12-01', '2011-12-31')
sc24_max = ('2012-01-01', '2015-12-31')


# Helper function
def mask(df, start, end):
    return df[(df['Date'] >= start) & (df['Date'] <= end) & (df['Vel'] > 0) & (df['CBI'] > 0)]

df23_min = mask(orig_df, *sc23_min)
df23_max = mask(orig_df, *sc23_max)
df24_min = mask(orig_df, *sc24_min)
df24_max = mask(orig_df, *sc24_max)

# Stats function
def compute_stats(df_slice):
    return {
        'N': len(df_slice),
        'CBI mean': np.mean(df_slice['CBI']),
        'CBI median': np.median(df_slice['CBI']),
        'Vel mean': np.mean(df_slice['Vel']),
        'Vel median': np.median(df_slice['Vel']),
    }

# === Set up 2x2 plot grid ===
fig, axs = plt.subplots(2, 2, figsize=(12, 10), sharex=True, sharey=True)

# Data/label layout
plot_data = [
    (df23_min, "SC23 Min", axs[0, 0]),
    (df23_max, "SC23 Max", axs[0, 1]),
    (df24_min, "SC24 Min", axs[1, 0]),
    (df24_max, "SC24 Max", axs[1, 1]),
]

for df_phase, title, ax in plot_data:
    ax.scatter(df_phase['CBI'], df_phase['Vel'], s=20)
    stats = compute_stats(df_phase)
    ax.set_title(f"{title} (N={stats['N']})", fontsize=14)
    ax.grid(True)

    # Stats box under legend area (top right)
    textstr = (
        f"CBI μ={stats['CBI mean']:.2e}, med={stats['CBI median']:.2e}\n"
        f"Vel μ={stats['Vel mean']:.1f} km/s, med={stats['Vel median']:.1f}"
    )
    ax.text(0.98, 0.78, textstr, transform=ax.transAxes,
            fontsize=10, va='top', ha='right',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8))

# Axis labels
for ax in axs[1, :]:
    ax.set_xlabel("CBI Value (MSB)", fontsize=12)
for ax in axs[:, 0]:
    ax.set_ylabel("CME Velocity (km/s)", fontsize=12)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.suptitle("CME Velocity vs CBI During Solar Minimum and Maximum (by Cycle)", fontsize=16, y=0.995)
plt.show()
