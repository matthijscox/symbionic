'''
currently just a script
@author: Matthijs Cox
'''

import matplotlib.pyplot as plt
import numpy as np
import symbionic

folder = r"C:\Users\matcox\TMC\Teamsite - Documenten\Data\OYMotion-sample\data"
folder = folder.replace("\\", "/")

emg_signals = symbionic.EmgData()
emg_signals.load_training_data(folder + '/g1/535-170309-g1-20-f1.hex',gesture='g1')
emg_signals.load_training_data(folder + '/g2/226-170310-g2-20-f2.hex',gesture='g2')
emg_signals.load_training_data(folder + '/g3/226-170310-g3-20-f2.hex',gesture='g3')
emg_signals.load_training_data(folder + '/g4/226-170310-g4-20-f2.hex',gesture='g4')
emg_signals.load_training_data(folder + '/g5/533-170309-g5-20-f1.hex',gesture='g5')
emg_signals.load_training_data(folder + '/g6/226-170310-g6-20-f2.hex',gesture='g6')
emg_signals.calc_envelopes()
emg_signals.label_patterns()


# plotting
def set_axe_properties(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(color='#DDDDDD', linestyle='--', linewidth=0.5)
    ax.set_ylim((-60, 60))
    ax.tick_params(length=0)

gestures = emg_signals.gestures_with_data()
number_of_gestures = len(gestures)
channel_names = emg_signals.channel_names
number_of_channels = len(channel_names)
indices = np.arange(200, 3000) # data to use in the plot

A1 = plt.figure(1, figsize=(3*number_of_gestures, number_of_channels))
for (g,gesture) in zip(range(len(gestures)),gestures):
    data = emg_signals.data[gesture]
    envelope = emg_signals.envelope[gesture]
    for chan in range(emg_signals.channels):
        sub_plot_ax = chan*number_of_gestures + g + 1

        # get a subset of data
        emg_signal = data[channel_names[chan]][indices]
        envelope_signal = envelope[channel_names[chan]][indices]
        time = data['time'][indices]
        labeled = np.array(envelope['labeled'][indices])

        # plotting that stuff
        ax = plt.subplot(number_of_channels, number_of_gestures, sub_plot_ax)

        ax.plot(time, emg_signal, color='#888888', lw=0.5)
        #ax.plot(time,envelope_signal,color='#1D91C2',lw=1.5)
        #ax.fill_between(time, 60*labeled, y2=-60, color='#D0F1FF', where=labeled)

        # setting axe properties
        set_axe_properties(ax)
        if g == 0:
            ax.set_ylabel('ch{0}'.format(chan+1))
        else:
            ax.set_yticklabels([])
        if sub_plot_ax <= (number_of_channels-1)*number_of_gestures:
            ax.set_xticklabels([])
        else:
            ax.set_xlabel('Time (s)')
        if chan ==0:
            ax.set_title(gesture)

plt.tight_layout()
plt.show()
