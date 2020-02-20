from datetime import datetime
from datetime import date
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from math import ceil

from Session import Session
from config import measures_of_interest


class Dataset:

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

    def add_data_point(self, time_s, scramble, penalty):
        new_df = self.append_line_to_data_file(int(time_s * 1000), datetime.now().strftime(
            "%H:%M:%S"), date.today().strftime("%d/%m/%Y"), scramble, penalty)
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
        for key, value in measures_of_interest.items():
            df = pd.DataFrame()
            for name, session in self.sessions_counting_towards_pbs.items():
                best_average = session.get_best_average(measures_of_interest[key][0],
                                                        measures_of_interest[key][1])
                df = df.append(best_average, ignore_index=True)
            df.sort_values(by=['c2'], inplace=True, ascending=True)
            times = df.iloc[:, 0].to_numpy()
            pb_time = times[0]
            for i in range(1, times.size):
                if times[i] > pb_time:
                    times[i] = pb_time
                elif not np.isnan(times[i]):
                    pb_time = times[i]
            df.iloc[:, 0] = times
            pbs.update({key: df})
        return pbs

    def plot_pbs(self):
        pbs = self.get_pbs()
        fig, ax = plt.subplots()
        min_time = 60000
        max_time = 0
        for key, value in pbs.items():
            times = value.iloc[:, 0].to_numpy()
            min_time = min(min(times), min_time)
            max_time = max(max(times), max_time)
            dates = value.iloc[:, 2].to_list()
            ax.plot(dates, times / 1000, color=measures_of_interest[key][2], marker='o')
            for i in range(1, times.size):
                times[i] = times[i] if not np.isnan(times[i]) else times[i - 1]
            ax.plot(dates, times / 1000, color=measures_of_interest[key][2], linestyle='-', label=key)

        fig.set_size_inches(8, 5)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
        fig.set_dpi(300)
        plt.yticks(np.arange(1 + ceil((max_time - min_time) / 1000)) + int(min_time / 1000))
        plt.ylabel('Seconds')
        plt.legend(loc='best')
        plt.title('PBs')
        plt.grid()
        plt.show()

    def append_line_to_data_file(self, c0, c1, c2, c3, c4):
        new_df = pd.DataFrame({'c0': [c0], 'c1': [c1], 'c2': [c2], 'c3': [c3], 'c4': [c4]})
        new_df.to_csv(self.data_file, mode='a', header=False, index=False, sep=';')
        return new_df
