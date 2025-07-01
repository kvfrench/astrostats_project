#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 16:40:50 2025

@author: kfrench
"""

import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.stats import pearsonr

# Path to SWAN database
db_path = '/Users/kfrench/Desktop/swan/swan_preprocess_cbi.db'

# === Query the database for time series ===
query = """
SELECT Timestamp, CBI, TOTBSQ
FROM solar_flare_data
WHERE CBI IS NOT NULL AND TOTBSQ IS NOT NULL
ORDER BY Timestamp
"""

# === Load data into DataFrame ===
conn = sqlite3.connect(db_path)
df = pd.read_sql_query(query, conn)
conn.close()

# === Parse timestamp ===
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# === Plot time series ===
df.sort_values('Timestamp', inplace=True)

fig, ax1 = plt.subplots(figsize=(12, 6))

color_cbi = 'tab:blue'
color_meanpot = 'tab:red'

# Plot CBI as a solid line with light alpha
ax1.set_xlabel("Date", fontsize=14)
ax1.set_ylabel("CBI (MSB)", color=color_cbi, fontsize=14)
ax1.plot(df['Timestamp'], df['CBI'], color=color_cbi, linestyle='-', alpha=0.6, label='CBI')
ax1.tick_params(axis='y', labelcolor=color_cbi)

# Plot MEANPOT as dashed line with light alpha on twin axis
ax2 = ax1.twinx()
ax2.set_ylabel("TOTBSQ (G$^2$)", color=color_meanpot, fontsize=14)
ax2.plot(df['Timestamp'], df['TOTBSQ'], color=color_meanpot, linestyle='--', alpha=0.6, label='TOTBSQ')
ax2.tick_params(axis='y', labelcolor=color_meanpot)

# Format dates better
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))  # every 3 months
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
fig.autofmt_xdate()

# Lighter grid only on y axes
ax1.grid(True, axis='y', linestyle='--', alpha=0.3)
ax2.grid(False)

# Legend outside to the right
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2,
           loc='upper right', fontsize=11,
           framealpha=0.85, facecolor='white', edgecolor='gray')


# === Compute stats ===
cbi_mean = df['CBI'].mean()
cbi_std = df['CBI'].std()
meanpot_mean = df['TOTBSQ'].mean()
meanpot_std = df['TOTBSQ'].std()

# Pearson correlation
r_value, p_value = pearsonr(df['CBI'], df['TOTBSQ'])

# === Annotate on the plot ===
stats_text = (
    f"CBI: μ={cbi_mean:.2f}, σ={cbi_std:.2f}\n"
    f"TOTBSQ: μ={meanpot_mean:.2e}, σ={meanpot_std:.2e}\n"
    f"Pearson r = {r_value:.2f} (p = {p_value:.2e})"
)

# Add a textbox to the upper right of the plot
ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
         fontsize=11, va='top', ha='left',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.85))

fig.suptitle("Time Series of CBI and TOTBSQ (Raw Data)", fontsize=16)
fig.tight_layout()

plt.show()


