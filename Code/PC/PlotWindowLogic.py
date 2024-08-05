import copy
import json
import math
import multiprocessing
import os
import sys
from functools import partial
from multiprocessing import Pool

import jsonpickle
import matplotlib
import numpy as np
from matplotlib.backend_tools import ToolBase
from pandas import DataFrame, Series
from scipy import signal

from PyQt5.QtCore import QRegularExpression
from PyQt5.QtWidgets import *
from scipy.optimize import curve_fit

from PC.Record import Record
from PC.Parameters import Parameters
from PlotWindowUI import Ui_Form
from PyQt5 import QtWidgets
import matplotlib.pyplot as plt

if not sys.warnoptions:
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning,
                            message="Treat the new Tool classes introduced in v1.5 as experimental for now")

matplotlib.rcParams["toolbar"] = "toolmanager"
plot_data = {}
plot_name = ""

class PlotLogic:
    def __init__(self):
        # NOTE: Debugging code
        # self.app = QtWidgets.QApplication(sys.argv)
        self.ui = Ui_Form()
        self.form = QtWidgets.QWidget()
        self.record_file_name = None
        self.record = Record()
        self.record_saved = Record()
        self.available_channel_records = []

        self.changes_made = False

        self.fig = None
        self.ax1 = None
        self.ax2 = None
        self.cursor_line = None
        self.cursor_text = None
        self.drag_event = None

        self.cursor_font = {'family': 'monospace',
                            'color':  'black',
                            'weight': 'normal',
                            'size': 10,
                            }

    def run(self, record_file_name):
        self.ui.setupUi(self.form)

        self.record_file_name = record_file_name
        global plot_name
        plot_name = self.record_file_name
        self.form.setWindowTitle(self.record_file_name.replace(".json", ""))
        self.load_data()

        self.update_enabled_widgets()
        self.assign_button_functions()
        self.set_field_limit_values()

        self.form.show()
        # NOTE: Debugging code
        # sys.exit(self.app.exec_())

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
        if self.changes_made:
            self.ui.SaveChangesButton.setEnabled(True)
        self.ui.RecordLengthValue.setValue(self.record.length_ms)
        self.ui.RecordIntervalValue.setValue(self.record.interval_us)

        for i in range(self.record.num_of_channels):
            channel_enable_checkbox_widget = self.form.findChild(QCheckBox, f"ChannelEnabled_{i + 1}")
            channel_enable_checkbox_widget.setEnabled(True)
            channel_enable_checkbox_widget.setChecked(self.record.channels[i].available)

            if not self.available_channel_records[i]:
                channel_enable_checkbox_widget.setEnabled(False)
                channel_label_widget = self.form.findChild(QLabel, f"ChannelLabel_{i + 1}")
                channel_label_widget.setText("Unavailable")
                continue

            self.update_channel_widgets_enable_status(i + 1)

    def change_apply_cancel_buttons_enable_status(self, state):
        self.ui.ApplyButton.setEnabled(state)
        self.ui.CancelButton.setEnabled(state)

    def update_channel_widgets_enable_status(self, channel):
        channel_index = channel - 1

        self.change_apply_cancel_buttons_enable_status(False)

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
        channel_index = channel - 1
        self.record.channels[channel_index].available = not self.record.channels[channel_index].available
        self.update_channel_widgets_enable_status(channel)
        self.change_apply_cancel_buttons_enable_status(True)

    def toggle_data_processing(self, channel):
        channel_index = channel - 1
        self.record.channels[channel_index].data_processing_enabled = not self.record.channels[channel_index].data_processing_enabled
        self.update_channel_widgets_enable_status(channel)
        self.change_apply_cancel_buttons_enable_status(True)

    def toggle_temperature_prediction(self, channel):
        channel_index = channel - 1
        self.record.channels[channel_index].temperature_prediction_enabled = not self.record.channels[channel_index].temperature_prediction_enabled
        self.update_channel_widgets_enable_status(channel)
        self.change_apply_cancel_buttons_enable_status(True)

    def toggle_prediction_processing(self, channel):
        channel_index = channel - 1
        self.record.channels[channel_index].prediction_processing_enabled = not self.record.channels[channel_index].prediction_processing_enabled
        self.update_channel_widgets_enable_status(channel)
        self.change_apply_cancel_buttons_enable_status(True)

    def data_filter_order_changed(self, channel):
        channel_index = channel - 1
        widget = self.form.findChild(QSpinBox, f"DataLowPassOrder_{channel}")
        self.record.channels[channel_index].data_filter_order = widget.value()
        self.change_apply_cancel_buttons_enable_status(True)

    def data_filter_frequency_changed(self, channel):
        channel_index = channel - 1
        widget = self.form.findChild(QDoubleSpinBox, f"DataLowPassCornerFrequency_{channel}")
        self.record.channels[channel_index].data_filter_freq_khz = widget.value()
        self.change_apply_cancel_buttons_enable_status(True)

    def prediction_time_constant_changed(self, channel):
        channel_index = channel - 1
        widget = self.form.findChild(QDoubleSpinBox, f"PredictionTimeConstant_{channel}")
        self.record.channels[channel_index].prediction_time_constant_ms = widget.value()
        self.change_apply_cancel_buttons_enable_status(True)

    def prediction_queue_length_changed(self, channel):
        channel_index = channel - 1
        widget = self.form.findChild(QSpinBox, f"PredictionQueueLength_{channel}")
        self.record.channels[channel_index].prediction_queue_length = widget.value()
        self.change_apply_cancel_buttons_enable_status(True)

    def prediction_filter_order_changed(self, channel):
        channel_index = channel - 1
        widget = self.form.findChild(QSpinBox, f"PostProcessLowPassOrder_{channel}")
        self.record.channels[channel_index].post_process_filter_order = widget.value()
        self.change_apply_cancel_buttons_enable_status(True)

    def prediction_filter_frequency_changed(self, channel):
        channel_index = channel - 1
        widget = self.form.findChild(QDoubleSpinBox, f"PostProcessLowPassCornerFrequency_{channel}")
        self.record.channels[channel_index].post_process_filter_freq_khz = widget.value()
        self.change_apply_cancel_buttons_enable_status(True)

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

        self.ui.DataLowPassOrder_1.valueChanged.connect(lambda: self.data_filter_order_changed(1))
        self.ui.DataLowPassOrder_2.valueChanged.connect(lambda: self.data_filter_order_changed(2))
        self.ui.DataLowPassOrder_3.valueChanged.connect(lambda: self.data_filter_order_changed(3))
        self.ui.DataLowPassOrder_4.valueChanged.connect(lambda: self.data_filter_order_changed(4))
        self.ui.DataLowPassCornerFrequency_1.valueChanged.connect(lambda: self.data_filter_frequency_changed(1))
        self.ui.DataLowPassCornerFrequency_2.valueChanged.connect(lambda: self.data_filter_frequency_changed(2))
        self.ui.DataLowPassCornerFrequency_3.valueChanged.connect(lambda: self.data_filter_frequency_changed(3))
        self.ui.DataLowPassCornerFrequency_4.valueChanged.connect(lambda: self.data_filter_frequency_changed(4))
        self.ui.PredictionTimeConstant_1.valueChanged.connect(lambda: self.prediction_time_constant_changed(1))
        self.ui.PredictionTimeConstant_2.valueChanged.connect(lambda: self.prediction_time_constant_changed(2))
        self.ui.PredictionTimeConstant_3.valueChanged.connect(lambda: self.prediction_time_constant_changed(3))
        self.ui.PredictionTimeConstant_4.valueChanged.connect(lambda: self.prediction_time_constant_changed(4))
        self.ui.PredictionQueueLength_1.valueChanged.connect(lambda: self.prediction_queue_length_changed(1))
        self.ui.PredictionQueueLength_2.valueChanged.connect(lambda: self.prediction_queue_length_changed(2))
        self.ui.PredictionQueueLength_3.valueChanged.connect(lambda: self.prediction_queue_length_changed(3))
        self.ui.PredictionQueueLength_4.valueChanged.connect(lambda: self.prediction_queue_length_changed(4))
        self.ui.PostProcessLowPassOrder_1.valueChanged.connect(lambda: self.prediction_filter_order_changed(1))
        self.ui.PostProcessLowPassOrder_2.valueChanged.connect(lambda: self.prediction_filter_order_changed(2))
        self.ui.PostProcessLowPassOrder_3.valueChanged.connect(lambda: self.prediction_filter_order_changed(3))
        self.ui.PostProcessLowPassOrder_4.valueChanged.connect(lambda: self.prediction_filter_order_changed(4))
        self.ui.PostProcessLowPassCornerFrequency_1.valueChanged.connect(lambda: self.prediction_filter_frequency_changed(1))
        self.ui.PostProcessLowPassCornerFrequency_2.valueChanged.connect(lambda: self.prediction_filter_frequency_changed(2))
        self.ui.PostProcessLowPassCornerFrequency_3.valueChanged.connect(lambda: self.prediction_filter_frequency_changed(3))
        self.ui.PostProcessLowPassCornerFrequency_4.valueChanged.connect(lambda: self.prediction_filter_frequency_changed(4))

        self.ui.ViewPlotButton.clicked.connect(self.plot)
        self.ui.ApplyButton.clicked.connect(self.update_parameters)
        self.ui.CancelButton.clicked.connect(self.restore_saved_parameters)
        self.ui.SaveChangesButton.clicked.connect(self.save_changes)

    def load_data(self):
        with open(Parameters.record_folder_dir + self.record_file_name) as record_file:
            file_raw = record_file.read()
            self.record = jsonpickle.decode(file_raw)

        for i in range(self.record.num_of_channels):
            self.available_channel_records.append(self.record.channels[i].available)
            self.display_saved_parameter_values(i)

        self.record_saved = copy.deepcopy(self.record)

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
        if not self.changes_made:
            self.ui.SaveChangesButton.setEnabled(True)
            self.changes_made = True

        self.record_saved = copy.deepcopy(self.record)
        for i in range(self.record.num_of_channels):
            if self.record.channels[i].available:
                self.display_saved_parameter_values(i)
        self.update_enabled_widgets()

    def restore_saved_parameters(self):
        self.record = copy.deepcopy(self.record_saved)
        for i in range(self.record.num_of_channels):
            if self.record.channels[i].available:
                self.display_saved_parameter_values(i)
        self.update_enabled_widgets()

    def save_changes(self):
        jsonpickle.set_encoder_options('json', indent=4)
        output_json = jsonpickle.encode(self.record)

        with open(str(Parameters.record_folder_dir + self.record_file_name), "w") as output_file:
            output_file.writelines(output_json)

        self.load_data()
        self.changes_made = False
        self.ui.SaveChangesButton.setEnabled(False)

    def plot(self):
        self.restore_saved_parameters()
        global plot_data
        plot_data = {}

        impedance_values = None
        y_data_values = None
        y_prediction_values = None

        enabled_channels = list(x.available for x in self.record.channels).count(True)
        if not enabled_channels:
            messagebox = QMessageBox(QMessageBox.Critical,
                                     "Measurement error",
                                     "Please enable at least one channel",
                                     QMessageBox.Ok)
            messagebox.exec()
            self.form.setEnabled(True)
            return

        self.fig, self.ax1 = plt.subplots()
        self.ax2 = self.ax1.twinx()

        x_values = np.linspace(0, self.record.length_ms, int(self.record.length_ms/(self.record.interval_us/1000)))
        x_values = np.round(x_values, math.ceil(math.log10(1000 / self.record.interval_us)))
        plot_data["Time[ms]"] = x_values

        # Plotting impedance
        try:
            impedance_values = self.record.generator_raw_data["Z"]
        except AttributeError:
            impedance_values = self.record.impedance_raw_data
        except KeyError:
            impedance_values = None

        if impedance_values is not None:
            x_values_imp = list(range(self.record.generator_log_start_time_ms,
                                      self.record.generator_log_start_time_ms + len(impedance_values),
                                      self.record.generator_log_interval_ms))
            plt.axvspan(self.record.generator_log_start_time_ms,
                        self.record.generator_log_start_time_ms + len(impedance_values) - 1,
                        facecolor='0.2',
                        alpha=0.15)

            plot_data["Z[Ω]"] = impedance_values
            self.ax2.plot(x_values_imp, impedance_values, color="Black", label="Impedance")

            self.ax2.set_xlabel("Time [ms]")
            self.ax2.set_ylabel("Impedance [Ω]")
            impedance_axis_max = math.ceil(max(impedance_values)/1000.0) * 1000
            self.ax2.set_ylim([0, impedance_axis_max])
            ticker = matplotlib.ticker.EngFormatter(unit='', sep="")
            self.ax2.yaxis.set_major_formatter(ticker)

        # Plotting temperature
        channel_colors = ["red", "blue", "green", "orange"]

        y_max = None
        for i in range(self.record.num_of_channels):
            if not self.record.channels[i].available:
                continue

            # Data plot
            if not self.record.channels[i].data_processing_enabled:
                y_data_values = self.record.channels[i].raw_data
                data_label = f"Channel {i + 1} data (No filter)"
            else:
                data = self.record.channels[i].raw_data
                filter_order = self.record.channels[i].data_filter_order
                filter_corner_freq_khz = self.record.channels[i].data_filter_freq_khz
                y_data_values = self.apply_low_pass_filter(data, filter_order, filter_corner_freq_khz)
                data_label = f"Channel {i + 1} data ({filter_corner_freq_khz} kHz, order {filter_order} filter)"

            if y_max is None or max(y_data_values) > y_max:
                y_max = max(y_data_values)

            plot_data["Treal[°C]"] = y_data_values
            self.ax1.plot(x_values, y_data_values, color=channel_colors[i], label=data_label)

            # Prediction plot
            if not self.record.channels[i].temperature_prediction_enabled:
                continue

            prediction_values = PlotLogic.calculate_predicted_data(x_values, y_data_values, self.record.channels[i])

            if not self.record.channels[i].prediction_processing_enabled:
                y_prediction_values = prediction_values
                prediction_label = f"Channel {i + 1} prediction (No filter)"
            else:
                filter_order = self.record.channels[i].post_process_filter_order
                filter_corner_freq_khz = self.record.channels[i].post_process_filter_freq_khz
                y_prediction_values = self.apply_low_pass_filter(prediction_values, filter_order, filter_corner_freq_khz)
                prediction_label = f"Channel {i + 1} prediction ({filter_corner_freq_khz} kHz, order {filter_order} filter)"

            if max(y_prediction_values) > y_max:
                y_max = max(y_prediction_values)

            x_values_prediction = x_values[:len(x_values) - self.record.channels[i].prediction_queue_length]
            plot_data["Tpred[°C]"] = y_prediction_values
            self.ax1.plot(x_values_prediction, y_prediction_values, color=channel_colors[i], linestyle="dashed", label=prediction_label)

        plt.title(self.record_file_name.replace(".json", ""), pad=15)
        self.ax1.set_xlabel("Time [ms]")
        self.ax1.set_ylabel("Temperature [°C]")
        plt.figlegend()
        self.ax1.grid()

        # Save to Excel button
        tm = self.fig.canvas.manager.toolmanager
        tm.add_tool("Save to Excel", SaveToExcelButton)
        self.fig.canvas.manager.toolbar.add_tool(tm.get_tool("Save to Excel"), "toolgroup")

        plt.tight_layout()
        plt.show()

        # Cursors
        self.fig.canvas.draw()
        self.fig.my_bg = self.fig.canvas.copy_from_bbox(self.fig.bbox)

        self.cursor_line = plt.axvline(0, color='blue', ls='--', lw=1)
        self.cursor_text = plt.text(0, 0, "", fontdict=self.cursor_font)
        self.cursor_text.set_bbox(dict(facecolor="yellow", alpha=1))

        y_axis_names_values = {"     Z[Ω]": impedance_values,
                               "Treal[°C]": y_data_values,
                               "Tpred[°C]": y_prediction_values}
        self.fig.canvas.mpl_connect("button_press_event", lambda event: self.drag_cursor(event, y_axis_names_values))
        self.fig.canvas.mpl_connect("button_release_event", self.release_cursor)
        self.fig.canvas.mpl_connect("resize_event", self.window_resize)
        self.ax2.callbacks.connect("ylim_changed", self.window_resize)

    def drag_cursor(self, event, y_axis_names_values):
        if event.button == 1:
            self.hide_cursor()
            return
        self.drag_event = self.fig.canvas.mpl_connect("motion_notify_event", lambda evt: self.show_cursor(evt, y_axis_names_values))
        return

    def release_cursor(self, event):
        self.fig.canvas.mpl_disconnect(self.drag_event)
        return

    def show_cursor(self, event, y_axis_names_values):
        time_value = event.xdata

        if time_value is None:
            return

        round_base = self.record.interval_us / 1000.0
        round_precision = math.ceil(math.log10(1000 / self.record.interval_us))

        time_value_rounded = round(round_base * round(time_value / round_base), round_precision)

        # time_value_rounded = round(time_value, math.ceil(math.log10(1000 / self.record.interval_us)))

        temperature_index = round(time_value / (self.record.interval_us / 1000.0))
        impedance_index = round(time_value / self.record.generator_log_interval_ms - self.record.generator_log_start_time_ms)

        self.cursor_line.set_xdata(time_value_rounded)

        annotation_text = f" Time[ms]: {time_value_rounded:.2f}\n"
        for name, values in y_axis_names_values.items():
            if "Ω" in name:
                if values is not None and len(values) > impedance_index > 0:
                    annotation_text += f"{name}: {values[impedance_index]}\n"
            else:
                if values is not None and len(values) > temperature_index > 0:
                    annotation_text += f"{name}: {values[temperature_index]:.2f}\n"

        annotation_text = annotation_text.strip("\n")
        self.cursor_text.set_position((event.xdata + (self.ax1.get_xlim()[1] - self.ax1.get_xlim()[0])*0.035, event.ydata))
        self.cursor_text.set_text(annotation_text)

        self.fig.canvas.restore_region(self.fig.my_bg)
        self.fig.draw_artist(self.cursor_line)
        self.fig.draw_artist(self.cursor_text)
        self.fig.canvas.blit()
        # print(annotation_text)

    def hide_cursor(self):
        self.fig.canvas.restore_region(self.fig.my_bg)
        self.fig.canvas.blit()

    def window_resize(self, event):
        cursor_line_x = self.cursor_line.get_xdata()[0]
        cursor_text_coords = self.cursor_text.get_position()
        cursor_text = self.cursor_text.get_text()
        self.cursor_line.remove()
        self.cursor_text.remove()
        self.fig.canvas.draw()
        self.fig.my_bg = self.fig.canvas.copy_from_bbox(self.fig.bbox)

        self.cursor_line = plt.axvline(cursor_line_x, color='blue', ls=':', lw=2)
        self.cursor_text = plt.text(cursor_text_coords[0], cursor_text_coords[1], cursor_text, fontdict=self.cursor_font)
        self.cursor_text.set_bbox(dict(facecolor="yellow", alpha=1))
        self.fig.canvas.restore_region(self.fig.my_bg)
        self.fig.draw_artist(self.cursor_line)
        self.fig.draw_artist(self.cursor_text)
        self.fig.canvas.blit()
        return

    def apply_low_pass_filter(self, data, order, corner_frequency_khz):
        cutoff_freq_khz = (1 / self.record.interval_us) * 1000
        nyquist_freq_khz = cutoff_freq_khz / 2
        b, a = signal.butter(N=order, Wn=corner_frequency_khz / nyquist_freq_khz)
        data_filtered = signal.filtfilt(b, a, data)
        return data_filtered.tolist()

    def apply_rejection_filter(self, data, stop_freq, qual_factor):
        sample_freq = (1 / self.record.interval_us) * 1000
        b, a = signal.iirnotch(stop_freq, qual_factor, sample_freq)
        data_filtered = signal.filtfilt(b, a, data)
        return data_filtered.tolist()

    def set_field_limit_values(self):
        max_filter_frequency_khz = (1.0 / (self.record.interval_us / 10**3)) / 2 - 0.001
        filter_field_names = QRegularExpression(r".*Frequency.*")
        filter_field_widgets = self.form.findChildren(QDoubleSpinBox, filter_field_names)
        for widget in filter_field_widgets:
            widget.setMaximum(max_filter_frequency_khz)

    @staticmethod
    def heating_function(x, t_env, tau_ms, t_0):
        return t_env + ((t_0 - t_env) * np.exp(-(1 / (tau_ms / 1000)) * x))

    @staticmethod
    def calculate_predicted_data(x_data, y_data, channel_parameters):
        x_short_ms = x_data[:channel_parameters.prediction_queue_length]
        x_short = list((x*10**(-3)) for x in x_short_ms)
        y_short = y_data[:channel_parameters.prediction_queue_length]

        y_sets = []
        for data_point in y_data[channel_parameters.prediction_queue_length:]:
            y_sets.append(copy.copy(y_short))

            y_short.pop(0)
            y_short.append(data_point)

        pool = Pool(processes=multiprocessing.cpu_count())
        predictions = pool.map(partial(PlotLogic.calculate_predicted_data_point, x_short, channel_parameters),
                               y_sets)

        return predictions

    @staticmethod
    def calculate_predicted_data_point(x_data, channel_parameters, y_data):
        t_0 = y_data[0]
        heating_function_fixed_params = partial(PlotLogic.heating_function,
                                                tau_ms=channel_parameters.prediction_time_constant_ms,
                                                t_0=t_0)
        param, param_cov = curve_fit(heating_function_fixed_params, x_data, y_data)
        return param[0]

    # NOTE: Slower method, but works with debugging
    # @staticmethod
    # def calculate_predicted_data(x_data, y_data, channel_parameters):
    #     x_short_ms = x_data[:channel_parameters.prediction_queue_length]
    #     x_short = list((x*10**(-3)) for x in x_short_ms)
    #
    #     y_short = y_data[:channel_parameters.prediction_queue_length]
    #     predictions = []
    #
    #     for data_point in y_data[channel_parameters.prediction_queue_length:]:
    #         t_0 = y_short[0]
    #         heating_function_fixed_params = partial(PlotLogic.heating_function,
    #                                                 tau_ms=channel_parameters.prediction_time_constant_ms,
    #                                                 t_0=t_0)
    #
    #         param, param_cov = curve_fit(heating_function_fixed_params, x_short, y_short)
    #         predictions.append(param[0])
    #
    #         y_short.pop(0)
    #         y_short.append(data_point)
    #
    #     return predictions


class SaveToExcelButton(ToolBase):
    def trigger(self, *args, **kwargs):
        global plot_data, plot_name

        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(parent=None,
                                                             caption="Save File",
                                                             directory=plot_name.replace(".json", ".xlsx"),
                                                             filter="Excel files(*.xlsx *.xls *.xlsm *.xlt);;"
                                                                    "CSV files(*.csv)",
                                                             options=options)

        if not file_name:
            return
        df = DataFrame.from_dict(plot_data, orient="index")
        df = df.transpose()
        if "Z[Ω]" in df:
            impedance_column = df.pop("Z[Ω]")
            impedance_time_column = list(range(Parameters.generator_log_start_time_ms,
                                               Parameters.generator_log_start_time_ms + len(plot_data["Z[Ω]"]),
                                               Parameters.generator_log_interval_ms))
            df[""] = np.nan
            df["Generator time[ms]"] = Series(impedance_time_column)
            df["Z[Ω]"] = impedance_column

        if "csv" in file_name:
            df.to_csv(file_name, sep=",", encoding="utf-8 sig", index=False)
        else:
            df.to_excel(file_name, index=False)

# NOTE: Debugging code
# if __name__ == "__main__":
#     plot_window = PlotLogic()
#     plot_window.run("hot_cold_hot_sample_10us.json")