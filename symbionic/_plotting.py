
import matplotlib.pyplot as plt
import numpy as np


def set_axe_properties(ax,ylim=(-60,60)):
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(color='#DDDDDD', linestyle='--', linewidth=0.5)
    ax.set_ylim(ylim)
    ax.tick_params(length=0)


def plot(emg_data,time=(0.2,4.8),figsize=(15,8),ylim=(-60,60),show_data=True,show_labels=True,show_envelope=False):
    gestures = emg_data.gestures_with_data()
    number_of_gestures = len(gestures)
    channel_names = emg_data.channel_names
    number_of_channels = len(channel_names)
    samples = [int(t*emg_data.sample_rate) for t in time]
    indices = np.arange(samples[0], samples[1]) # data to use in the plot

    fig = plt.figure(1, figsize=figsize)
    for (g,gesture) in zip(range(len(gestures)),gestures):
        data = emg_data.data[gesture]
        envelope = emg_data.envelope[gesture]
        for chan in range(emg_data.channels):
            sub_plot_ax = chan*number_of_gestures + g + 1
            ax = plt.subplot(number_of_channels, number_of_gestures, sub_plot_ax)

            plot_time = data['time'][indices]
            if show_data:
                emg_signal = data[channel_names[chan]][indices]
                ax.plot(plot_time, emg_signal, color='#888888', lw=0.5)

            if show_envelope:
                envelope_signal = envelope[channel_names[chan]][indices]
                ax.plot(plot_time,envelope_signal,color='#1D91C2',lw=1.5)

            if show_labels:
                try:
                    labeled = np.array(data['labeled'][indices])
                    ax.fill_between(plot_time, ylim[1]*labeled, y2=ylim[0], color='#D0F1FF', where=labeled)
                except:
                    pass

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
    return fig
