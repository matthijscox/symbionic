import symbionic
import pandas as pd


def test_list_to_dataframe():
    emg_data = symbionic.EmgData()
    df = emg_data.convert_emg_values_to_dataframe([1.1]*emg_data.channels*2,demean=False)
    assert df.shape == (2, emg_data.channels + 1), 'Output shape does not match'
    assert df[emg_data.channel_names[0]].tolist() == [1.1]*2


def test_data_retrieval():
    emg_data = symbionic.EmgData()
    emg_data.store_emg_values_in_gesture([1.1]*emg_data.channels*2,'g1')
    data = emg_data.get_data_from_gesture('g1')
    assert isinstance(data,pd.DataFrame)
    assert emg_data.get_data_from_gesture('g2') is None

