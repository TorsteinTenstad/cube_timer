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
        
        df = pd.read_csv(self.data_file, sep=';')
        for index, row in df.iterrows():
            if row['c0'] == '---Session':
                action = row['c1']
                session_name = row['c2']
                if action == 'start':
                    new_session = Session(row['c2'])
                    self.active_sessions.update({session_name: new_session})
                elif action == 'pause':
                    self.paused_sessions.update({session_name: self.active_sessions.pop(session_name)})
                elif action == 'unpause':
                    self.active_sessions.update({session_name: self.paused_sessions.pop(session_name)})
                elif action == 'stop':
                    session_to_move = self.active_sessions.pop(session_name)
                    if not session_to_move:
                        session_to_move = self.paused_sessions.pop(session_name)
                    self.stopped_sessions.update({session_name: session_to_move})
                elif action == 'reopen':
                    self.active_sessions.update({session_name: self.stopped_sessions.pop(session_name)})
            else:
                for session_name, session in self.active_sessions.items():
                    session.add_data_point(row.to_frame())

    def add_data_point(self, time_s):
        new_df = pd.DataFrame({'c0': [int(time_s * 1000)], 'c1': [datetime.now().strftime(
            "%H:%M:%S")], 'c2': [date.today().strftime("%d/%m/%Y")]})
        print(new_df)
        new_df.to_csv(self.data_file, mode='a', header=False, index=False)
        for session_name, session in self.active_sessions.items():
            session.add_data_point(new_df)


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
