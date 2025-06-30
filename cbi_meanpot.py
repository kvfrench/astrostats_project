#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 16:40:50 2025

@author: kfrench
"""

import pandas as pd
import numpy as np
import sqlite3
from datetime import timedelta
import matplotlib.pyplot as plt
from scipy.stats import linregress

# Load CBI data
cbi_file = '/Users/kfrench/Desktop/LASCO_CBI/cbi_wedge_40_sum.xlsx'
orig_df = pd.read_excel(cbi_file)
orig_df['Date'] = pd.to_datetime(orig_df['Date'])
orig_df.rename(columns={'Corrected Velocity': 'Vel', 'Median Brightness': 'CBI'}, inplace=True)

#Swan database
db_path = '/Users/kfrench/Desktop/swan/swan_preprocess.db'


# Parse flare intensity as before 
flare_intensities = np.zeros(len(orig_df), dtype='float')
for idx, each_flare in enumerate(orig_df['Cls']):
    fclass = each_flare[0]
    mult = 10.0 if (fclass == 'X') else 1.0
    fval = float(each_flare[1:])
    flare_intensities[idx] = mult * fval
orig_df['F_Intensity'] = flare_intensities

# Filter for valid velocities
df = orig_df[orig_df['Vel'] > 0]

# === MEANPOT matching ===
def get_meanpot_near_times(cbi_df, db_path, time_window_hours=6):
    conn = sqlite3.connect(db_path)
    results = []

    for date in cbi_df['Date']:
        start_time = (date - timedelta(hours=time_window_hours)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = (date + timedelta(hours=time_window_hours)).strftime("%Y-%m-%d %H:%M:%S")

        query = f"""
        SELECT MEANPOT
        FROM solar_flare_data
        WHERE Timestamp BETWEEN '{start_time}' AND '{end_time}'
        AND MEANPOT IS NOT NULL
        """
        df_window = pd.read_sql_query(query, conn)

        if not df_window.empty:
            results.append(df_window['MEANPOT'].max())  # or mean(), first(), etc.
        else:
            results.append(np.nan)

    conn.close()
    return results

# Match MEANPOT values
df['MEANPOT'] = get_meanpot_near_times(df, db_path, time_window_hours=6)
df.dropna(subset=['MEANPOT'], inplace=True)

# Scatter plot: CBI vs MEANPOT (log y-axis)
plt.figure(figsize=(8, 6))
plt.scatter(df['MEANPOT'], df['CBI'], color='darkgreen', alpha=0.5, s=15)
plt.xlabel("MEANPOT (Mx$^2$/cm$^2$)", fontsize=14)
plt.ylabel("CBI (MSB)", fontsize=14)
plt.title("CBI vs. MEANPOT", fontsize=16)
plt.xscale('log')  # log scale on MEANPOT
plt.grid(True, which='both', linestyle='--', linewidth=0.5)

slope, intercept, r_value, p_value, _ = linregress(np.log10(df['MEANPOT']), df['CBI'])
x_vals = np.logspace(np.log10(df['MEANPOT'].min()), np.log10(df['MEANPOT'].max()), 100)
y_vals = slope * np.log10(x_vals) + intercept
plt.plot(x_vals, y_vals, color='black', label=f"Log-Linear Fit: r={r_value:.2f}, p={p_value:.3f}")

plt.legend()
plt.tight_layout()
plt.show()
