import pandas
import numpy
from pandas import DataFrame
from scipy.signal import butter, filtfilt, savgol_filter, hilbert
import re
from symbionic import _plotting, _dataReceiver, _dataLoader
import os


def example_data_directory():
    file_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(file_dir)
    return parent_dir + '/data/'


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


def calc_envelope(signal, freq=200, smooth=21):
    filtered_emg_signal = emg_filter_bandpass(signal, cut=freq)  # lowpass filter
    h = calc_hilbert(filtered_emg_signal)  # hilbert transform
    return savgol_filter(h[0], smooth, 1)  # extra smoothing


def GFDataHandler():
    return _dataReceiver.GFDataHandler()


def GFDataReceiverSocket(*args, **kwargs):
    return _dataReceiver.GFDataReceiverSocket(*args, **kwargs)


def EmgData(*args, **kwargs):
    return _dataLoader.EmgData(*args, **kwargs)