import pandas as pd
import numpy as np
from scipy.special import stdtrit
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from scipy import stats
from math import ceil

from config import measures_of_interest


class Session:

    def __init__(self, name):
        self.name = name
        self.df = pd.DataFrame()
        return

    def add_data_point(self, data_point):
        self.df = self.df.append(data_point)

    def print(self):
        print(self.df.to_string(formatters={'Date': lambda x: x.strftime('%d/%m/%Y')}))

    def hist(self, bin_width=1, show_middle_80=True):
        times = self.df.iloc[:, 0].to_numpy(dtype=np.dtype(np.int64))
        fig, ax = plt.subplots()
        min_tick = int(min(times) / 1000)
        min_tick += bin_width * int((min(times) / 1000 - min_tick) / bin_width)
        bin_n = (max(times) / 1000 - min_tick) / bin_width + 1
        bins = bin_width * np.arange(bin_n) + min_tick
        plt.hist(times / 1000, bins=bins, alpha=1, color='cornflowerblue', label='All times')
        if show_middle_80:
            discard_amount = int(0.1 * times.size)
            times_truncated = np.sort(times)
            times_truncated = times_truncated[discard_amount:times.size - discard_amount]
            min_tick_t = bin_width * int((min(times_truncated) / 1000 - min_tick) / bin_width)
            bin_n_t = (max(times_truncated) / 1000 - min_tick_t) / bin_width + 1
            bins_t = bin_width * np.arange(bin_n_t) + min_tick_t
            plt.hist(times_truncated / 1000, bins=bins, alpha=1, color='royalblue', label='Middle 80%')
        plt.xticks(bins)
        plt.xlabel('Seconds')
        plt.title('Histogram for session ' + self.name)
        fig.set_size_inches(bin_n * 0.5, 5)
        plt.show()

    def compute_averages(self, sample_len, discard_amount):
        session_length = len(self.df)
        averages_df = self.df.copy()
        if sample_len > session_length:
            averages_df['Solvetime'] = np.NaN * np.ones(session_length)
            averages_df['Time of day'] = np.NaN * np.ones(session_length)
            averages_df['Scramble'] = np.NaN * np.ones(session_length)
            averages_df['Penalty'] = np.NaN * np.ones(session_length)
        else:
            times = self.df.iloc[:, 0].to_numpy(dtype='Int64')
            averages = np.ones(times.size)
            for i in range(times.size - sample_len + 1):
                sample = times[i: i + sample_len]
                sample = np.sort(sample)
                sample = sample[discard_amount:sample.size - discard_amount]
                averages[i + sample_len - 1] = int(np.average(sample))
            averages[0:sample_len - 1] = np.NaN
            averages_df['Solvetime'] = averages
        return averages_df

    def get_best_average(self, sample_len, discard_amount):
        averages_df = self.compute_averages(sample_len, discard_amount).sort_values(by=['Solvetime'])
        averages_df.iat[0, 3] = np.NaN
        return averages_df.iloc[0, :]

    def compute_sample_mean(self):
        return int(np.average(self.df.iloc[:, 0].to_numpy(dtype=np.dtype(np.int64))))

    def compute_average(self):
        return self.compute_averages(len(self.df), int(0.1 * len(self.df))).iloc[-1, 0]

    def compute_sample_variance(self):
        sample_mean = self.compute_sample_mean()
        times = self.df.iloc[:, 0].to_numpy(dtype=np.dtype(np.int64))
        return int(np.sum(np.square(times - sample_mean)) / times.size)

    def compute_confidence_interval_global_mean(self, interval_size=0.95):
        sample_mean = self.compute_sample_mean()
        sample_variance = self.compute_sample_variance()
        radius = int(stdtrit(self.df.size - 1, 1 - (1 - interval_size) / 2) * np.sqrt(sample_variance / self.df.size))
        return np.asarray([sample_mean - radius, sample_mean + radius])

    def summary(self):
        if len(self.df) < 1:
            print('Can\'t show summary: No datapoints in session')
            return
        print('Session:', self.name)
        print('Solves:', len(self.df))
        for key, value in measures_of_interest.items():
            best_average = self.get_best_average(value[0], value[1])
            id_string = '' if np.isnan(best_average[0]) else '\t(' + str(best_average.name) + ')'
            print('Best ' + key[0].lower() + key[1:] + ':' + value[3] + str(best_average[0] / 1000) + id_string)
        print('Average:\t\t' + str(self.compute_average() / 1000))
        print('Total mean:\t\t' + str(self.compute_sample_mean() / 1000))
        print('Standard deviation:\t' + str(int(np.sqrt(self.compute_sample_variance())) / 1000))
        print('Confidence interval:\t' + str(self.compute_confidence_interval_global_mean() / 1000))

    def trend(self, sample_len=1, discard_amount=0):
        if len(self.df) < 2:
            print('Can\'t show trend: Too few datapoints')
            return
        times = self.df.iloc[:, 0].to_numpy(dtype=np.dtype(np.int64)) if sample_len == 1 else self.compute_averages(
            sample_len, discard_amount).iloc[sample_len - 1:, 0].to_numpy(dtype=np.dtype(np.int64))
        fig, ax = plt.subplots()
        x = np.arange(times.size)
        y = times
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        print('Estimated improvement per solve: %d' % -slope + 'ms')
        print('P-value: ', round(p_value, 3))
        plt.plot(x, y / 1000, 'bo', x, (slope * x + intercept) / 1000, 'r')
        plt.ylabel('Seconds')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        average_info = 'Averages of ' + str(sample_len) + ' (' + str(sample_len-2*discard_amount) + ' of ' + str(sample_len) + ')' if discard_amount != 0 else 'Means of ' + str(sample_len)
        title = 'Times' if sample_len == 1 else average_info
        plt.title(title + ', session: ' + self.name)
        plt.grid()
        plt.show()
