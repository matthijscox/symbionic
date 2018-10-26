import random
import numpy as np
import symbionic
from sklearn.ensemble import RandomForestClassifier
from keras.utils import np_utils

def prepare_data_for_keras(input_data):
    # only select last 195 samples
    output_data = input_data[-195:, :]
    # preparation for 1D Neural Network
    # TODO: it's too slow for fast updating at 0.1 second intervals...
    output_data = np.apply_along_axis(lambda x: symbionic.calc_envelope(x,smooth=51), 0, output_data)
    output_data = output_data.reshape((1,output_data.shape[0]*output_data.shape[1]))
    return output_data


def absmax_at_end(signal):
    return np.max(abs(signal[-50:]))


def take_max_abs(input_data):
    features =  np.apply_along_axis(absmax_at_end, 0, input_data)
    features = features.reshape(1, -1)
    return features


class FakeModel:
    def __init__(self, n_gestures=6):
        self.number_of_gestures = n_gestures

    def predict(self, input_data):
        p = self.number_of_gestures*[0]
        p[random.randrange(self.number_of_gestures)] = 1
        return p


class GestureModel:
    def __init__(self,model=None, data_prepare=None):
        self.model = model
        self.data_prepare = data_prepare
        self.collapse = False

    def predict(self,input_data):
        prediction = 0
        input_data = self.prepare(input_data)
        if self.model is not None:
            prediction = self.model.predict(input_data)
            if self.collapse:
                prediction = np.argmax(prediction)
        return prediction

    def prepare(self,input_data):
        if self.data_prepare is not None:
            output_data = self.data_prepare(input_data)
        else:
            output_data = input_data
        return output_data


class PredictionBuffer:
    def __init__(self, n_gestures=6):
        self.number_of_gestures = n_gestures
        self.buffer = [[] for n in range(self.number_of_gestures)]
        self.stored_predictions = 1

    def append(self,predictions):
        for gesture, gesture_probability in zip(range(self.number_of_gestures), predictions):
            self.buffer[gesture].append(gesture_probability)
        self.stored_predictions += 1

    def get_predictions(self,number_of_predictions=30):
        predictions = self.buffer
        predictions = [p[-number_of_predictions:] for p in predictions]
        return np.array(predictions).transpose()


class AbsMaxRandomForestModel(GestureModel):
    def __init__(self):
        super().__init__(model=RandomForestClassifier(), data_prepare=take_max_abs)

    def fit(self, data, labels):
        max_abs_of_data = np.apply_along_axis(absmax_at_end, 1, data)
        dummy_y = np_utils.to_categorical(labels)
        self.model.fit(max_abs_of_data, dummy_y)
