#https://kivy.org/doc/stable/installation/installation-windows.html
#follow installation guide!!
from kivy.lang import Builder
from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import ObjectProperty, StringProperty
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
import symbionic
from symbionic.gui.graph import Graph, LinePlot
from symbionic._model import FakeModel, GestureModel, PredictionBuffer, take_max_abs
from sklearn.externals import joblib
import os

class DataIterator:
    def __init__(self, data):
        self.index = 0
        self.step = 1
        self.size = 1
        self.data = data

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.data):
            #raise StopIteration
            self.index = 0 # start over
        start_index = self.index
        end_index = start_index + self.step + self.size - 1
        self.index = start_index + self.step
        return self.data[start_index:end_index, :]

    def goto(self, index):
        self.index = index


class FileDataStub:
    def __init__(self):
        emg_data = symbionic.EmgData()
        emg_data.load(symbionic.example_data_directory() + "raw3.bin")
        emg_array = emg_data.data['g1'].drop('time', axis=1).values
        emg_iterator = DataIterator(emg_array)
        emg_iterator.step = 80
        emg_iterator.size = 500
        self.emg_iterator = emg_iterator

    def __next__(self):
        return next(self.emg_iterator)


class RandomForestModel:
    def __init__(self):
        # using a pre-trained random forest stored via joblib
        self.fitted_model = joblib.load('maxabs_forest.joblib')

    def predict(self,data):
        # need to convert to a 1D array for single sample data
        predictions = self.fitted_model.predict(data)
        return predictions.ravel()


def save_raw_data(receiver,file_path):
    device_data = receiver.dataHandler.ExtendedDeviceData
    chained_data = receiver.dataHandler.chain_all_packages(device_data)
    # save in binary format
    output_file = open(file_path, "wb")
    output_file.write(bytearray(chained_data))
    output_file.close()


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class Root(BoxLayout):
    def __init__(self):
        super().__init__()
        self.number_of_channels = 8
        self.number_of_packages = 15
        self.number_of_gestures = 7
        self.update_interval = 0.1
        self.graphs = []
        self.plots = []
        self.cbs = []
        self.receiver = symbionic.GFDataReceiverSocket(stub=True)
        self.fake_data = FileDataStub()
        self.rawDataBox = []
        self.gestureGraph = []
        self.gestureCheckbox = []
        self.gestureModel = GestureModel(FakeModel(self.number_of_gestures), data_prepare=take_max_abs)
        #self.gestureModel.model = RandomForestModel()
        self.predictions = PredictionBuffer(self.number_of_gestures)
        self.selected_gesture = StringProperty()
        self._popup = ObjectProperty(None)
        self.saving_method = save_raw_data

    def init_graphs(self):
        self.rawDataBox = GraphBox(self.ids.raw_data_box, self.number_of_channels)
        self.rawDataBox.init_graphs()
        self.gestureGraph = GraphBox(self.ids.gesture_graph, self.number_of_gestures)
        self.gestureGraph.ylim = (-0.1,1.1)
        self.gestureGraph.init_graphs()


    def init_checkbox(self):
        self.gestureCheckbox = clsCheckBox(self, self.ids.gesture_checkbox, self.number_of_gestures, "gestures")
        self.gestureCheckbox.init_cbs()

    def start(self):
        self.receiver.start()
        Clock.schedule_interval(self.update_gui, self.update_interval)

    def stop(self):
        self.receiver.stop()
        Clock.unschedule(self.update_gui)

    def update_gui(self, dt):
        data = self.receiver.dataHandler.get_latest_emg_data(self.number_of_packages)
        #data = next(self.fake_data)
        self.rawDataBox.update_graphs(data)
        self.update_predictions(data)
        self.update_prediction_graphs()

    def update_predictions(self,data):
        predictions = self.gestureModel.predict(data)
        self.predictions.append(predictions)

    def update_prediction_graphs(self):
        predictions = self.predictions.get_predictions()
        self.gestureGraph.update_graphs(predictions)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_raw_data_save(self):
        self.saving_method = save_raw_data
        self.show_save()

    def show_save(self):
        # https://kivy.org/doc/stable/api-kivy.uix.filechooser.html
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def save(self, path, filename):
        file_path = os.path.join(path, filename)
        self.saving_method(self.receiver,file_path)
        self.dismiss_popup()


class clsCheckBox:
    def __init__(self, Logic, cbox_id, number_of_cbs, CB_group):
        self.Logic = Logic
        self.cbox_id = cbox_id
        self.number_of_cbs = number_of_cbs
        self.CB_group = CB_group
        self.cbs = []
        self.ylim = (-150,150)

    def init_cbs(self):
        for g in range(self.number_of_cbs):
            self.add_cb(self.cbox_id)

    def add_cb(self, box_id):
        cbs = CheckBox(group=self.CB_group)
        cbs.bind(active=self.on_checkbox_active)
        self.cbs.append(cbs)
        box_id.add_widget(cbs)

    def on_checkbox_active(self, checkboxId, isActive):
        if isActive:
           self.Logic.selected_gesture = str(self.cbs.index(checkboxId) + 1)

class GraphBox:
    def __init__(self, box_id, number_of_graphs):
        self.box_id = box_id
        self.number_of_graphs = number_of_graphs
        self.graphs = []
        self.plots = []
        self.ylim = (-150,150)

    def init_graphs(self):
        for g in range(self.number_of_graphs):
            self.add_graph(self.box_id)

    def add_graph(self, box_id):
        graph = Graph(xmin=-0, xmax=100, ymin=self.ylim[0], ymax=self.ylim[1])
        plot = LinePlot(color=[1, 0, 0, 1], line_width=1.1)
        graph.add_plot(plot)
        self.plots.append(plot)
        self.graphs.append(graph)
        box_id.add_widget(graph)

    def update_graphs(self,data):
        buffer_size = data.shape[0]  # data size
        x_axis = [x for x in range(0, buffer_size)]  # x-axis data of graph
        for graph in range(self.number_of_graphs):
            single_graph = data[:, graph].tolist()
            self.plots[graph].points = [(x, y) for (x, y) in zip(x_axis,single_graph)]
            self.graphs[graph].xmax = buffer_size


class SymbionicApp(App):
    Window.size = (1000,600)

    def build(self):
        self.root = Builder.load_file("look.kv")
        self.root.init_graphs()
        self.root.init_checkbox()
        return self.root

Factory.register('Root', cls=Root)
#Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)

if __name__ == "__main__":
    SymbionicApp().run()
