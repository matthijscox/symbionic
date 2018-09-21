from tkinter import *
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.animation as animation
import symbionic
import time
import random

# create figure for inside the gui
fig = Figure(figsize=(7, 6))
#plt.ion()

# use a stubbed receiver
receiver = symbionic.GFDataReceiverSocket(stub=True)
number_of_packages = 15
gestures = []

def start_data_receiver():
    # start the receiver
    receiver.start()
    # wait for some data to come in
    time.sleep(number_of_packages * 0.03 + 0.2)


def stop_data_receiver():
    receiver.stop()
    #print(len(receiver.dataHandler.ExtendedDeviceData))


class GestureDisplayer:
    def __init__(self):
        self.gestures = []
        self.prediction = 0

    def add(self,gesture):
        self.gestures.append(gesture)

    def show_prediction(self):
        for g in self.gestures:
            g.configure(style='Disabled.Label')
        self.gestures[self.prediction].configure(style='Enabled.Label')


gesture_displayer = GestureDisplayer()


def update_prediction():
    gesture_displayer.prediction = random.randrange(6)
    gesture_displayer.show_prediction()


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
        update_prediction()
    return line,  # matplotlib.animation requires an iterable (like a tuple) as output


############## Tkinter ################
root = Tk()
root.title("Symbionic GUI")
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

gui_style = ttk.Style()
gui_style.configure('My.TFrame', background='white')
gui_style.configure('Enabled.Label', foreground="red")
gui_style.configure('Disabled.Label', foreground="black")

top_frame = ttk.Frame(root, padding="3 3 12 12", style='My.TFrame')
middle_frame = ttk.Frame(root, padding="3 3 12 12", style='My.TFrame')
lower_frame = ttk.Frame(root, padding="3 3 12 12", style='My.TFrame')
top_frame.pack(fill="both", expand=True)
middle_frame.pack(fill="both", expand=True)
lower_frame.pack(fill="both", expand=True)

# add top label
ttk.Label(top_frame, text="Nice GUI", background='white').pack(anchor='center')

# add a figure
middle_left_frame = ttk.Frame(middle_frame, style='My.TFrame')
middle_left_frame.pack(side=LEFT)
init_plot()
canvas = FigureCanvasTkAgg(fig, master=middle_left_frame)
canvas.draw()
canvas.get_tk_widget().pack()

middle_right_frame = ttk.Frame(middle_frame, style='My.TFrame')
middle_right_frame.pack(side=LEFT, expand=True)

for g in range(6):
    gesture = ttk.Label(middle_right_frame, text=f"Gesture {g+1}", style='Disabled.Label')
    gesture.pack(pady=5)
    gesture_displayer.add(gesture)

# add buttons
ttk.Button(lower_frame, text="Start", command=start_data_receiver).pack(side=RIGHT, padx=5)
ttk.Button(lower_frame, text="Stop", command=stop_data_receiver).pack(side=RIGHT, padx=5)

# get going
ani = animation.FuncAnimation(fig, animate, interval=300)
root.mainloop()
