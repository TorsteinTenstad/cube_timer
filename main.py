import keyboard
import time
from datetime import datetime
from datetime import date
import pandas as pd
import numpy as np
from scipy.special import stdtrit
import random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def scramble_checker(scramble):
    opposite_axis = [3, 4, 5, 0, 1, 2]
    error_count = 0
    for i in range(len(scramble)-2):
        if scramble[i] == scramble[i+1]:
            print('err1', scramble[i])
            error_count += 1
        if scramble[i] == scramble[i+2] and scramble[i] == opposite_axis[scramble[i+1]]:
            error_count += 1
            print('err2', scramble[i])
    if error_count > 0:
        print(scramble)
    return error_count


class Scrambler:

    moves = ['F', 'R', 'U', 'B', 'L', 'D', 'F2', 'R2', 'U2', 'B2', 'L2', 'D2', 'F\'', 'R\'', 'U\'', 'B\'', 'L\'', 'D\'', ]
    opposite_axis = [3, 4, 5, 0, 1, 2]

    def __init__(self, scramble_len):
        self.scramble_len = scramble_len

    def generate_scramble(self):
        scramble = np.zeros(self.scramble_len, dtype=np.dtype(np.int8))
        scramble[0] = random.randint(0, 5)
        for i in range(1, self.scramble_len):
            x = random.randint(0, 4)
            scramble[i] = 5 if (scramble[i-1] == x) else x
            if i >= 2 and scramble[i] == scramble[i-2] and self.opposite_axis[scramble[i]] == scramble[i-1]:
                new_x = random.randint(0, 3)
                if new_x == scramble[i-1]:
                    new_x = 5 if scramble[i-2] != 5 else 4
                elif new_x == scramble[i-2]:
                    new_x = 5 if scramble[i-1] != 5 else 4
                scramble[i] = new_x
        scramble += 6*np.random.randint(0, 3, self.scramble_len)
        scramble_str = ''
        for i in range(self.scramble_len):
            scramble_str += self.moves[scramble[i]] + ' '
        return scramble_str


class Dataset:

    measures_of_interest = {'Single': [1, 0, 'C2'],
                            'Average of 5': [5, 1, 'C1'],
                            'Average of 12': [12, 1, 'C0'],
                            'Average of 100': [100, 10, 'C3']}

    def __init__(self, data_file):
        self.data_file = data_file
        self.all_sessions = {}
        self.sessions_counting_towards_pbs = {}
        self.active_sessions = {}
        self.paused_sessions = {}
        self.stopped_sessions = {}
        self.sessions = {'start': self.active_sessions, 'pause': self.paused_sessions, 'end': self.stopped_sessions}

        df = pd.read_csv(self.data_file, sep=';')
        for index, row in df.iterrows():
            if row['c0'] == '---Session':
                self.set_session_status(row['c2'], row['c1'], row['c3'] == 'True')
            else:
                for session_name, session in self.active_sessions.items():
                    row['c2'] = pd.to_datetime(row['c2'], format="%d/%m/%Y")
                    session.add_data_point(row.to_frame().transpose())
        #
        # for session_dir in self.sessions.values():
        #     for session in session_dir.values():
        #         session.print_session()

    def add_data_point(self, time_s, scramble):
        new_df = self.append_line_to_data_file(int(time_s * 1000), datetime.now().strftime(
            "%H:%M:%S"), date.today().strftime("%d/%m/%Y"), scramble)
        for session_name, session in self.active_sessions.items():
            session.add_data_point(new_df)

    def set_session_status(self, session_name, new_status, counting_towards_pbs):
        for status, session_dict in self.sessions.items():
            if status != new_status:
                session_to_move = self.sessions[status].pop(session_name, None)
                if session_to_move:
                    self.sessions[new_status].update({session_name: session_to_move})
                    return session_to_move
        if new_status == 'start':
            new_session = Session(session_name)
            if counting_towards_pbs:
                self.sessions_counting_towards_pbs.update({session_name: new_session})
            self.all_sessions.update({session_name: new_session})
            self.active_sessions.update({session_name: new_session})
            return new_session

    def log_session_action(self, session_name, new_status, counting_towards_pbs):
        if self.set_session_status(session_name, new_status, counting_towards_pbs):
            self.append_line_to_data_file('---Session', new_status, session_name, counting_towards_pbs)

    def get_pbs(self):
        pbs = {}
        for key, value in self.measures_of_interest.items():
            df = pd.DataFrame()
            for name, session in self.sessions_counting_towards_pbs.items():
                best_average = session.get_best_average(self.measures_of_interest[key][0], self.measures_of_interest[key][1])
                df = df.append(best_average, ignore_index=True)
            df.sort_values(by=['c2'], inplace=True, ascending=True)
            times = df.iloc[:, 0].to_numpy()
            for i in range(1, times.size):
                times[i] = min(times[i], times[i-1])
            df.iloc[:, 0] = times
            pbs.update({key: df})
        return pbs

    def plot_pbs(self):
        pbs = self.get_pbs()
        fig, ax = plt.subplots()
        for key, value in pbs.items():
            times = value.iloc[:, 0].to_numpy()
            dates = value.iloc[:, 2].to_list()
            ax.plot(dates, times/1000, color=self.measures_of_interest[key][2], marker='o')
            for i in range(1, times.size):
                times[i] = times[i] if not np.isnan(times[i]) else times[i-1]
            ax.plot(dates, times/1000, color=self.measures_of_interest[key][2], linestyle='-', label=key)

        fig.set_size_inches(8, 5)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
        fig.set_dpi(300)
        plt.yticks(np.arange(18)+17)
        plt.ylabel('Seconds')
        plt.legend(loc='best')
        plt.title('PBs')
        plt.grid()
        plt.show()

    def append_line_to_data_file(self, c0, c1, c2, c3):
        new_df = pd.DataFrame({'c0': [c0], 'c1': [c1], 'c2': [c2], 'c3': [c3]})
        new_df.to_csv(self.data_file, mode='a', header=False, index=False, sep=';')
        return new_df


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


class Timer:

    def __init__(self, send_time_func, scramble_func, trigger_key='space', quit_key='q', min_hold_time=1):
        self.send_time_func = send_time_func
        self.scramble_func = scramble_func
        self.trigger_key = trigger_key
        self.quit_key = quit_key
        self.min_hold_time = min_hold_time

    def record_time(self):
        scramble = self.scramble_func()
        print(scramble)
        ready = False
        while not ready:
            keyboard.wait(self.trigger_key, suppress=True, trigger_on_release=False)
            initial_t = time.time()
            while True:
                if time.time() - initial_t > self.min_hold_time:
                    print('Ready')
                    ready = True
                    break
                elif not keyboard.is_pressed(self.trigger_key):
                    break

        keyboard.wait(self.trigger_key, suppress=True, trigger_on_release=True)
        t = time.time()
        keyboard.wait(self.trigger_key)
        recorded_time = time.time() - t
        self.send_time_func(recorded_time, scramble)
        print('Time:', recorded_time)
        keyboard.wait(self.trigger_key, suppress=True, trigger_on_release=True)

    def run(self):
        state = 0
        recorded_time = -1
        new_scramble = self.scramble_func()
        print(new_scramble)
        while True:
            if state == 0:
                if keyboard.is_pressed(self.trigger_key):
                    hold_start = time.time()
                    state = 1
                elif keyboard.is_pressed(self.quit_key):
                    if recorded_time > 0:
                        self.send_time_func(recorded_time, scramble)
                    return
            if state == 1:
                if time.time() - hold_start > self.min_hold_time:
                    print('Ready')
                    if recorded_time > 0:
                        self.send_time_func(recorded_time, scramble)
                    state = 2
                elif not keyboard.is_pressed(self.trigger_key):
                    state = 0
            if state == 2:
                if not keyboard.is_pressed(self.trigger_key):
                    start_time = time.time()
                    state = 3
            if state == 3:
                if keyboard.is_pressed(self.trigger_key):
                    recorded_time = time.time() - start_time
                    print('Time: ', recorded_time)
                    scramble = new_scramble
                    new_scramble = self.scramble_func()
                    print(new_scramble)
                    state = 4
            if state == 4:
                if not keyboard.is_pressed(self.trigger_key):
                    state = 0


def main():
    random.seed(time.time())
    scrambler = Scrambler(20)
    main_data_set = Dataset('testfile.txt')
    timer = Timer(main_data_set.add_data_point, scrambler.generate_scramble)
    #main_data_set.plot_pbs()
    timer.run()

if __name__ == "__main__":
    main()
