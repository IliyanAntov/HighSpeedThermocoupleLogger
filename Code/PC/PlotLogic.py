from PyQt5.QtCore import QRegularExpression
from PyQt5.QtWidgets import *

from PC.SharedParameters import SharedParameters
from PlotUI import Ui_Form
from PyQt5 import QtWidgets
import matplotlib.pyplot as plt


class PlotLogic:
    def __init__(self):
        self.ui = Ui_Form()
        self.form = QtWidgets.QWidget()

        self.channel_enabled = [False, False, False, False]
        self.data_processing_enabled = [False, False, False, False]
        self.temperature_prediction_enabled = [False, False, False, False]
        self.prediction_processing_enabled = [False, False, False, False]

        self.record_file_name = None

    def run(self, record_file_name):
        self.ui.setupUi(self.form)

        self.update_enabled_widgets()
        self.assign_button_functions()
        self.record_file_name = record_file_name

        self.form.show()

    def update_enabled_widgets(self):
        for widget_index in range(self.ui.ChannelParametersLayout.count()):
            widget = self.ui.ChannelParametersLayout.itemAt(widget_index).widget()
            if widget is None:
                continue
            elif isinstance(widget, QLabel):
                widget.setEnabled(True)
            else:
                widget.setEnabled(False)

        self.ui.ApplyButton.setEnabled(True)
        self.ui.CancelButton.setEnabled(True)
        self.ui.ViewPlotButton.setEnabled(True)

        channel_enable_checkbox_names = QRegularExpression("ChannelEnabled_\d")
        channel_enable_checkbox_widgets = self.form.findChildren(QCheckBox, channel_enable_checkbox_names)
        for widget in channel_enable_checkbox_widgets:
            widget.setEnabled(True)

        for i in range(4):
            self.update_channel_widgets_enable_status(i + 1)

    def update_channel_widgets_enable_status(self, channel):
        channel_index = channel - 1

        # Channel enabled
        checkbox_object_names = QRegularExpression(fr"[^ChannelEnabled].*_{channel}")
        checkbox_object_widgets = self.form.findChildren(QCheckBox, checkbox_object_names)
        # Enable/Disable relevant objects
        for widget in checkbox_object_widgets:
            if "PostProcess" in widget.objectName():
                if not self.temperature_prediction_enabled[channel_index]:
                    self.prediction_processing_enabled[channel_index] = False
                    widget.setChecked(False)
                    widget.setEnabled(False)
                    continue
            widget.setEnabled(self.channel_enabled[channel_index])

        # Data pre-processing
        data_processing_names = QRegularExpression(fr"DataLowPass.*_{channel}")
        data_processing_widgets = self.form.findChildren((QSpinBox, QDoubleSpinBox), data_processing_names)
        # Enable/Disable relevant objects
        for widget in data_processing_widgets:
            widget.setEnabled(self.data_processing_enabled[channel_index] and self.channel_enabled[channel_index])

        # Temperature prediction
        temperature_prediction_names = QRegularExpression(fr"Prediction.*_{channel}")
        temperature_prediction_widgets = self.form.findChildren((QSpinBox, QDoubleSpinBox),
                                                                temperature_prediction_names)
        # Enable/Disable relevant objects
        for widget in temperature_prediction_widgets:
            widget.setEnabled(
                self.temperature_prediction_enabled[channel_index] and self.channel_enabled[channel_index])

        # Prediction post-processing
        post_processing_names = QRegularExpression(fr"PostProcess.*_{channel}")
        post_processing_widgets = self.form.findChildren((QSpinBox, QDoubleSpinBox), post_processing_names)
        # Enable/Disable relevant objects
        for widget in post_processing_widgets:
            widget.setEnabled(self.prediction_processing_enabled[channel_index] and self.channel_enabled[channel_index])

    def toggle_channel(self, channel):
        channel_index = channel - 1
        self.channel_enabled[channel_index] = not self.channel_enabled[channel_index]
        self.update_channel_widgets_enable_status(channel)

    def toggle_data_processing(self, channel):
        channel_index = channel - 1
        self.data_processing_enabled[channel_index] = not self.data_processing_enabled[channel_index]
        self.update_channel_widgets_enable_status(channel)

    def toggle_temperature_prediction(self, channel):
        channel_index = channel - 1
        self.temperature_prediction_enabled[channel_index] = not self.temperature_prediction_enabled[channel_index]
        self.update_channel_widgets_enable_status(channel)

    def toggle_prediction_processing(self, channel):
        channel_index = channel - 1
        self.prediction_processing_enabled[channel_index] = not self.prediction_processing_enabled[channel_index]
        self.update_channel_widgets_enable_status(channel)

    def assign_button_functions(self):
        self.ui.ChannelEnabled_1.clicked.connect(lambda: self.toggle_channel(1))
        self.ui.ChannelEnabled_2.clicked.connect(lambda: self.toggle_channel(2))
        self.ui.ChannelEnabled_3.clicked.connect(lambda: self.toggle_channel(3))
        self.ui.ChannelEnabled_4.clicked.connect(lambda: self.toggle_channel(4))
        self.ui.DataLowPassEnabled_1.clicked.connect(lambda: self.toggle_data_processing(1))
        self.ui.DataLowPassEnabled_2.clicked.connect(lambda: self.toggle_data_processing(2))
        self.ui.DataLowPassEnabled_3.clicked.connect(lambda: self.toggle_data_processing(3))
        self.ui.DataLowPassEnabled_4.clicked.connect(lambda: self.toggle_data_processing(4))
        self.ui.PredictionEnabled_1.clicked.connect(lambda: self.toggle_temperature_prediction(1))
        self.ui.PredictionEnabled_2.clicked.connect(lambda: self.toggle_temperature_prediction(2))
        self.ui.PredictionEnabled_3.clicked.connect(lambda: self.toggle_temperature_prediction(3))
        self.ui.PredictionEnabled_4.clicked.connect(lambda: self.toggle_temperature_prediction(4))
        self.ui.PostProcessLowPassEnabled_1.clicked.connect(lambda: self.toggle_prediction_processing(1))
        self.ui.PostProcessLowPassEnabled_2.clicked.connect(lambda: self.toggle_prediction_processing(2))
        self.ui.PostProcessLowPassEnabled_3.clicked.connect(lambda: self.toggle_prediction_processing(3))
        self.ui.PostProcessLowPassEnabled_4.clicked.connect(lambda: self.toggle_prediction_processing(4))

        self.ui.ViewPlotButton.clicked.connect(self.plot)

    def plot(self):
        # with open(SharedParameters.record_folder_dir + plot_file_name) as f:
        #     print(f.readlines())
        plt.plot([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], color="red")
        plt.show()

