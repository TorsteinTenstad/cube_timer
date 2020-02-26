from Dataset import Dataset
from Scrambler import Scrambler
from Timer import Timer
from time_data_formatter import time_data_formatter

scrambler = Scrambler(20)
ds = Dataset('testfile.txt')
timer = Timer(ds.add_data_point, scrambler.generate_scramble, ds.print_number_of_solves)