import socket
import struct
import threading
import numpy as np
from itertools import chain
import struct
import random
import time


class GFDataReceiverSocket:

    def __init__(self, data_handler=None):
        self.connected = False
        self.client_socket = None
        if data_handler is None:
            data_handler = GFDataHandler()
        self.dataHandler = data_handler
        self.internalThread = threading.Thread(target=self.run)

    def start(self):
        self.internalThread.start()

    def run(self):
        while getattr(self.internalThread, "do_run", True):
            try:
                if not self.connected:
                    self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                    self.client_socket.connect(('localhost', 12345))
                    self.connected = True
                else:
                    data = self.client_socket.recv(1)
                    if data[0] is not 0:
                        data2 = self.client_socket.recv(1)
                        dataType = int(ord(data2))
                        # print(f"dataType = {dataType}")
                        dataLength = (data[0] - 1)
                        # print(f"dataLength = {dataLength}")
                        self.HandleData(dataType, dataLength)
            except socket.error:
                self.connected = False

    def stop(self):
        self.internalThread.do_run = False
        self.internalThread.join()
        self.client_socket.close()
        self.connected = False

    def HandleData(self, dataType, dataLength):
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
    OrientationData = []
    GestureData = []
    ExtendedDeviceData = []
    totalPackages = 0
    sentPackages = 0
    latestPackages = []

    def HandleOrientationData(self, f1,f2,f3,f4):
        self.OrientationData = [f1,f2,f3,f4]

    def HandleGestureData(self, data):
        self.GestureData = data

    def HandleExtendedDeviceData(self, dataType, data):
        buffered_data = data[2:]  # removes first 2 bytes (assuming they are useless)
        self.ExtendedDeviceData.append(buffered_data)
        self.totalPackages += 1

    def getLatestExtendedDeviceData(self):
        if self.sentPackages is not self.totalPackages:
            self.latestPackages = self.ExtendedDeviceData[self.sentPackages:]
        else:
            self.latestPackages = []
        self.sentPackages = self.totalPackages
        return self.latestPackages

    def sendChannelData(self):
        latestArray = self.latestPackages
        channel8 = list(chain.from_iterable(latestArray))
        return channel8[0::8]
        #latestArray = list(chain.from_iterable(latestArray))
        #return latestArray[0::8]

#task last time:
#convert channel8 into a n by 8 numpy array.
#As example, see code symbionic hex to bi


def get_random_bytes(data_length):
    return bytearray(random.getrandbits(8) for _ in range(data_length))


class ClientSocketStub():

    def __init__(self):
        self.index = 0
        self.start_time = time.time()
        self.data_delay = 0.3 # the time delay before a data package is being sent
        self.data = {0: bytearray([0]),
                     1: bytearray([131]),
                     2: chr(3),
                     3: chr(8),
                     4: get_random_bytes(130)
                     }

    def next(self):
        passed_time = time.time() - self.start_time
        if passed_time > self.data_delay:
            self.index += 1
        if self.index == 5:
            # reset
            self.start_time = time.time()
            self.index = 0

    def close(self):
        return True

    def recv(self,data_length):
        # very simple stub, doesn't even use the data_length input
        data = self.data[self.index]
        self.next()
        return data
