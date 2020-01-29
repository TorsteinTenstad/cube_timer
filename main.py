import keyboard
import time
from datetime import datetime
from datetime import date
import pandas as pd


class Dataset:
    def __init__(self, data_file):
        self.data_file = data_file
        self.active_sessions = {}
        self.paused_sessions = {}
        self.stopped_sessions = {}
        self.sessions = {'start': self.active_sessions, 'pause': self.paused_sessions, 'end': self.stopped_sessions}

        df = pd.read_csv(self.data_file, sep=';')
        for index, row in df.iterrows():
            if row['c0'] == '---Session':
                self.set_session_status(row['c2'], row['c1'])
            else:
                for session_name, session in self.active_sessions.items():
                    session.add_data_point(row.to_frame())

    def add_data_point(self, time_s):
        new_df = self.append_line_to_data_file(int(time_s * 1000), datetime.now().strftime(
            "%H:%M:%S"), date.today().strftime("%d/%m/%Y"))
        for session_name, session in self.active_sessions.items():
            session.add_data_point(new_df)

    def set_session_status(self, session_name, new_status):
        for status, session_dict in self.sessions.items():
            if status != new_status:
                session_to_move = self.sessions[status].pop(session_name, None)
                if session_to_move:
                    self.sessions[new_status].update({session_name: session_to_move})
                    return session_to_move
        if new_status == 'start':
            new_session = Session(session_name)
            self.active_sessions.update({session_name: new_session})
            return new_session

    def log_session_action(self, session_name, new_status):
        if self.set_session_status(session_name, new_status):
            self.append_line_to_data_file('---Session', new_status, session_name)

    def append_line_to_data_file(self, c0, c1, c2):
        new_df = pd.DataFrame({'c0': [c0], 'c1': [c1], 'c2': [c2]})
        new_df.to_csv(self.data_file, mode='a', header=False, index=False)
        return new_df


class Session:

    def __init__(self, name):
        self.name = name
        self.df = []
        return

    def add_data_point(self, data_point):
        self.df.append(data_point)
        return


class Timer:

    def __init__(self, trigger_key, send_time_func):
        self.trigger_key = trigger_key
        self.send_time_func = send_time_func

    def record_time(self):
        ready = False
        while not ready:
            keyboard.wait(self.trigger_key, suppress=True, trigger_on_release=False)
            initial_t = time.time()
            while True:
                if time.time() - initial_t > 1:
                    print('Ready')
                    ready = True
                    break
                elif not keyboard.is_pressed(self.trigger_key):
                    break

        keyboard.wait(self.trigger_key, suppress=True, trigger_on_release=True)
        t = time.time()
        keyboard.wait(self.trigger_key)
        self.send_time_func(time.time() - t)
        keyboard.wait(self.trigger_key, suppress=True, trigger_on_release=True)


main_data_set = Dataset('testfile.txt')
timer = Timer('space', main_data_set.add_data_point)
while True:
    timer.record_time()
