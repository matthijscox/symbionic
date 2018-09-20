import matplotlib.pyplot as plt
import symbionic
import numpy as np
import time
from matplotlib.pyplot import imshow, pause
import requests


class data_container:
    def __init__(self, data):
        self.index = 0
        self.step = 1
        self.size = 1
        self.data = data

    def __iter__(self):
        return self

    def __next__(self):
        if self.index == len(self.data):
            raise StopIteration
        start_index = self.index
        end_index = start_index + self.step + self.size - 1
        self.index = end_index
        return self.data[start_index:end_index, :]

    def goto(self, index):
        self.index = index


# Load a binary data file
emg_data = symbionic.EmgData()
emg_data.load(symbionic.example_data_directory() + "raw1.bin")
emg_array = emg_data.data['g1'].drop('time', axis=1).values


emg_iterator = data_container(emg_array)  
emg_iterator.goto(0)
emg_iterator.size = 1000
buffer_size = 500

# voltages = data_container()
emg_iterator.goto(0)
emg_iterator.step = 1
emg_iterator.size = buffer_size
data = next(emg_iterator)
emg_iterator.size = 50
# emg_iterator.goto(0)

x = [x for x in range(0, buffer_size)]


def update_data():
    global data
    data = np.vstack((data, next(emg_iterator)))
    if len(data) > buffer_size:
        data = data[-buffer_size:, :]


fig = plt.figure(figsize=(7, 8))
#plt.show()
plt.ion()


def init_plot(draw=False, channels=8):
    global ax
    global line
    global lines
    lines = []
    for chan in range(channels):
        ax = plt.subplot(channels, 1, chan + 1)
        # ax = fig.add_subplot(111)
        ax.autoscale(False)
        ax.set_ylim((-100, 100))
        ax.set_xlim((0, buffer_size))
        ax.set_xticks([])
        ax.set_yticks([])
        line, = ax.plot([], [])
        lines.append(line)
    if draw:
        fig.show()
        fig.canvas.draw()
    return line,  # matplotlib.animation requires an iterable (like a tuple) as output


def animate(draw=False):
    update_data()
    for chan in range(len(lines)):
        lines[chan].set_xdata(x)
        lines[chan].set_ydata(data[:, chan])
    # ax.plot(data)
    if draw:  # interactive plots requires you to update the canvas
        fig.canvas.draw()
    #time.sleep(.05)
    return line,  # matplotlib.animation requires an iterable (like a tuple) as output


line, = init_plot(draw=True)
animate(draw=True)


for i in range(0, 100):
    animate(draw=True)
    pause(.05)



