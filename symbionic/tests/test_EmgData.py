import symbionic


def test_constructor():
    emg_data = symbionic.EmgData()
    assert isinstance(emg_data, symbionic.EmgData)