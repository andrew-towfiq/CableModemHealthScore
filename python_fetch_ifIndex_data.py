import mysql.connector
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
import MySQLdb

import plotly.plotly as py
import plotly.graph_objs as go
from numpy import arange, array, ones
from scipy import stats
import pandas as pd
import datetime as dt


# This funciton returns a table from Mysql of all the intervaces (ifIndexes)
# for a given MAC address from a cable modem.


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
        for row in rows:
            print(row)
        print('Total Row(s):', cursor.rowcount)
        return(rows)

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

# plot scores for a given mac address and one interface it is connected to


def plot_ifIndex_mac_scores(mac, interface):
    try:

        # Connect to MySQLdb
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()

        # create query to return timestamp, mac, interface, snr and pl scores for specified interface
        select_query = "SELECT ts, mac, ifIndex, snr_score, pl_score, direction FROM v_snr_pl_scores "
        where_query = " WHERE mac = '" + mac + "' AND ifIndex = '" + interface + "'"
        final_query = select_query + where_query
        print(final_query)
        cursor.execute(final_query)
        rows = cursor.fetchall()

        # put Mysql query results into data frame to process for plotly
        df = pd.DataFrame([[ij for ij in i] for i in rows])
        df.rename(columns={0: 'Timestamp', 1: 'MAC_Address',
                           2: 'IfIndex', 3: 'SNR_Score', 4: 'PL_Score', 5: 'Direction'}, inplace=True)
        df.Timestamp = pd.to_numeric(df.Timestamp)
        df_up = df[df.Direction == 1]
        df_down = df[df.Direction == 2]

        if df_up.empty:
            print("Df_up is empty")
        else:

            fig = {
                'data': [
                    {
                        'x': df_up.Timestamp,
                        'y': df_up.SNR_Score,
                        'mode': 'markers',
                                'name': 'SNR Score Upstream'},
                    {
                        'x': df_up.Timestamp,
                        'y': df_up.PL_Score,
                        'mode': 'markers',
                                'name': 'PL Score Upstream'}
                ],
                'layout': {
                    'xaxis': {'title': 'Timestamp'},
                    'yaxis': {'title': 'Score'}
                }
            }
            plot_name = 'CM_' + mac + '_IF_' + interface + '_upstream'
            url = py.plot(fig, filename=plot_name)

        if df_down.empty:
            print("df_down is empty")
        else:
            plot_name = 'CM_' + mac + '_IF_' + interface + '_upstream'
            xi = df_down.Timestamp
            y_snr = df_down.SNR_Score
            y_pl = df_down.PL_Score
            slope_snr, intercept_snr, r_value_snr, p_value_snr, std_err_snr = stats.linregress(
                xi, y_snr)
            slope_pl, intercept_pl, r_value_pl, p_value_pl, st_err_pl = stats.linregress(
                xi, y_pl)
            line_pl = slope_pl * xi + intercept_pl
            line_snr = slope_snr * xi + intercept_snr
            fig = {
                'data': [
                    {
                        'x': df_down.Timestamp,
                        'y': df_down.SNR_Score,
                        'mode': 'markers',
                        'name': 'SNR Score Upstream'},
                    {
                        'x': df_down.Timestamp,
                        'y': df_down.PL_Score,
                        'mode': 'markers',
                        'name': 'PL Score Upstream'},
                    {
                        'x': xi,
                        'y': line_snr,
                        'mode': 'lines',
                        'name': 'SNR Score Fit'},
                    {
                        'x': xi,
                        'y': line_pl,
                        'mode': 'lines',
                        'name': 'PL Score Fit'}
                ],
                'layout': {
                    'title': plot_name,
                    'xaxis': {'title': 'Timestamp'},
                    'yaxis': {'title': 'Score'}
                }
            }

            url = py.plot(fig, filename=plot_name)
    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    mac = input("Enter a desired MAC address: ")
    # print(mac)
    # fetchall_ifIndex_mac(mac)
    interface = input(
        "Enter a desired Interface from above output: ")
    # fetchall_ifIndex_scores(mac, interface)
    plot_ifIndex_mac_scores(mac, interface)
