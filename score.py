
import pandas as pd
import numpy as np
import matplotlib as plt

# This script is intended to read a .csv file of historical cable modem statistics
# on signal to noise ratio and power levels upstream/downstream

d_cols = ['Timestamp', 'MAC', 'Direction', 'IfChannel', 'SNR', 'PWR']
raw_data = pd.read_csv(
    "~/Desktop/Billing_and_Nodes_Data/snr3.csv", names=d_cols)

# print(raw_data.head())
# print(raw_data.describe())

# Enter desired MAC and Timestamp
mac = '0001A6FF38DF'
timestamp = '2018-09-02 00:00:35.0010'

cm = raw_data[(raw_data.MAC == mac) & (
    raw_data.Timestamp == timestamp)]

print("Cable Modem MAC:", mac)
print("Timestamp: ", timestamp)

cm_snr = cm.at[0, 'SNR']
cm_pwr = cm.at[0, 'PWR']
cm_direction = cm.at[0, 'Direction']

# Returns a score out of 100 given a SNR value and a max SNR thresholdself.
# Greater the value, the better the score.


def snrscore(snr, max_snr):
    snr_score = cm_snr / max_snr * 100
    #print("SNR: ", snr)
    if snr_score > 100.0:
        snr_score = 100.0
    return snr_score


print("SNR: ", cm_snr)
print("SNR Score: ", snrscore(cm_snr, 40.0))

# Returns a score out of 100 given a PWR Level, upstream/downstream, a target
# power level, and a threshold for the difference of that target PWRself.
# PWR levels that are close to the target and threshold boundaries are higher.


def pwrscore(pwr, direction, thresh, target):
    if direction == 1:
        target = 45.0

    max = target + thresh
    min = target - thresh

    if pwr <= max and pwr >= min:
        pwr_score = 100.00
    elif pwr < min:
        pwr_score = (-1.0 / (pwr - min - 1)) * 100.0
    else:
        pwr_score = (1.0 / (pwr - max + 1)) * 100.0
    return pwr_score

# returns a data frame with only records for a given MAC address. Adds scores for
# SNR and PWR level to data frame.


def scorecm(data, mac):
    cm_data = data[data.MAC == mac]
    cm_data = cm_data.assign(SNR_Score=snrscore(cm_data.SNR, 40.0))
    cm_data = cm_data.assign(PWR_Score=pwrscore(
        cm_data.PWR, cm_data.Direction, 5.0, 0.0))
    return cm_data


print("PWR Score: ", pwrscore(cm_pwr, cm_direction, 5.0, 0.0))

print(scorecm(raw_data, mac))
