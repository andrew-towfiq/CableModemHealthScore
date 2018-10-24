# 10/23/2018
import pandas as pd
import numpy as np
import sys

# This script is intended to read a .csv file of historical cable modem statistics
# on signal to noise ratio and power levels upstream/downstream

d_cols = ['Timestamp', 'MAC', 'Direction', 'IfChannel', 'SNR', 'PWR']
raw_data = pd.read_csv(
    "~/Desktop/Billing_and_Nodes_Data/snr3.csv", names=d_cols)
# print(raw_data.head())
# print(raw_data.describe())

# Enter desired MAC and Timestamp
def_mac = '0001A6FF38DF'
def_timestamp = '2018-09-02 00:00:35.0010'

cm = raw_data[(raw_data.MAC == def_mac) & (
    raw_data.Timestamp == def_timestamp)]
cm_snr = cm.at[0, 'SNR']
print("Cable Modem MAC:", def_mac)
print("Timestamp: ", def_timestamp)
print("SNR: ", cm_snr)

# Threshold of "ideal" snr level.
max_snr = 40.0
snr_score = cm_snr / max_snr * 100

if snr_score > 100.0:
    snr_score = 100.0

print("SNR Score: ", snr_score)

direction = cm.at[0, 'Direction']
print(direction)

cm_pwr = cm.at[0, 'PWR']
pwr_score = 100.0
target = 0.0
thresh = 5.0
if(direction == 1):
    target = 45.0
    diff = target - cm_pwr
    if(abs(diff) > thresh):
        pwr_score = 
