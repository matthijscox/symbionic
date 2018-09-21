import matplotlib.pyplot as plt
import symbionic
import numpy as np
import time
from matplotlib.pyplot import imshow, pause

# number of packages to show
number_of_packages = 15

# start the receiver
receiver = symbionic.GFDataReceiverSocket(stub=True)
receiver.start()

# wait until we have enough data
time.sleep(number_of_packages*0.03+0.2)

# collect a first data package
data = receiver.dataHandler.get_latest_emg_data(number_of_packages)
buffer_size = data.shape[0]  # data size
x = [x for x in range(0, buffer_size)]  # x-axis data of graph

fig = plt.figure(figsize=(7, 8))
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
        ax.set_ylim((-150, 150))
        ax.set_xlim((0, buffer_size-1))
        ax.set_xticks([])
        ax.set_yticks([])
        line, = ax.plot([], [])
        lines.append(line)
    if draw:
        fig.show()
        fig.canvas.draw()
    return line,  # matplotlib.animation requires an iterable (like a tuple) as output


def animate(draw=False):
    data = receiver.dataHandler.get_latest_emg_data(number_of_packages)
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


while True:
    animate(draw=True)
    pause(.05)



