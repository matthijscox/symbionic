from tkinter import *
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import symbionic
import time
import random
import numpy as np
from keras.models import load_model
from tkinter.filedialog import askopenfilename, asksaveasfilename
import os
import sys

if getattr(sys, 'frozen', False):
    # frozen
    application_directory = os.path.dirname(sys.executable)
else:
    # unfrozen
    application_directory = os.path.dirname(os.path.abspath(__file__))


# create figure for inside the gui
fig = Figure(figsize=(7, 6))

# use a stubbed receiver
receiver = symbionic.GFDataReceiverSocket(stub=True)
number_of_packages = 15
number_of_gestures = 6
package_size = 16
gestures = []


def start_data_receiver():
    # start the receiver
    receiver.start()
    # wait for some data to come in
    time.sleep(number_of_packages * 0.03 + 0.2)


def stop_data_receiver():
    receiver.stop()
    #print(len(receiver.dataHandler.ExtendedDeviceData))


class FakeModel:
    def predict(self,input_data):
        p = 7*[0]
        p[random.randrange(7)] = 1
        return p


def prepare_data_for_prediction(input_data):
    # only select last 100 samples
    output_data = input_data[-195:, :]
    # preparation for 1D Neural Network
    output_data = np.apply_along_axis(lambda x: symbionic.calc_envelope(x,smooth=51), 0, output_data)
    output_data = output_data.reshape((1,output_data.shape[0]*output_data.shape[1]))
    return output_data


class GestureModel:
    def __init__(self,model=None, data_prepare=None):
        self.model = model
        self.data_prepare = data_prepare

    def predict(self,input_data):
        prediction = 0
        if self.data_prepare is not None:
            input_data = self.data_prepare(input_data)
        if self.model is not None:
            prediction = self.model.predict(input_data)
            prediction = np.argmax(prediction)
        return prediction


gestureModel = GestureModel(FakeModel(), prepare_data_for_prediction)


class GestureViewer:
    def __init__(self):
        self.gestures = []
        self.prediction = 0

    def add(self, gesture):
        self.gestures.append(gesture)

    def show_prediction(self):
        for g in self.gestures:
            g.configure(style='Disabled.TLabel')
        if self.prediction is not 0:
            self.gestures[self.prediction-1].configure(style='Enabled.TLabel')


gestureViewer = GestureViewer()


def update_prediction(input_data):
    gestureViewer.prediction = gestureModel.predict(input_data)
    gestureViewer.show_prediction()


def init_plot(channels=8):
    global ax
    global line
    global lines
    lines = []
    ax = []
    for chan in range(channels):
        ax.append(fig.add_subplot(channels, 1, chan + 1))
        ax[chan].autoscale(False)
        ax[chan].set_ylim(-150, 150)
        ax[chan].set_xlim(0, number_of_packages*package_size-1)
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
            lines[chan].set_xdata(x_data)
            lines[chan].set_ydata(data[:, chan])
        update_prediction(data)
        root.update_idletasks()  # improves performance significantly
    return line,  # matplotlib.animation requires an iterable (like a tuple) as output


#This is where we lauch the file manager bar.
def open_model_file():
    name = askopenfilename(initialdir=application_directory,
                           filetypes=(("H5 File", "*.h5"),),
                           title="Choose a H5 model file."
                           )
    #Using try in case user types in unknown file or closes without choosing a file.
    try:
        # overwrite model
        gestureModel.model = load_model(name)
    except:
        print("No file exists")


def save_raw_data():
    name = asksaveasfilename(initialdir=application_directory,
                           filetypes=(("binary files","*.bin"),("all files","*.*")),
                           title="Save your raw data."
                           )
    try:
        device_data = receiver.dataHandler.ExtendedDeviceData
        chained_data = receiver.dataHandler.chain_all_packages(device_data)
        # save in binary format
        output_file = open(name, "wb")
        output_file.write(bytearray(chained_data))
        output_file.close()
    except:
        print("File writing failed")


############## Tkinter ################
root = Tk()
root.title("Symbionic GUI")
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

gui_style = ttk.Style()
gui_style.configure('My.TFrame', background='white')
gui_style.configure('Enabled.TLabel', foreground="red", font=("Helvetica", 24))
gui_style.configure('Disabled.TLabel', foreground="black", font=("Helvetica", 24))

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
middle_right_frame.pack(side=LEFT, expand=True, padx=20)

#v = IntVar()
for g in range(number_of_gestures):
    gesture = ttk.Label(middle_right_frame, text=f"Gesture {g+1}", style='Disabled.TLabel')
    gesture.pack(pady=5)
    gestureViewer.add(gesture)

# add buttons
ttk.Button(lower_frame, text="Connect", command=start_data_receiver).pack(side=RIGHT, padx=5)
ttk.Button(lower_frame, text="Disconnect", command=stop_data_receiver).pack(side=RIGHT, padx=5)

# menu
menu = Menu(root)
root.config(menu=menu)
file = Menu(menu)
file.add_command(label='Save data', command=save_raw_data)
file.add_command(label='Load Model', command=open_model_file)
file.add_command(label='Exit', command=lambda:exit())
menu.add_cascade(label='File', menu=file)

# get going
ani = animation.FuncAnimation(fig, animate, interval=300)
root.mainloop()
