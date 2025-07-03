#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  1 15:28:28 2025

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

# Query TOTPOT and CBI
query = """
SELECT Timestamp, CBI, TOTPOT
FROM solar_flare_data
WHERE CBI IS NOT NULL AND TOTPOT IS NOT NULL
ORDER BY Timestamp
"""

# Load data
conn = sqlite3.connect(db_path)
df = pd.read_sql_query(query, conn)
conn.close()

df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df.sort_values('Timestamp', inplace=True)

# Filter out zeros or negatives to avoid log issues
df = df[df['TOTPOT'] > 0].copy()
df['log_TOTPOT'] = np.log10(df['TOTPOT'])

# Plot
fig, ax1 = plt.subplots(figsize=(12, 6))

color_cbi = 'tab:blue'
color_totpot = 'tab:orange'

ax1.set_xlabel("Date", fontsize=14)
ax1.set_ylabel("CBI (MSB)", color=color_cbi, fontsize=14)
ax1.plot(df['Timestamp'], df['CBI'], color=color_cbi, alpha=0.6, label='CBI')
ax1.tick_params(axis='y', labelcolor=color_cbi)

ax2 = ax1.twinx()
ax2.set_ylabel("log10(TOTPOT) (Mx$^2$/cm)", color=color_totpot, fontsize=14)
ax2.plot(df['Timestamp'], df['log_TOTPOT'], color=color_totpot, linestyle='--', alpha=0.6, label='log10(TOTPOT)')
ax2.tick_params(axis='y', labelcolor=color_totpot)

# Format dates
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
fig.autofmt_xdate()

# Grid and legend inside plot
ax1.grid(True, axis='y', linestyle='--', alpha=0.3)
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2,
           loc='upper right', fontsize=11,
           framealpha=0.85, facecolor='white', edgecolor='gray')

# Stats box inside plot
r_value, p_value = pearsonr(df['CBI'], df['log_TOTPOT'])
stats_text = f"Pearson r = {r_value:.2f} (p = {p_value:.2e})"
ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
         fontsize=11, va='top', ha='left',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.85))

fig.suptitle("Time Series of CBI and log10(TOTPOT)", fontsize=16)
fig.tight_layout()
plt.show()
