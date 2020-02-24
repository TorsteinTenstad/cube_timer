from Dataset import Dataset
from Scrambler import Scrambler
from Timer import Timer

scrambler = Scrambler(20)
ds = Dataset('testfile.txt')
timer = Timer(ds.add_data_point, scrambler.generate_scramble, ds.print_number_of_solves)
timer.run()
#ds.all_sessions['global'].plot_histogram(bin_width=2)
#ds.plot_pbs()
