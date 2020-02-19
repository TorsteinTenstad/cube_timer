import pandas as pd
import numpy as np
from scipy.special import stdtrit


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
        return self.compute_averages(self.df.size, int(0.1*self.df.size)).iloc[-1, 0]

    def compute_sample_variance(self):
        sample_mean = self.compute_sample_mean()
        times = self.df.iloc[:, 0].to_numpy(dtype=np.dtype(np.int64))
        return int(np.sum(np.square(times-sample_mean))/times.size)

    def compute_confidence_interval_global_mean(self):
        sample_mean = self.compute_sample_mean()
        sample_variance = self.compute_sample_variance()
        radius = int(stdtrit(self.df.size-1, 1-0.025)*np.sqrt(sample_variance/self.df.size))
        return [sample_mean - radius, sample_mean + radius]
