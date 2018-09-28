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
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
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
number_of_gestures = 7
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


gestureModel = GestureModel(FakeModel())


class GestureViewer(ttk.Frame):
    def __init__(self, master=None, n_gestures=number_of_gestures):
        ttk.Frame.__init__(self, master, style='My.TFrame')
        self.master = master
        self.gestures = []
        self.prediction = 0
        self.previous_prediction = 0
        self.gesture_disabled_style = 'Disabled.TRadiobutton'
        self.gesture_enabled_style = 'Enabled.TRadiobutton'
        self.selected_gesture = IntVar()
        self.selected_gesture.set(0)
        for g in range(n_gestures):
            if g is 0:
                gesture_name = "No Gesture"
            else:
                gesture_name = f"Gesture {g}"
            gesture = ttk.Radiobutton(self,
                                      text=gesture_name,
                                      style=self.gesture_disabled_style,
                                      variable=self.selected_gesture,
                                      value=g)
            gesture.pack(pady=5)
            self.add(gesture)

    def add(self, gesture):
        self.gestures.append(gesture)

    def show_prediction(self):
        self.set_gesture_style(self.previous_prediction,self.gesture_disabled_style)
        self.set_gesture_style(self.prediction, self.gesture_enabled_style)

    def update_prediction(self,input_data):
        self.previous_prediction = self.prediction
        self.prediction = gestureModel.predict(input_data)
        receiver.dataHandler.currentPrediction = self.prediction
        self.show_prediction()

    def set_gesture_style(self,predicted_gesture,style):
        if predicted_gesture<len(self.gestures):
            self.gestures[predicted_gesture].configure(style=style)


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


def save_raw_data_per_gesture():
    dir_name = askdirectory(initialdir=application_directory,
                           title="Save your raw data."
                           )
    try:
        device_data = receiver.dataHandler.ExtendedDeviceData
        chained_data = receiver.dataHandler.chain_all_packages(device_data)
        # save in binary format
        output_file = open(os.path.abspath(dir_name+'/raw1.bin'), "wb")
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
gui_style.configure('Enabled.TRadiobutton', foreground="red", font=("Helvetica", 24))
gui_style.configure('Disabled.TRadiobutton', foreground="black", font=("Helvetica", 24))
gui_style.configure('Main.TButton', relief='flat', background='black')

default_button_size = 80
default_button_border = 4

button_without_border_style = {
    'relief': 'flat',
    'activebackground': '#125D7D',
    'background':'#1EB4F2',
    'foreground':'white',
    'activeforeground':'white',
    'padx':5,
    'font':("Helvetica", 16),
    'highlightthickness': 0
}

button_with_border_style = {
    'relief': 'flat',
    'activebackground': 'white',
    'background':'white',
    'foreground':'#1EB4F2',
    'activeforeground':'#125D7D',
    'padx':5,
    'font':("Helvetica", 16),
}


class ButtonWithoutBorder(Frame):
    def __init__(self, master=None, height=default_button_size, bd=default_button_border, **kwargs):
        Frame.__init__(self, master, background=button_without_border_style['background'], bd=bd)
        self.configure(height=height)
        self.button = Button(self, **button_without_border_style, **kwargs)
        self.button.pack(fill='both', expand=1)


class ButtonWithBorder(Frame):
    def __init__(self, master=None, height=default_button_size, bd=default_button_border, **kwargs):
        Frame.__init__(self, master, background=button_with_border_style['foreground'], bd=bd)
        self.configure(height=height)
        self.button = Button(self, **button_with_border_style, **kwargs)
        self.button.pack(fill='both', expand=1)

#tk_style = Style()
#tk_style.configure('Main.TButton', relief='flat', background='black')

top_frame = ttk.Frame(root, padding="3 3 12 12", style='My.TFrame')
middle_frame = ttk.Frame(root, padding="3 3 12 12", style='My.TFrame')
lower_frame = ttk.Frame(root, padding="3 3 12 12", style='My.TFrame')
top_frame.pack(fill="both", expand=True)
middle_frame.pack(fill="both", expand=True)
lower_frame.pack(fill="both", expand=True)

# add top label
ttk.Label(top_frame, text="", background='white').pack(anchor='center')

# add a figure
middle_left_frame = ttk.Frame(middle_frame, style='My.TFrame')
middle_left_frame.pack(side=LEFT)
init_plot()
canvas = FigureCanvasTkAgg(fig, master=middle_left_frame)
canvas.draw()
canvas.get_tk_widget().pack()

#middle_right_frame = ttk.Frame(middle_frame, style='My.TFrame')
#middle_right_frame.pack(side=LEFT, expand=True, padx=20)
# add the gesture viewer to the frame
gestureViewer = GestureViewer(middle_frame)
gestureViewer.pack(side=LEFT, expand=True, padx=20)

# add buttons
ButtonWithoutBorder(lower_frame, text=" Connect ", command=start_data_receiver).pack(side=RIGHT, padx=5)
ButtonWithBorder(lower_frame, text="Disconnect", command=stop_data_receiver).pack(side=RIGHT, padx=5)

# menu
menu = Menu(root)
root.config(menu=menu)
file = Menu(menu)
file.add_command(label='Save data', command=save_raw_data)
file.add_command(label='Load Model', command=open_model_file)
file.add_command(label='Exit', command=lambda:exit())
menu.add_cascade(label='File', menu=file)


def animate(draw=False):
    if receiver.connected:
        data = receiver.dataHandler.get_latest_emg_data(number_of_packages)
        data_size = data.shape[0]  # data size
        x_data = [x for x in range(0, data_size)]  # x-axis data of graph
        for chan in range(len(lines)):
            lines[chan].set_xdata(x_data)
            lines[chan].set_ydata(data[:, chan])
        gestureViewer.update_prediction(data)
        root.update_idletasks()  # improves performance significantly
    return line,  # matplotlib.animation requires an iterable (like a tuple) as output


# get going
ani = animation.FuncAnimation(fig, animate, interval=300)
root.mainloop()
