from Dataset import Dataset
from Scrambler import Scrambler
from Timer import Timer


def main():
    scrambler = Scrambler(20)
    main_data_set = Dataset('testfile.txt')
    timer = Timer(main_data_set.add_data_point, scrambler.generate_scramble)
    #main_data_set.plot_pbs()
    timer.run()

if __name__ == "__main__":
    main()