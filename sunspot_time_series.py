#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 12:51:08 2025

@author: kfrench
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime


cube = np.load('/Users/kfrench/Desktop/LASCO_CBI/cbi_interp_may2023.npy', allow_pickle=True)
dates = np.load('/Users/kfrench/Desktop/LASCO_CBI/cbi_dates_interp_Nov2022_rev.npy', allow_pickle=True)
cbi_ts = np.median(cube, axis=[1, 2])  # Or multiply by 1e4 if preferred


url = "https://www.sidc.be/SILSO/DATA/SN_m_tot_V2.0.txt"
col_names = ['year', 'month', 'decimal_date', 'sunspot_number',
             'std_dev', 'num_obs', 'provisional']
sunspots = pd.read_csv(url, delim_whitespace=True, header=None, names=col_names)
sunspots['date'] = pd.to_datetime(dict(year=sunspots.year, month=sunspots.month, day=1))


start_date = pd.to_datetime(dates[100])  # skip first 100 goofy entries
end_date = pd.to_datetime(dates[-1])
sunspots = sunspots[(sunspots['date'] >= start_date) & (sunspots['date'] <= end_date)]


fig, ax1 = plt.subplots(figsize=(10, 5))

# CBI data
ax1.plot(dates[100:], cbi_ts[100:], color='steelblue', label='CBI')
ax1.set_xlabel("Year")
ax1.set_ylabel("Mean Solar Brightness (CBI)", color='steelblue')
ax1.tick_params(axis='y', labelcolor='steelblue')

#Sunspot data
ax2 = ax1.twinx()
ax2.plot(sunspots['date'], sunspots['sunspot_number'], color='indianred', alpha=0.7, label='Sunspot Number')
ax2.set_ylabel("Monthly Sunspot Number", color='indianred')
ax2.tick_params(axis='y', labelcolor='indianred')


plt.title('Coronal Brightness Index and Sunspot Number Time Series')
ax1.grid(True)
fig.tight_layout()
plt.show()
