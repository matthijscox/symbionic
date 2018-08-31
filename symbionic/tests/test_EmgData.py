import symbionic
import pandas as pd
import pytest


@pytest.fixture
def raw_emg_data_sample(channels=8):
    # very simple raw data sample for now, just the same value repeated over and over
    return [1.1]*channels*2


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

