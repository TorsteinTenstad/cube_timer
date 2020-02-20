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
        self.df = self.df.append(data_point, ignore_index=True)

    def print_session(self):
        print('\n', self.name)
        print(self.df)

    def plot_histogram(self):
        times = self.df.iloc[:, 0].to_numpy(dtype=np.dtype(np.int64))
        fig, ax = plt.subplots()
        plt.hist(times/1000, bins=ceil((max(times) - min(times)) / 1000))
        tick_n = 1 + ceil((max(times) - min(times)) / 1000)
        plt.xticks(np.arange(tick_n) + int(min(times) / 1000))
        fig.set_size_inches(tick_n*0.25, 5)
        plt.show()

    def compute_means(self, sample_len):
        times = self.df.iloc[:, 0].to_numpy(dtype=np.dtype(np.int64))
        if sample_len > times.size:
            return pd.DataFrame({'c0': np.NaN*np.ones(sample_len), 'c1': np.NaN*np.ones(sample_len), 'c2': self.df.iat[0, 2], 'c3': np.NaN*np.ones(sample_len)})
        means = np.zeros(times.size)
        for i in range(sample_len):
            means = np.add(means, np.roll(times, i))
        means /= sample_len
        means[0:sample_len-1] = np.NaN
        means_df = self.df.copy()
        means_df.iloc[:, 0] = means.astype(dtype=np.dtype(np.int64))
        return means_df

    def compute_averages(self, sample_len, discard_amount):
        times = self.df.iloc[:, 0].to_numpy(dtype=np.dtype(np.int64))
        if sample_len > times.size:
            return pd.DataFrame({'c0': np.NaN*np.ones(sample_len), 'c1': np.NaN*np.ones(sample_len), 'c2': self.df.iat[0, 2], 'c3': np.NaN*np.ones(sample_len)})
        averages = np.ones(times.size)
        for i in range(sample_len, times.size+1):
            sample = times[i-sample_len: i]
            for j in range(discard_amount):
                sample = np.delete(sample, sample.argmin())
                sample = np.delete(sample, sample.argmax())
            averages[i-1] = np.average(sample)
        averages[0:sample_len-1] = np.NaN
        averages_df = self.df.copy()
        averages_df.iloc[:, 0] = averages.astype(dtype=np.dtype(np.int64))
        return averages_df

    def get_best_average(self, sample_len, discard_amount):
        row = self.compute_averages(sample_len, discard_amount)
        row = row.iloc[sample_len-1:, :].sort_values(by=['c0'])
        row.iloc[:, 3] = self.name
        return row.iloc[0, :]

    def compute_sample_mean(self):
        return int(np.average(self.df.iloc[:, 0].to_numpy(dtype=np.dtype(np.int64))))

    def compute_average(self):
        return self.compute_averages(len(self.df), int(0.1*len(self.df))).iloc[-1, 0]

    def compute_sample_variance(self):
        sample_mean = self.compute_sample_mean()
        times = self.df.iloc[:, 0].to_numpy(dtype=np.dtype(np.int64))
        return int(np.sum(np.square(times-sample_mean))/times.size)

    def compute_confidence_interval_global_mean(self, interval_size=0.95):
        sample_mean = self.compute_sample_mean()
        sample_variance = self.compute_sample_variance()
        radius = int(stdtrit(self.df.size-1, 1-(1-interval_size)/2)*np.sqrt(sample_variance/self.df.size))
        return [sample_mean - radius, sample_mean + radius]

    def print_summary(self):
        print('Session:', self.name)
        print('Solves:', len(self.df))
        for key, value in measures_of_interest.items():
            best_average = self.get_best_average(value[0], value[1])
            print('Best', key[0].lower() + key[1:] + ':' + value[3], best_average[0]/1000)
        print('Total mean:\t\t\t', self.compute_sample_mean()/1000)
        print('Confidence interval:', self.compute_confidence_interval_global_mean())
