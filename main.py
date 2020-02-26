from Dataset import Dataset
from Scrambler import Scrambler
from Timer import Timer
from time_data_formatter import time_data_formatter


def new_dataset(filename):
    dataset = Dataset(filename)
    timer.send_time_func = dataset.add_data_point
    timer.call_on_finish = dataset.print_number_of_solves
    return dataset


scrambler = Scrambler(20)
ds = Dataset('times.txt')
timer = Timer(ds.add_data_point, scrambler.generate_scramble, ds.print_number_of_solves)