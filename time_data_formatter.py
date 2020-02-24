import pandas as pd
import numpy as np


def time_data_formatter(filename):
    df = pd.read_csv(filename, sep=';')
    length = len(df)
    scramble = df.iloc[:, 1].to_numpy()
    times = np.empty(length, dtype=np.int64)
    time_of_day = np.empty(length, dtype=np.dtype('U8'))
    date = np.empty(length, dtype=np.dtype('U10'))
    penalty = np.empty(length, dtype=np.dtype('U3'))
    for j in range(length):
        i = length - 1 - j
        times[i] = int(df.iat[j, 0][0:2]) * 60000 + int(df.iat[j, 0][3:5]) * 1000 + int(df.iat[j, 0][6:9])
        if df.iat[j, 4] == 'yes':
            penalty[i] = 'DNF'
            times[i] = 60000
        elif df.iat[j, 3] == 'yes':
            penalty[i] = '+2'
            times[i] += 2000
        time_of_day[i] = df.iat[j, 2][11:16]+':00'
        date[i] = df.iat[j, 2][8:10]+'/'+df.iat[j, 2][5:7]+'/'+df.iat[j, 2][0:4]
    new_df = pd.DataFrame({'c0': times, 'c1': time_of_day, 'c2': date, 'c3': np.flip(scramble), 'c4': penalty})
    new_df.to_csv(filename[:len(filename) - 4] + '_result.txt', mode='w', header=False, index=False, sep=';')
