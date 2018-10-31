
import pandas as pd
import numpy as np
import matplotlib as plt

# This script is intended to read a .csv file of historical cable modem statistics
# on signal to noise ratio and power levels upstream/downstream

d_cols = ['Timestamp', 'MAC', 'Direction', 'IfChannel', 'SNR', 'PWR']
raw_data = pd.read_csv(
    "~/Desktop/Billing_and_Nodes_Data/snr2.csv", names=d_cols)

print(raw_data.head())
# print(raw_data.describe())

# Enter desired MAC and Timestamp

mac = '0001A6FF38DF'
# timestamp = '2018-09-02 00:00:35.0010'

# cm = raw_data[(raw_data.MAC == mac) & (
# raw_data.Timestamp == timestamp)]

# print("Cable Modem MAC:", mac)
# print("Timestamp: ", timestamp)

# cm_snr = cm.at[0, 'SNR']
# cm_pwr = cm.at[0, 'PWR']
# cm_direction = cm.at[0, 'Direction']

# Returns a score out of 100 given a SNR value and a max SNR thresholdself.
# Greater the value, the better the score.


def snrscore(snr, max_snr):
    snr_score = snr / max_snr * 100
    # print("SNR: ", snr)
    if snr_score > 100.0:
        snr_score = 100.0
    return snr_score

# print("SNR: ", cm_snr)
# print("SNR Score: ", snrscore(cm_snr, 40.0))

# Returns a score out of 100 given a PWR Level, upstream/downstream, a target
# power level, and a threshold for the difference of that target PWR.
# PWR levels that are close to the target and threshold boundaries are higher.


def pwrscore(pwr, direction, thresh, target):
    target = getPwrTarget(direction)

    diff = abs(pwr - target)
    if (diff <= thresh):
        pwr_score = 100.0
    else:
        pwr_score = 100.0 / (diff + 1)
    return pwr_score
    return pwr_score


def getPwrTarget(direction):
    if direction == 1:
        return 45.0
    else:
        return 0.0

# returns a data frame with only records for a given MAC address. Adds scores for
# SNR and PWR level to data frame.


def scorecm(data):
    # cm_data = data[data.MAC == mac]
    cm_data = data
    cm_data.loc[:, 'SNR_Score'] = 0.0
    cm_data.loc[:, 'PWR_Score'] = 0.0
    # print("cm_data: ", cm_data)
    # print("cm_data_size: ", len(cm_data))
    for i in range(len(cm_data.MAC)):
        print(i, ":", cm_data.loc[i, 'MAC'], ";",
              cm_data.loc[i, 'SNR'], ";", cm_data.loc[i, 'PWR'])
        cm_snrscore = snrscore(cm_data.loc[i, 'SNR'], 40.0)
        cm_pwrscore = pwrscore(
            cm_data.loc[i, 'PWR'], cm_data.loc[i, 'Direction'], 5.0, 0.0)
        cm_data.loc[i, 'SNR_Score'] = cm_snrscore
        cm_data.loc[i, 'PWR_Score'] = cm_pwrscore
    return cm_data


cm_scores = scorecm(raw_data)
print(cm_scores.head())
cm_scores.to_csv("~/Desktop/Billing_and_Nodes_Data/cm_scores.csv")
