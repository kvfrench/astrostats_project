#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 14:46:42 2025

@author: kfrench
"""


import pandas as pd
import numpy as np
from scipy.stats import linregress, t


dirname = '/Users/kfrench/Desktop/LASCO_CBI/'
fname = 'cbi_wedge_40_sum_markedAR.xlsx'
f = dirname + fname


orig_df = pd.read_excel(f)
orig_df['Date'] = pd.to_datetime(orig_df['Date'])
orig_df.rename(columns={'Corrected Velocity': 'Vel', 'Median Brightness': 'CBI'}, inplace=True)


df = orig_df[orig_df['Vel'] > 0]


def reg_compare(df, x_col='CBI', y_col='Vel'):
    """
    Compare manual linear regression to scipy.stats.linregress.
    Includes manual p-value calculation for the slope.
    """

    df_clean = df.dropna(subset=[x_col, y_col])
    x = df_clean[x_col].values
    y = df_clean[y_col].values
    n = len(x)

    # Manual regression
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    x_dev = x - x_mean
    y_dev = y - y_mean

    numerator = np.sum(x_dev * y_dev)
    denominator = np.sum(x_dev ** 2)
    slope_manual = numerator / denominator
    intercept_manual = y_mean - slope_manual * x_mean
    r_manual = numerator / np.sqrt(np.sum(x_dev ** 2) * np.sum(y_dev ** 2))
    r_squared_manual = r_manual ** 2

    # Manual standard error and t-test for slope
    y_pred = slope_manual * x + intercept_manual
    residuals = y - y_pred
    residual_variance = np.sum(residuals**2) / (n - 2)
    se_slope = np.sqrt(residual_variance / np.sum(x_dev ** 2))
    t_stat = slope_manual / se_slope
    p_manual = 2 * t.sf(np.abs(t_stat), df=n - 2)  # two-tailed

    # Library regression
    slope_lib, intercept_lib, r_value, p_value, std_err = linregress(x, y)
    r_squared_lib = r_value ** 2

    # Output with tolerance check
    print("=== Manual vs linregress Comparison ===")

    slope_diff = slope_manual - slope_lib
    if abs(slope_diff) < 1e-6:
        slope_diff = 0.0
    print(f"Slope:         manual = {slope_manual:.8f}, lib = {slope_lib:.8f}, Δ = {slope_diff:.2e}")

    intercept_diff = intercept_manual - intercept_lib
    if abs(intercept_diff) < 1e-6:
        intercept_diff = 0.0
    print(f"Intercept:     manual = {intercept_manual:.8f}, lib = {intercept_lib:.8f}, Δ = {intercept_diff:.2e}")

    r_diff = r_manual - r_value
    if abs(r_diff) < 1e-6:
        r_diff = 0.0
    print(f"Correlation r: manual = {r_manual:.8f}, lib = {r_value:.8f}, Δ = {r_diff:.2e}")

    r2_diff = r_squared_manual - r_squared_lib
    if abs(r2_diff) < 1e-6:
        r2_diff = 0.0
    print(f"R²:            manual = {r_squared_manual:.8f}, lib = {r_squared_lib:.8f}, Δ = {r2_diff:.2e}")

    pval_diff = p_manual - p_value
    if abs(pval_diff) < 1e-6:
        pval_diff = 0.0
    print(f"P-value:       manual = {p_manual:.8f}, lib = {p_value:.8f}, Δ = {pval_diff:.2e}")



    return {
        'slope_diff': slope_manual - slope_lib,
        'intercept_diff': intercept_manual - intercept_lib,
        'r_diff': r_manual - r_value,
        'r_squared_diff': r_squared_manual - r_squared_lib,
        'p_value_manual': p_manual,
        'p_value_lib': p_value,
        'p_value_diff': p_manual - p_value
    }
