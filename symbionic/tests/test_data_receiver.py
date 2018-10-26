import symbionic
import time


def get_running_receiver_stub(delay=0.3):
    receiver = symbionic.GFDataReceiverSocket(stub=True)
    receiver.start()
    receiver.client_socket.data_delay = delay
    return receiver


def assert_data_length(data,expected_length):
    data_length = len(data)
    assert data_length == expected_length, f"expected data length of {expected_length}, but found {data_length}"


def test_socket_stub():
    stub = symbionic._dataReceiver.ClientSocketStub()
    # turn off the stubbed data delay for the test
    stub.data_delay = 0
    time.sleep(0.01)
    # ignore the very first byte
    stub.recv(1)
    # receive first package
    data = stub.recv(1)
    assert isinstance(data, (bytes, bytearray)), 'Received data is not a bytearray'
    data_length = data[0]-1
    assert data_length is 131, f"data length should have been 130, but it is {data_length}"
    # receive 2nd package
    data = stub.recv(1)
    assert int(ord(data)) is 3
    # 3rd package
    data = stub.recv(1)
    assert int(ord(data)) is 8
    # 4th package
    data = stub.recv(data_length-1)
    assert len(list(data)) == 130, f"data should have 130 elements, instead it has {len(list(data))}"


def test_receiver_stub():
    receiver = get_running_receiver_stub(0.05)
    time.sleep(0.16)  # wait for 3 packages
    device_data = receiver.dataHandler.get_latest_extended_device_data()
    receiver.stop()
    assert_data_length(device_data, 3)
    package_lengths = [len(x) for x in device_data]
    assert all(x == 128 for x in package_lengths), \
        f"expected all packages to have length 128, instead found lengths = {package_lengths}"
    # test manual data retrieval
    device_data = receiver.dataHandler.get_latest_extended_device_data(2)
    assert_data_length(device_data, 2)
    # test converted data
    emg_data = receiver.dataHandler.get_latest_emg_data(2)
    expected_shape = (int(128*2/8), 8)
    assert emg_data.shape == expected_shape, f"Shape should be {expected_shape}, but it was {emg_data.shape}"
    # test retrieval of too much data


def test_receiver_restart():
    receiver = get_running_receiver_stub()
    receiver.stop()
    assert not receiver.connected, "Receiver should not have been running"
    assert not receiver.internalThread.do_run, "Thread should have not been running"
    receiver.start()
    time.sleep(0.05)
    assert receiver.connected, "Receiver should have been running"
    assert receiver.internalThread.do_run, "Thread should have been running"
    receiver.stop()
    assert not receiver.connected, "Receiver should not have been running"
    assert not receiver.internalThread.do_run, "Thread should have not been running"


def test_data_handler_prediction_update():
    receiver = get_running_receiver_stub(0.03)
    time.sleep(0.04)
    receiver.dataHandler.currentPrediction = 2
    time.sleep(0.04)
    receiver.stop()
    assert receiver.dataHandler.predictedGestures[-1] is 2
    assert len(receiver.dataHandler.get_device_data_for_prediction(2))>1
