import symbionic
import pandas as pd
import pytest
import os


@pytest.fixture
def raw_emg_data_sample(channels=8):
    # very simple raw data sample for now, just the same value repeated over and over
    return [1.1]*channels*2


@pytest.fixture
def data_directory():
    return symbionic.example_data_directory()


@pytest.fixture
def load_emg_data_single_gesture():
    emg_data = symbionic.EmgData()
    emg_data.load(data_directory() + 'raw2.bin',gesture='g2')
    emg_data.label_patterns()
    return emg_data


def test_list_to_dataframe():
    emg_data = symbionic.EmgData()
    df = emg_data.convert_emg_values_to_dataframe(raw_emg_data_sample(),demean=False)
    assert df.shape == (2, emg_data.channels + 1), 'Output shape does not match'
    assert df[emg_data.channel_names[0]].tolist() == [1.1]*2


def test_data_retrieval():
    emg_data = symbionic.EmgData()
    emg_data.store_emg_values_in_gesture(raw_emg_data_sample(),'g1')
    data = emg_data.get_data_from_gesture('g1')
    assert isinstance(data,pd.DataFrame)
    assert emg_data.get_data_from_gesture('g2') is None


def test_binary_data_loading_and_retrieval():
    emg_data = load_emg_data_single_gesture()
    assert emg_data.has_data['g1'] is False, 'Gesture 1 should not have data'
    assert emg_data.get_data_from_gesture('g1') is None, 'Gesture 1 should not have data'
    assert emg_data.has_data['g2'], 'Gesture 2 should have data'
    assert isinstance(emg_data.get_data_from_gesture('g2'),pd.DataFrame), 'Gesture 2 should have data'


def test_windowed_data_retrieval():
    emg_data = load_emg_data_single_gesture()
    step_time = 0.062
    window_size = 130
    step_size = int(step_time * emg_data.sample_rate)
    samples = emg_data.get_training_samples(step = step_time)
    assert samples['X'].shape == (984, window_size, 8), 'Output data shape is unexpected'
    gesture_data = emg_data.get_data_from_gesture('g2')
    actual_sample = samples['X'][1,:,4] # take the 2nd sample of the 5th gesture
    expected_sample = gesture_data['emg5'].values[step_size:step_size+window_size] # manually create the windowed sample
    assert all(actual_sample == expected_sample), 'Sample is not as expected'
    assert all((samples['y'] == 0) | (samples['y'] == 2)), 'Expected only the relaxed and 1 other gesture'
