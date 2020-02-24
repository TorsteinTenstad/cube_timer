import pandas as pd
import numpy as np


def time_data_formatter(filename):
    df = pd.read_csv(filename, sep=';')
    times_str = df.iloc[:, 0].to_numpy()
    scramble = df.iloc[:, 1].to_numpy()
    date_and_time = df.iloc[:, 2].to_numpy()
    times = np.empty(times_str.size, dtype=np.int64)
    time_of_day = np.empty(times_str.size, dtype=np.dtype('U8'))
    date = np.empty(times_str.size, dtype=np.dtype('U10'))
    penalty = np.empty(times_str.size, dtype=np.dtype('U3'))
    for i in range(len(df)):
        times[i] = int(df.iat[i, 0][0:2]) * 60000 + int(df.iat[i, 0][3:5]) * 1000 + int(df.iat[i, 0][6:9])
        if df.iat[i, 4] == 'yes':
            penalty[i] = 'DNF'
            times[i] = 60000
        elif df.iat[i, 3] == 'yes':
            penalty[i] = '+2'
            times[i] += 2000
        time_of_day[i] = df.iat[i, 2][11:16]+':00'
        date[i] = df.iat[i, 2][8:10]+'/'+df.iat[i, 2][5:7]+'/'+df.iat[i, 2][0:4]
    x = np.arange(times_str.size)
    new_df = pd.DataFrame({'c0': times, 'c1': time_of_day, 'c2': date, 'c3': scramble, 'c4': penalty})
    new_df.to_csv(filename[:len(filename) - 4] + '_result.txt', mode='w', header=False, index=False, sep=';')
