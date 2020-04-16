from Dataset import Dataset
from Scrambler import Scrambler
from Timer import Timer
from os import listdir
from os.path import isfile, join
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from time_data_formatter import time_data_formatter


def new_dataset(filename, print_message=True):
    dataset = Dataset(dataset_folder + filename)
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


pd.set_option('display.max_rows', 1000)
register_matplotlib_converters()

dataset_folder = 'datasets/'
files = [f for f in listdir(dataset_folder) if isfile(join(dataset_folder, f))]
print('Select dataset. Available datasets:')
for file in files:
    print(file[:len(file)-4])
data = input() + '.txt'

if data in files:
    print('Creating new dataset ds')
else:
    print('Creating dataset ds from ' + data)

print('Setting active dataset to ds')

scrambler = Scrambler(20)
timer = Timer(scrambler.generate_scramble)
ds = new_dataset(data, False)
