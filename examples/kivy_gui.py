#https://kivy.org/doc/stable/installation/installation-windows.html
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from examples.graph import Graph, MeshLinePlot
from symbionic import GFDataReceiverSocket
import time


class Logic(BoxLayout):
    def __init__(self):
        super(Logic, self).__init__()
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.graphs = []
        self.plots = []
        self.receiver = GFDataReceiverSocket(stub=True)
        self.number_of_channels = 8
        self.number_of_packages = 15

    def start(self):
        self.receiver.start()
        Clock.schedule_interval(self.get_value, 0.1)

    def stop(self):
        self.receiver.stop()
        Clock.unschedule(self.get_value)

    def get_value(self, dt):
        data = self.receiver.dataHandler.get_latest_emg_data(self.number_of_packages)
        buffer_size = data.shape[0]  # data size
        x_axis = [x for x in range(0, buffer_size)]  # x-axis data of graph
        for chan in range(self.number_of_channels):
            single_channel = data[:, chan].tolist()
            self.plots[chan].points = [(x, y) for (x, y) in zip(x_axis,single_channel)]
            self.graphs[chan].xmax = buffer_size

    def add_graph(self):
        graph = Graph(xmin=-0, xmax=100, ymin=-150, ymax=150, padding=5)
        plot = MeshLinePlot(color=[1, 0, 0, 1])
        graph.add_plot(plot)
        self.plots.append(plot)
        self.graphs.append(graph)
        self.ids.upper_box.add_widget(graph)


class MyApp(App):
    def build(self):
        self.root = Builder.load_file("look.kv")
        for g in range(self.root.number_of_channels):
            self.root.add_graph()
        return self.root


if __name__ == "__main__":
    MyApp().run()
