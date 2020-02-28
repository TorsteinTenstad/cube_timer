from Dataset import Dataset
from Scrambler import Scrambler
from Timer import Timer
import pandas as pd
from time_data_formatter import time_data_formatter


def new_dataset(filename, print_message=True):
    dataset = Dataset(filename)
    if print_message:
        print('Creating dataset from file: ' + filename)
        print('This is now the active dataset')
    set_active_dataset(dataset)
    return dataset


def set_active_dataset(dataset):
    timer.send_time_func = dataset.add_data_point
    timer.call_on_finish = dataset.print_number_of_solves
    print('Active sessions in this dataset:')
    dataset.lst()


data = 'times.txt'


scrambler = Scrambler(20)
timer = Timer(scrambler.generate_scramble)
print('Creating dataset ds from ' + data)
print('Setting active dataset to ds')
ds = new_dataset(data, False)
