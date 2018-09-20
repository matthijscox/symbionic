'''
currently just a script
@author: Matthijs Cox
'''

import symbionic
import numpy as np
import matplotlib.pyplot as plt

folder = symbionic.example_data_directory()

emg_data = symbionic.EmgData()
emg_data.load(folder + 'raw1.bin', gesture='g1')
emg_data.load(folder + 'raw2.bin', gesture='g2')
emg_data.load(folder + 'raw3.bin', gesture='g3')
emg_data.load(folder + 'raw4.bin', gesture='g4')
emg_data.load(folder + 'raw5.bin', gesture='g5')
emg_data.load(folder + 'raw6.bin', gesture='g6')
emg_data.label_patterns()
emg_data.plot(ylim=(-100, 100))

# get windowed training samples
# samples = emg_data.get_training_samples()

