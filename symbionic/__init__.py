import pandas
import numpy
from pandas import DataFrame
from scipy.signal import butter, filtfilt, savgol_filter, hilbert
import re
from symbionic import _plotting


def emg_filter_bandpass(x, order=4, sRate=650., cut=200., btype='low'):
    """ Forward-backward (high- or low-)pass filtering (IIR butterworth filter) """
    nyq = 0.5 * sRate
    low = cut / nyq
    b, a = butter(order, low, btype=btype, analog=False)
    return filtfilt(b=b, a=a, x=x, axis=0, method='pad', padtype='odd',
                    padlen=numpy.minimum(3 * numpy.maximum(len(a), len(b)), x.shape[0] - 1))


def calc_hilbert(signal):
    analytic_signal = hilbert(signal)
    amplitude_envelope = numpy.abs(analytic_signal)
    instantaneous_phase = numpy.unwrap(numpy.angle(analytic_signal))
    instantaneous_frequency = (numpy.diff(instantaneous_phase) / (2.0 * numpy.pi) * 650)
    return [amplitude_envelope, instantaneous_frequency]


def plot_confusion_matrix(*args, **kwargs):
    return _plotting.plot_confusion_matrix( *args, **kwargs)


class EmgData:
    def __init__(self, channels: int = 8, sample_rate: int = 650, gestures: int = 6):
        self.channels = channels
        self.gestures = gestures
        self.sample_rate = sample_rate  # Hz
        self.channel_names = ['emg' + str(i) for i in range(1, self.channels + 1)]
        self.gesture_names = ['g' + str(i + 1) for i in range(self.gestures)]
        self.data = self._init_gesture_dict()
        self.has_data = dict([(g, False) for g in self.gesture_names])
        self.envelope = self._init_gesture_dict()

    def _init_gesture_dict(self):
        return dict([(g, None) for g in self.gesture_names])  # gestures, called g1, g2, etc

    def gestures_with_data(self):
        return [x for x in self.gesture_names if self.has_data[x]]

    def load(self,path,gesture='g1'):
        # we only support hex data for now
        self.load_hex_data(path,gesture)

    def load_training_data(self, path, gesture='g1'):
        # deprecated
        self.load(path,gesture)

    def load_hex_data(self, path, gesture='g1'):
        # read in the binary data
        with open(path, 'rb') as f:
            bytesdata = f.read()
        # convert bytes to integer list
        values = [x for x in bytesdata]
        self.store_emg_values_in_gesture(values,gesture)

    def store_emg_values_in_gesture(self,values,gesture):
        df = self.convert_emg_values_to_dataframe(values)
        self.store_dataframe_in_gesture(gesture, df)

    def convert_emg_values_to_dataframe(self,values,demean=True) -> DataFrame:
        columns = self.channel_names
        # initialize data frame
        index = range(0, int(len(values) / self.channels))
        df: DataFrame = pandas.DataFrame(index=index, columns=columns)
        # convert values to a dataframe
        # assuming the separate channels are stored intertwined
        # so the values are: [point1channel1,point1channel2, ..., point1channelN, point2channel1, point2channel2 ...]
        for chan in range(0, self.channels):
            df[columns[chan]] = pandas.DataFrame(values[chan::self.channels])
            if demean:
                df[columns[chan]] = df[columns[chan]] - df[columns[chan]].mean()  # remove the mean
        # add a time column
        df['time'] = numpy.array(range(len(df))) / self.sample_rate
        return df

    def store_dataframe_in_gesture(self,gesture,df):
        self.data[gesture] = df
        self.has_data[gesture] = True

    def get_data_from_gesture(self, gesture):
        return self.data[gesture]

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
        envelope: DataFrame = self.data[gesture].copy()
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
        envelope: DataFrame = self.envelope[gesture]
        data: DataFrame = self.data[gesture]
        envelope_signal = envelope['sum']
        filtered_signal = emg_filter_bandpass(envelope_signal, cut=3)
        labeled = filtered_signal > max(filtered_signal) / 3.5
        sample_shift = int(shift * self.sample_rate)
        labeled = numpy.concatenate((labeled[sample_shift:], labeled[:sample_shift]), axis=0)
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
        X = numpy.hstack([r['X'] for r in result]).transpose()
        y = numpy.hstack([r['y'] for r in result])
        dt = numpy.hstack([r['dt'] for r in result])
        return {'X': X, 'y': y, 'dt': dt}

    def _get_training_samples_one_gesture(self, gesture, window_size=130, step_size=40):
        ''' window and step in number of samples'''
        data: DataFrame = self.data[gesture]
        g = int(re.findall(r'\d+$', gesture)[0])  # find the trailing digits of the gesture name
        channel_names = self.channel_names
        labeled = data['labeled']
        # find the distance to the nearest pattern
        indices = numpy.nonzero(numpy.r_[1, numpy.diff(labeled)[:-1]])
        start_of_patterns = indices[0][1::2]

        def dist_to_nearest_pattern(index):
            nearest_index = (numpy.abs(start_of_patterns - index)).argmin()
            return index - start_of_patterns[nearest_index]

        # create training samples
        steps = int((len(data) - window_size) / step_size)
        # initialize
        X = numpy.zeros((window_size * len(channel_names), steps))
        y = numpy.zeros(steps)
        dt = numpy.zeros(steps)
        for step in range(steps):
            start_index = step * step_size
            end_index = start_index + window_size - 1
            data_samples = [data.loc[start_index:end_index, c] for c in channel_names]  # slow
            X[:, step] = numpy.ndarray.flatten(numpy.array(data_samples))  # a bit slow
            y[step] = labeled[end_index] * g
            dt[step] = dist_to_nearest_pattern(end_index)/self.sample_rate
        return {'X': X, 'y': y, 'dt': dt}

    def plot(self,*args,**kwargs):
        return _plotting.plot(self,*args,**kwargs)