from tkinter import *
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.animation as animation
import symbionic
import time

# create figure for inside the gui
fig = Figure(figsize=(7, 6))
#plt.ion()

# use a stubbed receiver
receiver = symbionic.GFDataReceiverSocket(stub=True)
number_of_packages = 15


def start_data_receiver():
    # start the receiver
    receiver.start()
    # wait for some data to come in
    time.sleep(number_of_packages * 0.03 + 0.2)


def stop_data_receiver():
    receiver.stop()
    print(len(receiver.dataHandler.ExtendedDeviceData))


def init_plot(channels=8):
    global ax
    global line
    global lines
    lines = []
    ax = []
    for chan in range(channels):
        ax.append(fig.add_subplot(channels, 1, chan + 1))
        ax[chan].autoscale(False)
        ax[chan].set_ylim(-150,150)
        ax[chan].set_xlim(0, 1)
        ax[chan].set_xticks([])
        ax[chan].set_yticks([])
        line, = ax[chan].plot([], [])
        lines.append(line)
    return line,


def animate(draw=False):
    if receiver.connected:
        data = receiver.dataHandler.get_latest_emg_data(number_of_packages)
        data_size = data.shape[0]  # data size
        x_data = [x for x in range(0, data_size)]  # x-axis data of graph
        for chan in range(len(lines)):
            ax[chan].set_xlim(0, data_size-1)
            lines[chan].set_xdata(x_data)
            lines[chan].set_ydata(data[:, chan])
    return line,  # matplotlib.animation requires an iterable (like a tuple) as output


############## Tkinter ################
root = Tk()
root.title("Symbionic GUI")
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N,S,E,W))

# add label and buttons
ttk.Label(mainframe, text="Nice GUI").grid(column=1, row=0, sticky=N)
ttk.Button(mainframe, text="Start", command=start_data_receiver).grid(column=0, row=2, sticky=W)
ttk.Button(mainframe, text="Stop", command=stop_data_receiver).grid(column=2, row=2, sticky=W)

# add a figure
init_plot()

canvas = FigureCanvasTkAgg(fig, master=mainframe)
canvas.draw()
canvas.get_tk_widget().grid(column=1, row=1)

# make everything stick
for x in range(3):
    mainframe.columnconfigure(x, weight=1)
for y in range(3):
    mainframe.rowconfigure(y, weight=1)

# add some padding
for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

# get going
ani = animation.FuncAnimation(fig, animate, interval=100)
root.mainloop()
