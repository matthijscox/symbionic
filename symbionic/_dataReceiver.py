import socket
import struct
import threading
import numpy as np
from itertools import chain
import struct
import random
import time
import symbionic


class GFDataReceiverSocket:

    def __init__(self, data_handler=None, stub=False):
        self.connected = False
        self.client_socket = None
        if data_handler is None:
            data_handler = GFDataHandler()
        self.dataHandler = data_handler
        self.internalThread = None
        self.use_stub = stub

    def start(self):
        if self.internalThread is not None and self.internalThread.is_alive():
            # enforce the do_run flag to true
            self.internalThread.do_run = True
        else:
            # create a new thread
            self.internalThread = threading.Thread(target=self.run)
            self.internalThread.start()

    def stop(self):
        # don't stop the thread itself, just set the flag to false
        if self.connected:
            if self.internalThread is not None and self.internalThread.is_alive():
                self.internalThread.do_run = False
            self.client_socket.close()
            self.connected = False

    def run(self):
        while getattr(self.internalThread, "do_run", True):
            try:
                if not self.connected:
                    self.connect_to_socket()
                    self.connected = True
                else:
                    self.receive_data()
            except socket.error:
                self.connected = False

    def connect_to_socket(self):
        if self.use_stub:
            self.client_socket = ClientSocketStub()
        else:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.client_socket.connect(('localhost', 12345))

    def receive_data(self):
        first_byte = self.client_socket.recv(1)
        if first_byte[0] is not 0:
            second_byte = self.client_socket.recv(1)
            data_type = int(ord(second_byte))
            data_length = (first_byte[0] - 1)
            self.handle_data(data_type, data_length)

    def handle_data(self, dataType, dataLength):
        if dataType == 1:
            self.HandleOrientationData(dataLength)
        elif dataType == 2:
            self.HandleGestureData(dataLength)
        elif dataType == 3:
            self.HandleExtendedDeviceData(dataLength)
        else:
            data = self.client_socket.recv(dataLength)
            # print(f'HandleData: {data}')

    def HandleOrientationData(self, dataLength):
        data = self.client_socket.recv(dataLength)
        f1 = struct.unpack('<f', bytes(data[0:4]))
        f2 = struct.unpack('<f', bytes(data[4:8]))
        f3 = struct.unpack('<f', bytes(data[8:12]))
        f4 = struct.unpack('<f', bytes(data[12:16]))
        self.dataHandler.HandleOrientationData(f1[0], f2[0], f3[0], f4[0])

    def HandleGestureData(self, dataLength):
        data = self.client_socket.recv(dataLength)
        self.dataHandler.HandleGestureData(int(ord(data)))

    def HandleExtendedDeviceData(self, dataLength):
        dataType = int(ord(self.client_socket.recv(1)))
        dataLength = (dataLength - 1)
        data = self.client_socket.recv(dataLength)
        self.dataHandler.HandleExtendedDeviceData(dataType, list(data))


class GFDataHandler:

    def __init__(self):
        self.OrientationData = []
        self.GestureData = []
        self.ExtendedDeviceData = []
        self.totalPackages = 0
        self.sentPackages = 0
        self.latestPackages = []
        self.currentPrediction = 0
        self.predictedGestures = []

    def HandleOrientationData(self, f1, f2, f3, f4):
        self.OrientationData = [f1, f2, f3, f4]

    def HandleGestureData(self, data):
        self.GestureData = data

    def HandleExtendedDeviceData(self, dataType, data):
        data_length = len(data)
        if data_length is 128 or data_length is 130:
            if data_length is 130:
                data = data[2:]  # removes first 2 bytes (assuming they are context info)
            self.ExtendedDeviceData.append(data)
            self.predictedGestures.append(self.currentPrediction)
            self.totalPackages += 1

    def get_latest_extended_device_data(self, packages=None):
        if packages is not None:
            if packages > self.totalPackages:
                # if the buffer is not full enough yet
                packages = self.totalPackages
            self.latestPackages = self.ExtendedDeviceData[-packages:]
        elif self.sentPackages is not self.totalPackages:
            # get the last packages that have not yet been sent
            self.latestPackages = self.ExtendedDeviceData[self.sentPackages:]
        else:
            self.latestPackages = []
        self.sentPackages = self.totalPackages
        return self.latestPackages

    def chain_all_packages(self, input):
        return list(chain.from_iterable(input))

    def get_latest_emg_data(self, packages=None, channels=8, demean=True):
        latest_array = self.get_latest_extended_device_data(packages)
        emg_values = self.chain_all_packages(latest_array)
        samples = int(len(emg_values) / channels)
        emg_data = np.zeros(shape=(samples, channels))
        for chan in range(0, channels):
            emg_data[:, chan] = np.array(emg_values[chan::channels])
        if demean:
            mean = emg_data.mean(axis=1)
            emg_data = emg_data - mean[:, np.newaxis]
        return emg_data

    def get_device_data_for_prediction(self, prediction=0):
        data_for_prediction = [x for (x, p) in zip(self.ExtendedDeviceData, self.predictedGestures) if p is prediction]
        return data_for_prediction

    def get_chained_device_data_for_prediction(self, prediction=0):
        data = self.get_device_data_for_prediction(prediction)
        return self.chain_all_packages(data)

    def get_emg_data_object(self, n_gestures=6):
        emg_data = symbionic.EmgData()
        for g in range(1, n_gestures + 1):
            emg_values = self.get_chained_device_data_for_prediction(g)
            if emg_values is not None and len(emg_values) > 0:
                emg_data.store_emg_values_in_gesture(emg_values, f'g{g}')
        return emg_data



def get_random_bytes(data_length):
    return bytearray(random.getrandbits(8) for _ in range(data_length))


def get_stubbed_extended_device_data():
    data = [
            bytearray([132]),  # data length
            chr(3),  # data type
            chr(8),  # number of channels?
            get_random_bytes  # ExtendedDeviceData package function
            ]
    return data


def get_stubbed_gesture_data():
    data = [
            bytearray([1]),  # data length
            chr(2),  # data type
            chr(1)  # gesture 1 to 6, formatted as string
            ]
    return data


class ClientSocketStub:

    def __init__(self):
        self._index = 0
        self._start_time = time.time()
        # pre-programmed data packages:
        self._data = [bytearray([0])] + \
            get_stubbed_extended_device_data() + \
            get_stubbed_gesture_data()
        # the time delay before a data package is being sent
        self.data_delay = 0.03

    def next(self):
        passed_time = time.time() - self._start_time
        if passed_time > self.data_delay:
            self._index += 1
        if self._index == 5:
            # reset
            self._start_time = time.time()
            self._index = 0

    def close(self):
        return True

    def recv(self, data_length):
        # very simple stub, doesn't even use the data_length input
        data = self._data[self._index]
        if callable(data):
            # if data is still a function, execute with the data_length:
            data = data(data_length)
        self.next()
        return data
