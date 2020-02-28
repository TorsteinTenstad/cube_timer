from datetime import datetime
from datetime import date
import pandas as pd
import numpy as np
import os as os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from math import ceil

from Session import Session
from config import measures_of_interest


class Dataset:

    def __init__(self, data_file):
        self.df = pd.DataFrame()
        self.data_file = data_file
        self.all_sessions = {}
        self.sessions_counting_towards_pbs = {}
        self.active_sessions = {}
        self.paused_sessions = {}
        self.stopped_sessions = {}
        self.sessions = {'all': self.all_sessions, 'start': self.active_sessions, 'pause': self.paused_sessions, 'end': self.stopped_sessions, 'pb': self.sessions_counting_towards_pbs}

        if os.path.exists(self.data_file):
            self.df = pd.read_csv(self.data_file, sep=';')
            self.df.apply(self.load_line_into_dataset, axis=1)

        else:
            self.append_line_to_data_file('Solvetime', 'Time of day', 'Date', 'Scramble', 'Penalty')
            self.log_session_action('global_session', 'start', False)

    def load_line_into_dataset(self, row):
        if row['Solvetime'] == '---Session':
            self.set_session_status(row['Date'], row['Time of day'], row['Scramble'] == 'True')
        else:
            for session_name, session in self.active_sessions.items():
                session.add_data_point(row.to_frame().transpose())

    def add_data_point(self, time_s, scramble, penalty):
        new_df = self.append_line_to_data_file(int(time_s * 1000), datetime.now().strftime(
            "%H:%M:%S"), date.today().strftime("%d/%m/%Y"), scramble, penalty)
        self.df = self.df.append(new_df)
        for session_name, session in self.active_sessions.items():
            session.add_data_point(new_df)

    def print_number_of_solves(self):
        for session_name, session in self.active_sessions.items():
            if session_name in self.sessions_counting_towards_pbs.keys():
                print('Solves in session ' + session_name + ':', len(session.df) + 1)

    def lst(self, type='start'):
        table = []
        for session_name, session in self.sessions[type].items():
            setattr(self, session_name, session)
            start_date = '-' if session.df.empty else session.df.iat[0, 2]
            end_date = '-' if session_name in list(self.active_sessions.keys()) else session.df.iat[-1, 2]
            table.append([session_name, str(len(session.df)), start_date, end_date])
        print(pd.DataFrame(table, columns=['Name', 'Solves', 'Start date', 'End date']).to_string(index=False))

    def set_session_status(self, session_name, new_status, counting_towards_pbs):
        for status in ['start', 'pause', 'end']:
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

    def log_session_action(self, session_name, new_status='start', counting_towards_pbs=True):
        if self.set_session_status(session_name, new_status, counting_towards_pbs):
            counting_towards_pbs = counting_towards_pbs if new_status == 'start' else ''
            self.append_line_to_data_file('---Session', new_status, session_name, counting_towards_pbs, '')

    def get_auto_sessions(self, status):
        return_list = []
        for session_name in self.sessions[status]:
            if session_name[0] == 's' and session_name[1:].isnumeric():
                return_list.append(session_name)
        return return_list

    def auto_start(self):
        existing_active_auto_sessions = self.get_auto_sessions('start')
        if len(existing_active_auto_sessions) == 0:
            existing_auto_sessions = self.get_auto_sessions('all')
            newest_session_num = 0
            for session_name in existing_auto_sessions:
                newest_session_num = max(newest_session_num, int(session_name[1:]))
            session_name = 's' + str(newest_session_num + 1)
            print('Session ' + session_name + ' started')
            self.log_session_action(session_name, 'start')
        else:
            print('Active sessions are preventing automatic start of new session')
        print('Active sessions:')
        self.lst()

    def auto_end(self):
        existing_active_auto_sessions = self.get_auto_sessions('start')
        if len(existing_active_auto_sessions) == 0:
            print('No active automated sessions')
        elif len(existing_active_auto_sessions) == 1:
            print('Session ended: ' + existing_active_auto_sessions[0])
            self.log_session_action(existing_active_auto_sessions[0], 'end', )
        elif len(existing_active_auto_sessions) > 1:
            print('Error: Multiple automated sessions running')
            print('Active sessions:')
            self.lst()

    def get(self, index):
        pd.set_option('max_colwidth', 1000)
        row = self.df.loc[index]
        print(row.to_string())

    def summaries(self):
        summaries = {}
        for key, value in measures_of_interest.items():
            df = pd.DataFrame(columns=['Solvetime', 'Time of day', 'Date', 'Scramble', 'Penalty'])
            for name, session in self.sessions_counting_towards_pbs.items():
                best_average = session.get_best_average(measures_of_interest[key][0],
                                                        measures_of_interest[key][1])
                df = df.append(best_average, ignore_index=False)
            df.sort_values(by=['Date'], inplace=True, ascending=True)
            summaries.update({key: df})
        return summaries

    def print(self):
        print(self.df.to_string())

    def pbs(self):
        pbs = self.summaries()
        if list(pbs.values())[0].empty:
            print('Dataset does not include any sessions that count towards PBs')
            return
        print('PBs:')
        for key, df in pbs.items():
            df = df.sort_values('Solvetime')
            id_string = '' if np.isnan(df.iat[0, 0]) else '\t(' + str(df.index[0]) + ')'
            print('Best ' + key[0].lower() + key[1:] + ':' + measures_of_interest[key][3] + str(df.iat[0, 0] / 1000) + id_string)

    def plot_pbs(self):
        pbs = self.summaries()
        if list(pbs.values())[0].empty:
            print('Dataset does not include any sessions that count towards PBs')
            return
        fig, ax = plt.subplots()
        min_time = 60000
        max_time = 0
        for key, value in pbs.items():
            times = value.iloc[:, 0].to_numpy()
            pb_time = times[0]
            for i in range(1, times.size):
                if times[i] > pb_time:
                    times[i] = pb_time
                elif not np.isnan(times[i]):
                    pb_time = times[i]
            min_time = min_time if (min_time < min(times) or np.isnan(min(times))) else min(times)
            max_time = max_time if (max_time > max(times) or np.isnan(max(times))) else max(times)
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

    def append_line_to_data_file(self, solvetime, time_of_day, date, scramble, penalty):
        new_df = pd.DataFrame({'Solvetime': [solvetime], 'Time of day': [time_of_day], 'Date': [date], 'Scramble': [scramble], 'Penalty': [penalty]}, index=[len(self.df)])
        new_df.to_csv(self.data_file, mode='a', header=False, index=False, sep=';')
        return new_df
