import keyboard
import time


class Timer:

    def __init__(self, scramble_func, send_time_func=None, call_on_finish=None, trigger_key='space', quit_key='q', add_2_key='2', dnf_key='d', min_hold_time=1):
        self.send_time_func = send_time_func
        self.scramble_func = scramble_func
        self.trigger_key = trigger_key
        self.quit_key = quit_key
        self.add_2_key = add_2_key
        self.dnf_key = dnf_key
        self.min_hold_time = min_hold_time
        self.call_on_finish = call_on_finish

        self.state = 0
        self.recorded_time = -1
        self.add_2 = False
        self.dnf = False
        self.scramble = ''

    def register_time(self):
        if self.recorded_time > 0:
            penalty = ''
            time_to_send = self.recorded_time
            if self.dnf:
                penalty = 'DNF'
                time_to_send = 60
            elif self.add_2:
                penalty = '+2'
                time_to_send += 2
            self.send_time_func(time_to_send, self.scramble, penalty)
        self.add_2 = False
        self.dnf = False

    def run(self):
        self.state = 0
        self.recorded_time = -1
        self.add_2 = False
        self.dnf = False
        new_scramble = self.scramble_func()
        print(new_scramble)

        while True:
            if self.state == 0:  # waiting for input
                time.sleep(0.1)
                if keyboard.is_pressed(self.trigger_key):
                    hold_start = time.time()
                    self.state = 1
                elif keyboard.is_pressed(self.add_2_key):
                    self.add_2 = not self.add_2
                    print('+2:', self.add_2)
                    keyboard.wait(self.add_2_key, suppress=True, trigger_on_release=True)
                elif keyboard.is_pressed(self.dnf_key):
                    self.dnf = not self.dnf
                    print('DNF:', self.dnf)
                    keyboard.wait(self.dnf_key, suppress=True, trigger_on_release=True)
                elif keyboard.is_pressed(self.quit_key):
                    self.register_time()
                    return
            if self.state == 1:  # user is holding, waiting for ready signal
                if time.time() - hold_start > self.min_hold_time:
                    print('Ready')
                    self.register_time()
                    self.state = 2
                elif not keyboard.is_pressed(self.trigger_key):
                    self.state = 0
            if self.state == 2:  # timer starts
                if not keyboard.is_pressed(self.trigger_key):
                    start_time = time.time()
                    self.state = 3
            if self.state == 3:  # waiting for, and registering finish
                if keyboard.is_pressed(self.trigger_key):
                    self.recorded_time = time.time() - start_time
                    print('Time: ', self.recorded_time)
                    self.call_on_finish()
                    self.scramble = new_scramble
                    new_scramble = self.scramble_func()
                    print(new_scramble)
                    self.state = 4
            if self.state == 4:  # extra state to prevent immediately starting the timer again
                if not keyboard.is_pressed(self.trigger_key):
                    self.state = 0
