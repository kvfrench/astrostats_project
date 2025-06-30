#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 11:15:24 2025

@author: kfrench
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress


dirname = '/Users/kfrench/Desktop/LASCO_CBI/'
fname = 'cbi_wedge_40_sum.xlsx'
f = dirname + fname


orig_df = pd.read_excel(f)
orig_df['Date'] = pd.to_datetime(orig_df['Date'])
orig_df.rename(columns={'Corrected Velocity': 'Vel', 'Median Brightness': 'CBI'}, inplace=True)


flare_intensities = np.zeros(len(orig_df), dtype='float')
for idx, each_flare in enumerate(orig_df['Cls']):
    fclass = each_flare[0]
    mult = 10.0 if (fclass == 'X') else 1.0
    fval = float(each_flare[1:])
    flare_intensities[idx] = mult * fval
orig_df['F_Intensity'] = flare_intensities


df = orig_df[orig_df['Vel'] > 0]


mean_cbi = df['CBI'].mean()
std_cbi = df['CBI'].std()
mean_vel = df['Vel'].mean()
std_vel = df['Vel'].std()
sem_cbi = std_cbi / np.sqrt(len(df))
sem_vel = std_vel / np.sqrt(len(df))


slope, intercept, r_value, p_value, std_err = linregress(df['CBI'], df['Vel'])


plt.figure(figsize=(8, 6))


plt.scatter(df['CBI'], df['Vel'], s=10, color='blue', alpha=0.3, zorder=2)


x_min, x_max = df['CBI'].min(), df['CBI'].max()


x_vals = np.array([x_min, x_max])
y_vals = slope * x_vals + intercept


plt.plot(x_vals, y_vals, color='red', linewidth=2, label='Regression Line')


plt.axvspan(mean_cbi - 2*sem_cbi, mean_cbi + 2*sem_cbi,
            color='red', alpha=0.2, label='CBI ±2 SE')
plt.axhspan(mean_vel - 2*sem_vel, mean_vel + 2*sem_vel,
            color='blue', alpha=0.2, label='Velocity ±2 SE')


x_vals = np.array([df['CBI'].min(), df['CBI'].max()])
y_vals = intercept + slope * x_vals
plt.plot(x_vals, y_vals, color='black', linestyle='-', label='Linear Fit')


plt.xlabel("CBI Value (MSB)", fontsize=16)
plt.ylabel("CME Velocity (km/s)", fontsize=16)
plt.title("CME Velocity vs. CBI Value", fontsize=16)


plt.xticks(fontsize=14)
plt.yticks(fontsize=14)


stats_text = (
    f"CBI Mean ± 2SE:\n{mean_cbi:.2f} ± {2*sem_cbi:.2f}\n\n"
    f"Velocity Mean ± 2SE:\n{mean_vel:.1f} ± {2*sem_vel:.1f} km/s\n\n"
    f"Fit: Vel = {slope:.2f}·CBI + {intercept:.1f}\n"
    f"r = {r_value:.2f}, p = {p_value:.3f}"
)

plt.text(0.98, 0.98, stats_text,
         transform=plt.gca().transAxes,
         fontsize=12,
         verticalalignment='top',
         horizontalalignment='right',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.9))


plt.legend(loc='upper left', fontsize=10, frameon=True)
plt.grid(True, linestyle='--', linewidth=0.5)
plt.tight_layout()

plt.show()
