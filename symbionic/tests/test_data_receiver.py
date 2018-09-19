import symbionic
import time


def test_socket_stub():
    stub = symbionic._dataReceiver.ClientSocketStub()
    stub.data_delay = 0
    time.sleep(0.01)
    stub.recv(1) # ignore the very first byte
    # receive first package
    data = stub.recv(1)
    assert isinstance(data, (bytes, bytearray)), 'Received data is not a bytestring'
    data_length = data[0]-1
    assert data_length is 130, f"data length should have been 130, but it is {data_length}"
    # receive 2nd package
    data = stub.recv(1)
    assert int(ord(data)) is 3
    # 3rd package
    data = stub.recv(1)
    assert int(ord(data)) is 8
    # 4th package
    data = stub.recv(data_length)
    assert len(list(data)) == 130, "data is not the right length"


def test_receiver_stub():
    # set up the receiver with a stubbed socket
    dataHandler = symbionic.GFDataHandler()
    receiver = symbionic.GFDataReceiverSocket(dataHandler)
    receiver.connected = True
    stub = symbionic._dataReceiver.ClientSocketStub()
    stub.data_delay = 0.05
    receiver.client_socket = stub
    # get data on the fly
    receiver.start()
    time.sleep(0.17)
    device_data = dataHandler.getLatestExtendedDeviceData()
    assert len(device_data) == 3, f"expected 3 data packages, found only {len(device_data)}"
    receiver.stop()
