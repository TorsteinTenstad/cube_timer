from Dataset import Dataset
from Scrambler import Scrambler
from Timer import Timer

scrambler = Scrambler(20)
main_data_set = Dataset('times.txt')
timer = Timer(main_data_set.add_data_point, scrambler.generate_scramble)
#timer.run()
main_data_set.all_sessions['s7'].plot_histogram(bin_width=2)
#main_data_set.plot_pbs()
