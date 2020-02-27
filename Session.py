import pandas as pd
import numpy as np
from scipy.special import stdtrit
import matplotlib.pyplot as plt
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
        print('\n', self.name)
        print(self.df)

    def hist(self, show_middle_80=True, bin_width=1):
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

    # def compute_means(self, sample_len):
    #     times = self.df.iloc[:, 0].to_numpy(dtype=np.dtype(np.int64))
    #     if sample_len > times.size:
    #         return pd.DataFrame(
    #             {'Solvetime': np.NaN * np.ones(sample_len), 'Time of day': np.NaN * np.ones(sample_len), 'Date': self.df.iat[0, 2],
    #              'Scramble': np.NaN * np.ones(sample_len)})
    #     means = np.zeros(times.size)
    #     for i in range(sample_len):
    #         means = np.add(means, np.roll(times, i))
    #     means /= sample_len
    #     means[0:sample_len - 1] = np.NaN
    #     means_df = self.df.copy()
    #     means_df.iloc[:, 0] = means.astype(dtype=np.dtype(np.int64))
    #     return means_df
    #
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
        averages_df.iat[0,3] = np.NaN
        return averages_df.iloc[0,:]

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
        print('Session:', self.name)
        print('Solves:', len(self.df))
        for key, value in measures_of_interest.items():
            best_average = self.get_best_average(value[0], value[1])
            id_string = '' if np.isnan(best_average[0]) else '\t(' + str(best_average.name) + ')'
            print('Best ' + key[0].lower() + key[1:] + ':' + value[3] + str(best_average[0] / 1000) + id_string)
        print('Total mean:\t\t' +  str(self.compute_sample_mean() / 1000))
        print('Confidence interval:\t' + str(self.compute_confidence_interval_global_mean() / 1000))

    def trend(self):
        times = self.df.iloc[:, 0].to_numpy(dtype=np.dtype(np.int64))
        fig, ax = plt.subplots()
        x = np.arange(times.size)
        y = times
        a, b = np.polyfit(x, y, 1)
        print('Estimated improvement per solve: %d' % -a + 'ms')
        plt.plot(x, y / 1000, 'bo', x, (a*x+b) / 1000, 'r')
        plt.ylabel('Seconds')
        plt.title('Times, session: ' + self.name)
        plt.grid()
        plt.show()
