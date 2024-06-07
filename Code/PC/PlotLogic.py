import copy
import json
import sys

import numpy as np
from PyQt5.QtCore import QRegularExpression
from PyQt5.QtWidgets import *

from PC.Record import Record
from PC.SharedParameters import SharedParameters
from PlotUI import Ui_Form
from PyQt5 import QtWidgets
import matplotlib.pyplot as plt


class PlotLogic:
    def __init__(self):
        # TODO: delete
        self.app = QtWidgets.QApplication(sys.argv)
        self.ui = Ui_Form()
        self.form = QtWidgets.QWidget()
        self.record_file_name = None
        self.record = Record()
        self.record_saved = Record()
        self.available_channel_records = []
        self.changes_made = False

    def run(self, record_file_name):
        self.ui.setupUi(self.form)

        self.record_file_name = record_file_name
        self.load_data()

        self.update_enabled_widgets()
        self.assign_button_functions()

        self.form.show()
        # TODO: delete
        sys.exit(self.app.exec_())

    def update_enabled_widgets(self):
        for widget_index in range(self.ui.ChannelParametersLayout.count()):
            widget = self.ui.ChannelParametersLayout.itemAt(widget_index).widget()
            if widget is None:
                continue
            elif isinstance(widget, QLabel):
                widget.setEnabled(True)
            else:
                widget.setEnabled(False)

        self.ui.ViewPlotButton.setEnabled(True)

        for i in range(4):
            channel_enable_checkbox_widget = self.form.findChild(QCheckBox, f"ChannelEnabled_{i + 1}")
            channel_enable_checkbox_widget.setEnabled(True)
            channel_enable_checkbox_widget.setChecked(self.record.channels[i].available)

            if not self.available_channel_records[i]:
                channel_enable_checkbox_widget.setEnabled(False)
                channel_label_widget = self.form.findChild(QLabel, f"ChannelLabel_{i + 1}")
                channel_label_widget.setText("Unavailable")
                continue

            self.update_channel_widgets_enable_status(i + 1)

    def update_channel_widgets_enable_status(self, channel):
        channel_index = channel - 1

        self.ui.ApplyButton.setEnabled(self.changes_made)
        self.ui.CancelButton.setEnabled(self.changes_made)

        # Channel enabled
        checkbox_object_names = QRegularExpression(fr"[^ChannelEnabled].*_{channel}")
        checkbox_object_widgets = self.form.findChildren(QCheckBox, checkbox_object_names)
        # Enable/Disable checkboxes
        for widget in checkbox_object_widgets:
            if "PostProcess" in widget.objectName():
                if not self.record.channels[channel_index].temperature_prediction_enabled:
                    self.record.channels[channel_index].prediction_processing_enabled = False
                    widget.setChecked(False)
                    widget.setEnabled(False)
                    continue

            widget.setEnabled(self.record.channels[channel_index].available)


        # Data pre-processing
        data_processing_names = QRegularExpression(fr"DataLowPass.*_{channel}")
        data_processing_widgets = self.form.findChildren((QSpinBox, QDoubleSpinBox), data_processing_names)
        # Enable/Disable relevant objects
        for widget in data_processing_widgets:
            widget.setEnabled(self.record.channels[channel_index].data_processing_enabled and self.record.channels[channel_index].available)

        # Temperature prediction
        temperature_prediction_names = QRegularExpression(fr"Prediction.*_{channel}")
        temperature_prediction_widgets = self.form.findChildren((QSpinBox, QDoubleSpinBox),
                                                                temperature_prediction_names)
        # Enable/Disable relevant objects
        for widget in temperature_prediction_widgets:
            widget.setEnabled(
                self.record.channels[channel_index].temperature_prediction_enabled and self.record.channels[channel_index].available)

        # Prediction post-processing
        post_processing_names = QRegularExpression(fr"PostProcess.*_{channel}")
        post_processing_widgets = self.form.findChildren((QSpinBox, QDoubleSpinBox), post_processing_names)
        # Enable/Disable relevant objects
        for widget in post_processing_widgets:
            widget.setEnabled(self.record.channels[channel_index].prediction_processing_enabled and self.record.channels[channel_index].available)

    def toggle_channel(self, channel):
        self.changes_made = True
        channel_index = channel - 1
        self.record.channels[channel_index].available = not self.record.channels[channel_index].available
        self.update_channel_widgets_enable_status(channel)

    def toggle_data_processing(self, channel):
        self.changes_made = True
        channel_index = channel - 1
        self.record.channels[channel_index].data_processing_enabled = not self.record.channels[channel_index].data_processing_enabled
        self.update_channel_widgets_enable_status(channel)

    def toggle_temperature_prediction(self, channel):
        self.changes_made = True
        channel_index = channel - 1
        self.record.channels[channel_index].temperature_prediction_enabled = not self.record.channels[channel_index].temperature_prediction_enabled
        self.update_channel_widgets_enable_status(channel)

    def toggle_prediction_processing(self, channel):
        self.changes_made = True
        channel_index = channel - 1
        self.record.channels[channel_index].prediction_processing_enabled = not self.record.channels[channel_index].prediction_processing_enabled
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
        self.ui.ApplyButton.clicked.connect(self.update_parameters)
        self.ui.CancelButton.clicked.connect(self.restore_saved_parameters)

    def load_data(self):
        with open(SharedParameters.record_folder_dir + self.record_file_name) as file:
            file_json = json.load(file)

        self.record.interval_us = file_json["record_interval_us"]
        self.record.length_ms = file_json["record_length_ms"]

        channel_index = 0
        channel_names = file_json["channel_data"]
        for channel_name in channel_names:
            channel_data_json = copy.deepcopy(file_json["channel_data"][channel_name])

            if channel_data_json is None:
                self.record.channels[channel_index].available = False
                channel_index += 1
                continue

            self.record.channels[channel_index].tc_type = channel_data_json["tc_type"]
            self.record.channels[channel_index].raw_data = channel_data_json["raw_data"]

            # Data processing
            self.record.channels[channel_index].data_processing_enabled = channel_data_json["data_processing"]["enabled"]
            self.record.channels[channel_index].data_filter_order = channel_data_json["data_processing"]["filter_order"]
            self.record.channels[channel_index].data_filter_freq_khz = channel_data_json["data_processing"]["filter_corner_frequency_khz"]

            # Temperature prediction
            self.record.channels[channel_index].temperature_prediction_enabled = channel_data_json["temperature_prediction"]["enabled"]
            self.record.channels[channel_index].prediction_time_constant_ms = channel_data_json["temperature_prediction"]["time_constant_ms"]
            self.record.channels[channel_index].prediction_queue_length = channel_data_json["temperature_prediction"]["record_queue_length"]

            # Prediction processing
            self.record.channels[channel_index].prediction_processing_enabled = channel_data_json["prediction_processing"]["enabled"]
            self.record.channels[channel_index].post_process_filter_order = channel_data_json["prediction_processing"]["filter_order"]
            self.record.channels[channel_index].post_process_filter_freq_khz = channel_data_json["prediction_processing"]["filter_corner_frequency_khz"]

            self.display_saved_parameter_values(channel_index)
            self.update_channel_widgets_enable_status(channel_index + 1)
            channel_index += 1

        for i in range(self.record.num_of_channels):
            self.available_channel_records.append(self.record.channels[i].available)

    def display_saved_parameter_values(self, channel_index):
        channel_enabled_widget = self.form.findChild(QCheckBox, f"ChannelEnabled_{channel_index+1}")
        channel_enabled_widget.setChecked(self.record.channels[channel_index].available)
        tc_type_widget = self.form.findChild(QComboBox, f"ChannelTcType_{channel_index+1}_fixed")
        tc_type_widget.setCurrentText(self.record.channels[channel_index].tc_type)

        # Data processing
        data_processing_enabled_widget = self.form.findChild(QCheckBox, f"DataLowPassEnabled_{channel_index + 1}")
        data_processing_enabled_widget.setChecked(self.record.channels[channel_index].data_processing_enabled)
        data_filter_order_widget = self.form.findChild(QSpinBox, f"DataLowPassOrder_{channel_index + 1}")
        data_filter_order_widget.setValue(self.record.channels[channel_index].data_filter_order)
        data_filter_freq_widget = self.form.findChild(QDoubleSpinBox, f"DataLowPassCornerFrequency_{channel_index + 1}")
        data_filter_freq_widget.setValue(self.record.channels[channel_index].data_filter_freq_khz)

        # Temperature prediction
        prediction_enabled_widget = self.form.findChild(QCheckBox, f"PredictionEnabled_{channel_index + 1}")
        prediction_enabled_widget.setChecked(self.record.channels[channel_index].temperature_prediction_enabled)
        prediction_time_constant_widget = self.form.findChild(QDoubleSpinBox, f"PredictionTimeConstant_{channel_index + 1}")
        prediction_time_constant_widget.setValue(self.record.channels[channel_index].prediction_time_constant_ms)
        prediction_queue_length_widget = self.form.findChild(QSpinBox, f"PredictionQueueLength_{channel_index + 1}")
        prediction_queue_length_widget.setValue(self.record.channels[channel_index].prediction_queue_length)

        # Prediction processing
        prediction_processing_enabled_widget = self.form.findChild(QCheckBox, f"PostProcessLowPassEnabled_{channel_index + 1}")
        prediction_processing_enabled_widget.setChecked(self.record.channels[channel_index].prediction_processing_enabled)
        prediction_filter_order_widget = self.form.findChild(QSpinBox, f"PostProcessLowPassOrder_{channel_index + 1}")
        prediction_filter_order_widget.setValue(self.record.channels[channel_index].post_process_filter_order)
        prediction_filter_freq_widget = self.form.findChild(QDoubleSpinBox, f"PostProcessLowPassCornerFrequency_{channel_index + 1}")
        prediction_filter_freq_widget.setValue(self.record.channels[channel_index].post_process_filter_freq_khz)

        self.record_saved = copy.deepcopy(self.record)

    def update_parameters(self):
        self.changes_made = False
        self.record_saved = copy.deepcopy(self.record)
        for i in range(self.record.num_of_channels):
            if self.record.channels[i].available:
                self.display_saved_parameter_values(i)
        self.update_enabled_widgets()

    def restore_saved_parameters(self):
        self.changes_made = False
        self.record = copy.deepcopy(self.record_saved)
        for i in range(self.record.num_of_channels):
            if self.record.channels[i].available:
                self.display_saved_parameter_values(i)
        self.update_enabled_widgets()

    def plot(self):
        channel_colors = ["red", "blue", "green", "orange"]
        x_values = np.linspace(0, self.record.length_ms, int(self.record.length_ms/(self.record.interval_us/1000)))
        for i in range(self.record.num_of_channels):
            if not self.record.channels[i].available:
                continue
            y_values = self.record.channels[i].raw_data
            plt.plot(x_values, y_values, color=channel_colors[i], label=f"Channel {i + 1}")

        plt.title(self.record_file_name.replace(".json", ""), pad=15)
        plt.xlabel("Time [ms]")
        plt.ylabel("Temperature [°C]")
        plt.legend()

        plt.show()

# TODO: delete
if __name__ == "__main__":
    plot_window = PlotLogic()
    plot_window.run("11-30-00_06-06-2024.json")