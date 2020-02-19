import random
import time
import numpy as np


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
        random.seed(time.time())
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
        return scramble_str[:-1]
