import mysql.connector
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
import MySQLdb

import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np
from scipy import stats
import pandas as pd

# given a mac address, this function retrieves all other mac addresses that share
# the same interfaces as the mac passed to this function. returns dictionary
# of interfaces as keys, and list of macs as values.


def fetchall_mac_neighbors(mac):
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        arr_ifIndex = fetchall_ifIndex_mac(mac)
        dict_neighbors = {}
        for interface in arr_ifIndex:
            int_if = int(interface)
            query_mac = "SELECT mac FROM snr_pl_c WHERE ifIndex = '" + \
                str(int_if) + "' group by MAC"
            cursor.execute(query_mac)
            macs = cursor.fetchall()
            dict_neighbors[int_if] = macs

        return(dict_neighbors)
    except Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


def fetchall_latest_ifIndex_mac(mac):
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        begin_query = "select id, ts, mac, ifIndex, snr, pl, snr_score, pl_score FROM (select max(id) as id from snr_pl_h where mac='"
        end_query = "' group by ifIndex) as A JOIN v_snr_pl_scores using (id)"
        final_query = begin_query + mac + end_query
        # print(final_query)
        cursor.execute(final_query)
        rows = cursor.fetchall()

        for row in rows:
            print(row)
        print('Total Row(s):', cursor.rowcount)
        return(rows)

    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()

# this function fetches all mac addresses using a given interface in the database
# returns an array


def fetchall_mac_ifIndex(interface):
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
    except Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

# This funciton returns a table from Mysql of all the interfaces (ifIndexes)
# for a given MAC address from a cable modem. returns numpy array


def fetchall_ifIndex_mac(mac):
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        select_query = "SELECT ifIndex FROM snr_pl_h"
        where_query = " WHERE mac = '" + mac + "' GROUP BY ifIndex"
        final_query = select_query + where_query
        # print(final_query)
        cursor.execute(final_query)
        rows = cursor.fetchall()
        df = pd.DataFrame([[ij for ij in i] for i in rows])
        df.rename(columns={0: 'IfIndex'}, inplace=True)
        return(df.values)

    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()

# Returns all timestamps for scores given a specific ifIndex and cable modem mac
# address.


def fetchall_ifIndex_scores(mac, interface):
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        select_query = "SELECT ts, direction, ifIndex, snr_score, pl_score FROM v_snr_pl_scores"
        where_query = " WHERE mac = '" + mac + "' AND ifIndex = '" + interface + "'"
        final_query = select_query + where_query
        print(final_query)
        cursor.execute(final_query)
        rows = cursor.fetchall()
        for row in rows:
            print(row)

        print('Total Row(s):', cursor.rowcount)
        return(rows)
    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()


# plot scores or values for a given mac address and one interface it is connected to
def plot_ifIndex_mac(mac, interface):
    try:
        # Connect to MySQLdb
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()

        # create query to return timestamp, mac, interface, snr and pl scores for specified interface
        select_query = "SELECT ts, mac, ifIndex, snr_score, pl_score, snr, pl, direction FROM v_snr_pl_scores "
        where_query = "WHERE mac = '" + mac + "' AND ifIndex = '" + interface + "'"
        final_query = select_query + where_query
        print(final_query)
        cursor.execute(final_query)
        rows = cursor.fetchall()

        # put Mysql query results into data frame to process for plotly
        df = pd.DataFrame([[ij for ij in i] for i in rows])
        df.rename(columns={0: 'Timestamp', 1: 'MAC_Address',
                           2: 'IfIndex', 3: 'SNR_Score', 4: 'PL_Score', 5: 'SNR', 6: 'PL', 7: 'Direction'}, inplace=True)
        df['Timestamp_S'] = pd.to_numeric(df.Timestamp)
        ans = input("Do you wish to plot scores, values, or both? (s/v/b): ")
        if ans == 's':
            plot_df_scores(df)
        elif ans == 'v':
            plot_df_raw(df)
        elif ans == 'b':
            plot_df_both(df)
        else:
            print("Please enter a valid answer ('s' or 'v' or 'b')")

    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()

# given a dataframe of scores and values, plots both with a regression line for power
# level and snr.


def plot_df_both(df):
    if df.empty:
        print("df is empty")
    else:
        plot_name = 'CM_' + mac + '_IF_' + interface + '_values_scores'
        xi = df.Timestamp_S
        y_snr_score = df.SNR_Score
        y_snr = df.SNR
        y_pl_score = df.PL_Score
        y_pl = df.PL

        slope_snr_score, intercept_snr_score, r_value_snr_score, p_value_snr_score, std_err_snr_score = stats.linregress(
            xi, y_snr_score)
        slope_pl_score, intercept_pl_score, r_value_pl_score, p_value_pl_score, st_err_pl_score = stats.linregress(
            xi, y_pl_score)
        slope_snr, intercept_snr, r_value_snr, p_value_snr, std_err_snr = stats.linregress(
            xi, y_snr)
        slope_pl, intercept_pl, r_value_pl, p_value_pl, st_err_pl = stats.linregress(
            xi, y_pl)

        line_pl_score = slope_pl_score * xi + intercept_pl_score
        line_snr_score = slope_snr_score * xi + intercept_snr_score
        line_pl = slope_pl * xi + intercept_pl
        line_snr = slope_snr * xi + intercept_snr

        fig = {
            'data': [
                {
                    'x': df.Timestamp,
                    'y': df.SNR_Score,
                    'mode': 'markers',
                    'name': 'SNR Score'},

                {
                    'x': df.Timestamp,
                    'y': df.PL_Score,
                    'mode': 'markers',
                    'name': 'PL Score'},

                {
                    'x': df.Timestamp,
                    'y': df.SNR,
                    'mode': 'markers',
                    'name': 'SNR',
                    'yaxis': 'y2'},

                {
                    'x': df.Timestamp,
                    'y': df.PL,
                    'mode': 'markers',
                    'name': 'PL',
                    'yaxis': 'y2'},

                {
                    'x': df.Timestamp,
                    'y': line_snr_score,
                    'mode': 'lines',
                    'name': 'SNR Score Fit'},
                {
                    'x': df.Timestamp,
                    'y': line_pl_score,
                    'mode': 'lines',
                    'name': 'PL Score Fit'},
                {
                    'x': df.Timestamp,
                    'y': line_snr,
                    'mode': 'lines',
                    'name': 'SNR Fit',
                    'yaxis': 'y2'},
                {
                    'x': df.Timestamp,
                    'y': line_pl,
                    'mode': 'lines',
                    'name': 'PL Fit',
                    'yaxis': 'y2'}
            ],
            'layout': {
                'title': plot_name,
                'xaxis': {'title': 'Timestamp'},
                'yaxis': {'title': 'Score',
                          'range': [0.0, 100.0],
                          'side': 'left'},
                'yaxis2': {'title': 'Values',
                           'side': 'right',
                           'overlaying': 'y'}
            }
        }
        url = py.plot(fig, filename=plot_name)


# plots SNR and PL scores to plot.ly with linear regression given pandas
# dataframe from one mac and one interface

def plot_df_scores(df):

    if df.empty:
        print("df is empty")

    else:
        plot_name = 'CM_' + mac + '_IF_' + interface + '_scores'
        xi = df_up.Timestamp_S
        y_snr_score = df.SNR_Score
        y_pl_score = df.PL_Score

        slope_snr_score, intercept_snr_score, r_value_snr_score, p_value_snr_score, std_err_snr_score = stats.linregress(
            xi, y_snr_score)
        slope_pl_score, intercept_pl_score, r_value_pl_score, p_value_pl_score, st_err_pl_score = stats.linregress(
            xi, y_pl_score)

        line_pl_score = slope_pl_score * xi + intercept_pl_score
        line_snr_score = slope_snr_score * xi + intercept_snr_score

        fig = {
            'data': [
                {
                    'x': df.Timestamp,
                    'y': df.SNR_Score,
                    'mode': 'markers',
                    'name': 'SNR Score'},
                {
                    'x': df.Timestamp,
                    'y': df.PL_Score,
                    'mode': 'markers',
                    'name': 'PL Score'},
                {
                    'x': df.Timestamp,
                    'y': line_snr_score,
                    'mode': 'lines',
                    'name': 'SNR Score Fit'},
                {
                    'x': df.Timestamp,
                    'y': line_pl_score,
                    'mode': 'lines',
                    'name': 'PL Score Fit'}
            ],
            'layout': {
                'title': plot_name,
                'xaxis': {'title': 'Timestamp'},
                'yaxis': {'title': 'Score',
                          'range': [0.0, 100.0]}
            }
        }
        url = py.plot(fig, filename=plot_name)


# plots SNR and PL raw values to plot.ly with linear regression given pandas
# dataframe from one mac and one interface


def plot_df_raw(df):

    if df.empty:
        print("df is empty")

    else:
        plot_name = 'CM_' + mac + '_IF_' + interface + '_values'
        xi = df.Timestamp
        y_snr = df.SNR
        y_pl = df.PL

        slope_snr, intercept_snr, r_value_snr, p_value_snr, std_err_snr = stats.linregress(
            xi, y_snr)
        slope_pl, intercept_pl, r_value_pl, p_value_pl, st_err_pl = stats.linregress(
            xi, y_pl)

        line_pl = slope_pl * xi + intercept_pl
        line_snr = slope_snr * xi + intercept_snr
        fig = {
            'data': [
                {
                    'x': df.Timestamp,
                    'y': df.SNR,
                    'mode': 'markers',
                    'name': 'SNR Upstream'},
                {
                    'x': df.Timestamp,
                    'y': df.PL,
                    'mode': 'markers',
                    'name': 'PL Upstream'},
                {
                    'x': df.Timestamp,
                    'y': line_snr,
                    'mode': 'lines',
                    'name': 'SNR Fit'},
                {
                    'x': df.Timestamp,
                    'y': line_pl,
                    'mode': 'lines',
                    'name': 'PL Fit'}
            ],
            'layout': {
                'title': plot_name,
                'xaxis': {'title': 'Timestamp'},
                'yaxis': {'title': 'Values (dBmV)'}
            }
        }
        url = py.plot(fig, filename=plot_name)


def health_score_hist():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        select_query = "SELECT avg_log_health, w_avg_log_health, avg_stddev_health, w_avg_stddev_health from cm_health_scores"
        cursor.execute(select_query)
        rows = cursor.fetchall()
        df = pd.DataFrame([[ij for ij in i] for i in rows])
        df.rename(columns={0: 'avg_log_health', 1: 'w_avg_log_health',
                           2: 'avg_stddev_health', 3: 'w_avg_stddev_health'}, inplace=True)
        a_log = df['avg_log_health'].values
        w_log = df['w_avg_log_health'].values
        a_std = df['avg_stddev_health'].values
        w_std = df['w_avg_stddev_health'].values

        trace1 = go.Histogram(
            x=w_log,
            nbinsx=100
        )

        data = [trace1]
        layout = go.Layout(barmode='overlay')
        fig = go.Figure(data=data, layout=layout)
        py.iplot(fig, filename='Weighted Average Log Health Score Histogram')
    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    #mac = input("Enter a desired MAC address: ")
    # interface = input(
    #    "Enter a desired Interface: ")
    # fetchall_mac_neighbors(mac)
    #plot_ifIndex_mac(mac, interface)
    health_score_hist()
