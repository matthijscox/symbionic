from symbionic._dataReceiver import GFDataHandler, get_random_bytes
import pytest
from symbionic._model import AbsMaxRandomForestModel

@pytest.fixture
def stored_data_handler():
    data_handler = GFDataHandler()
    for p in range(7):
        for j in range(200):
            data_handler.currentPrediction = p
            data_handler.HandleExtendedDeviceData(4, get_random_bytes(128))
    return data_handler


def assert_length(input_list, expected_length):
    list_length = len(input_list)
    assert list_length == expected_length, f"length is unexpected ({list_length} instead of {expected_length})."


def test_stored_handler():
    d = stored_data_handler()
    assert_length(d.get_chained_device_data_for_prediction(2), 200*128)


def test_absmax_random_forest():
    d = stored_data_handler()
    emg_data = d.get_emg_data_object()
    samples = emg_data.get_training_samples()
    gesture_model = AbsMaxRandomForestModel()
    gesture_model.fit(samples['X'],samples['y'])
