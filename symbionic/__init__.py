import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt, savgol_filter, hilbert
import re
from symbionic._plotting import *


def emg_filter_bandpass(x, order=4, sRate=650., cut=200., btype='low'):
    """ Forward-backward (high- or low-)pass filtering (IIR butterworth filter) """
    nyq = 0.5 * sRate
    low = cut / nyq
    b, a = butter(order, low, btype=btype, analog=False)
    return filtfilt(b=b, a=a, x=x, axis=0, method='pad', padtype='odd',
                    padlen=np.minimum(3 * np.maximum(len(a), len(b)), x.shape[0] - 1))


def calc_hilbert(signal):
    analytic_signal = hilbert(signal)
    amplitude_envelope = np.abs(analytic_signal)
    instantaneous_phase = np.unwrap(np.angle(analytic_signal))
    instantaneous_frequency = (np.diff(instantaneous_phase) / (2.0 * np.pi) * 650)
    return [amplitude_envelope, instantaneous_frequency]


class EmgData:
    def __init__(self, channels=8, sample_rate=650, gestures=6):
        self.channels = channels
        self.gestures = gestures
        self.sample_rate = sample_rate  # Hz
        self.channel_names = ['emg' + str(i) for i in range(1, self.channels + 1)]
        self.gesture_names = ['g' + str(i + 1) for i in range(self.gestures)]
        self.data = self._init_gesture_dict()
        self.has_data = dict([(g, False) for g in self.gesture_names])
        self.data_path = self._init_gesture_dict()
        self.envelope = self._init_gesture_dict()

    def _init_gesture_dict(self):
        return dict([(g, '') for g in self.gesture_names])  # gestures, called g1, g2, etc

    def gestures_with_data(self):
        return [x for x in self.gesture_names if self.has_data[x]]

    def load_training_data(self, path, gesture='g1'):
        columns = self.channel_names
        # read in the binary data
        with open(path, 'rb') as f:
            bytesdata = f.read()
        # initialize data frame
        index = range(0, int(len(bytesdata) / self.channels))
        df = pd.DataFrame(index=index, columns=columns)
        # convert bytes to integer list
        values = [x for x in bytesdata]
        # convert values to dataframe
        for chan in range(0, self.channels):
            df[columns[chan]] = pd.DataFrame(values[chan::self.channels])
            df[columns[chan]] = df[columns[chan]] - df[columns[chan]].mean()  # remove the mean
        # add a time column
        df['time'] = np.array(range(len(df))) / self.sample_rate
        self.data[gesture] = df
        self.data_path[gesture] = path
        self.has_data[gesture] = True

    def run_method_on_gestures(self, fun_name, *args, **kwargs):
        result = []
        for g in self.gesture_names:
            if self.has_data[g]:
                result.append(getattr(self, fun_name)(g, *args, **kwargs))
        return result

    def calc_envelopes(self):
        self.run_method_on_gestures('_calc_envelope')

    def sum_envelope_channels(self):
        self.run_method_on_gestures('_sum_channels', attr='envelope')

    def label_patterns(self):
        self.run_method_on_gestures('_label_patterns')

    def _calc_envelope(self, gesture):
        # convert raw signals to envelope (pretty fast)
        channel_names = self.channel_names
        envelope = self.data[gesture].copy()
        for chan in range(self.channels):
            emg_signal = envelope[channel_names[chan]]
            filtered_emg_signal = emg_filter_bandpass(emg_signal, cut=200)  # lowpass filter
            h = calc_hilbert(filtered_emg_signal)  # hilter transform
            envelope[channel_names[chan]] = savgol_filter(h[0], 21, 1)  # extra smoothing
        self.envelope[gesture] = envelope

    def _sum_channels(self, gesture, attr='envelope'):
        df = getattr(self, attr)[gesture]
        df['sum'] = df[self.channel_names].sum(axis=1)

    def _label_patterns(self, gesture, shift=0.05):
        self._calc_envelope(gesture)
        self._sum_channels(gesture, attr='envelope')
        envelope = self.envelope[gesture]
        data = self.data[gesture]
        envelope_signal = envelope['sum']
        filtered_signal = emg_filter_bandpass(envelope_signal, cut=3)
        labeled = filtered_signal > max(filtered_signal) / 3.5
        sample_shift = int(shift * self.sample_rate)
        labeled = np.concatenate((labeled[sample_shift:], labeled[:sample_shift]), axis=0)
        envelope['labeled'] = labeled
        data['labeled'] = labeled

    def get_training_samples(self, window=0.2, step=0.062):
        '''
        Create training samples X, y and dt
        Input window and step are in seconds
        '''
        window_size = int(window * self.sample_rate)
        step_size = int(step * self.sample_rate)
        result = self.run_method_on_gestures('_get_training_samples_one_gesture',
                                             window_size=window_size, step_size=step_size)
        X = np.hstack([r['X'] for r in result]).transpose()
        y = np.hstack([r['y'] for r in result])
        dt = np.hstack([r['dt'] for r in result])
        return {'X': X, 'y': y, 'dt': dt}

    def _get_training_samples_one_gesture(self, gesture, window_size=130, step_size=40):
        ''' window and step in number of samples'''
        data = self.data[gesture]
        g = int(re.findall(r'\d+$', gesture)[0])  # find the trailing digits of the gesture name
        channel_names = self.channel_names
        labeled = data['labeled']
        # find the distance to the nearest pattern
        indices = np.nonzero(np.r_[1, np.diff(labeled)[:-1]])
        start_of_patterns = indices[0][1::2]

        def dist_to_nearest_pattern(index):
            nearest_index = (np.abs(start_of_patterns - index)).argmin()
            return index - start_of_patterns[nearest_index]

        # create training samples
        steps = int((len(data) - window_size) / step_size)
        # initialize
        X = np.zeros((window_size * len(channel_names), steps))
        y = np.zeros(steps)
        dt = np.zeros(steps)
        for step in range(steps):
            start_index = step * step_size
            end_index = start_index + window_size - 1
            data_samples = [data.loc[start_index:end_index, c] for c in channel_names]  # slow
            X[:, step] = np.ndarray.flatten(np.array(data_samples))  # a bit slow
            y[step] = labeled[end_index] * (g + 1)  # maybe check if there is any true?
            dt[step] = dist_to_nearest_pattern(end_index)
        return {'X': X, 'y': y, 'dt': dt}