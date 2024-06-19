import json
import os
import time
from datetime import datetime

import jsonpickle as jsonpickle
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QRegularExpression, Qt, QSize, QEventLoop, QTimer, pyqtSignal, QObject
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import *

from PC.Record import Record
from PC.SharedParameters import SharedParameters
from PlotLogic import PlotLogic

from MainWindowUI import Ui_Form
from PyQt5 import QtWidgets, QtTest
import sys


class MainWindowLogic:
    def __init__(self):
        self.ui = Ui_Form()
        self.app = QtWidgets.QApplication(sys.argv)
        self.form = QtWidgets.QWidget()
        self.record = Record(number_of_channels=4)
        self.serial = None
        self.connection_established = False

        self.record_length_ms_min_max = {
            "min": 1,
            "max": 2000
        }
        self.record_interval_us_min_max = {
            "min": 10,
            "max": 1000
        }

    def run(self):
        self.ui.setupUi(self.form)
        self.ui.RecordLengthValue.setValue(self.record.length_ms)
        self.ui.RecordIntervalValue.setValue(self.record.interval_us)

        self.update_enabled_widgets()
        self.assign_button_functions()
        self.display_available_records()

        self.form.show()

        sys.exit(self.app.exec_())

    def update_enabled_widgets(self):
        if not self.connection_established:
            self.update_connection_widgets_enable_status(False)
        else:
            self.update_connection_widgets_enable_status(True)

    def update_connection_widgets_enable_status(self, status):
        self.ui.MeasureButton.setEnabled(status)

        meas_settings_widgets = []
        for widget_index in range(self.ui.MeasSettingsLayout.count()):
            widget = self.ui.MeasSettingsLayout.itemAt(widget_index).widget()
            meas_settings_widgets.append(widget)
            if widget is not None:
                widget.setEnabled(status)

        for widget_index in range(self.ui.ChannelParametersLayout.count()):
            widget = self.ui.ChannelParametersLayout.itemAt(widget_index).widget()
            if widget is None:
                continue
            elif isinstance(widget, QLabel):
                widget.setEnabled(True)
            else:
                widget.setEnabled(False)

        # Enable channels
        if status:
            channel_enable_checkbox_names = QRegularExpression("ChannelEnabled_\d")
            channel_enable_checkbox_widgets = self.form.findChildren(QCheckBox, channel_enable_checkbox_names)
            for widget in channel_enable_checkbox_widgets:
                widget.setEnabled(True)

            for i in range(4):
                self.update_channel_widgets_enable_status(i + 1)

    def update_channel_widgets_enable_status(self, channel):
        channel_index = channel - 1

        # Channel enabled
        tc_type_selector_name = f"ChannelTcType_{channel}"
        tc_type_selector_widget = self.form.findChild(QComboBox, tc_type_selector_name)
        checkbox_object_names = QRegularExpression(fr"[^ChannelEnabled].*_{channel}")
        checkbox_object_widgets = self.form.findChildren(QCheckBox, checkbox_object_names)
        # Enable/Disable relevant objects
        tc_type_selector_widget.setEnabled(self.record.channels[channel_index].available)
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
        temperature_prediction_widgets = self.form.findChildren((QSpinBox, QDoubleSpinBox), temperature_prediction_names)
        # Enable/Disable relevant objects
        for widget in temperature_prediction_widgets:
            widget.setEnabled(self.record.channels[channel_index].temperature_prediction_enabled and self.record.channels[channel_index].available)

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

    def toggle_data_processing(self, channel):
        channel_index = channel - 1
        self.record.channels[channel_index].data_processing_enabled = not self.record.channels[channel_index].data_processing_enabled
        self.update_channel_widgets_enable_status(channel)

    def toggle_temperature_prediction(self, channel):
        channel_index = channel - 1
        self.record.channels[channel_index].temperature_prediction_enabled = not self.record.channels[channel_index].temperature_prediction_enabled
        self.update_channel_widgets_enable_status(channel)

    def toggle_prediction_processing(self, channel):
        channel_index = channel - 1
        self.record.channels[channel_index].prediction_processing_enabled = not self.record.channels[channel_index].prediction_processing_enabled
        self.update_channel_widgets_enable_status(channel)

    def record_length_changed(self):
        self.record.length_ms = self.ui.RecordLengthValue.value()
        self.set_field_limit_values()

    def set_record_length(self, value):
        self.record.length_ms = value
        self.ui.RecordLengthValue.setValue(self.record.length_ms)
        self.set_field_limit_values()

    def record_interval_changed(self):
        self.record.interval_us = self.ui.RecordIntervalValue.value()
        self.set_field_limit_values()

    def set_record_interval(self, value):
        self.record.interval_us = value
        self.ui.RecordIntervalValue.setValue(self.record.interval_us)
        self.set_field_limit_values()

    def channel_tc_type_changed(self, channel):
        channel_index = channel - 1
        widget = self.form.findChild(QComboBox, f"ChannelTcType_{channel}")
        self.record.channels[channel_index].tc_type = widget.currentText()

    def data_filter_order_changed(self, channel):
        channel_index = channel - 1
        widget = self.form.findChild(QSpinBox, f"DataLowPassOrder_{channel}")
        self.record.channels[channel_index].data_filter_order = widget.value()

    def data_filter_frequency_changed(self, channel):
        channel_index = channel - 1
        widget = self.form.findChild(QDoubleSpinBox, f"DataLowPassCornerFrequency_{channel}")
        self.record.channels[channel_index].data_filter_freq_khz = widget.value()

    def prediction_time_constant_changed(self, channel):
        channel_index = channel - 1
        widget = self.form.findChild(QDoubleSpinBox, f"PredictionTimeConstant_{channel}")
        self.record.channels[channel_index].prediction_time_constant_ms = widget.value()

    def prediction_queue_length_changed(self, channel):
        channel_index = channel - 1
        widget = self.form.findChild(QSpinBox, f"PredictionQueueLength_{channel}")
        self.record.channels[channel_index].prediction_queue_length = widget.value()

    def prediction_filter_order_changed(self, channel):
        channel_index = channel - 1
        widget = self.form.findChild(QSpinBox, f"PostProcessLowPassOrder_{channel}")
        self.record.channels[channel_index].post_process_filter_order = widget.value()

    def prediction_filter_frequency_changed(self, channel):
        channel_index = channel - 1
        widget = self.form.findChild(QDoubleSpinBox, f"PostProcessLowPassCornerFrequency_{channel}")
        self.record.channels[channel_index].post_process_filter_freq_khz = widget.value()


    def assign_button_functions(self):
        self.ui.ConnectionButton.clicked.connect(self.vcp_connection_change)
        self.ui.MeasureButton.clicked.connect(self.measure)

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
        self.ui.RecordLengthMinButton.clicked.connect(lambda: self.set_record_length(self.record_length_ms_min_max["min"]))
        self.ui.RecordLengthMaxButton.clicked.connect(lambda: self.set_record_length(self.record_length_ms_min_max["max"]))
        self.ui.RecordIntervalMinButton.clicked.connect(lambda: self.set_record_interval(self.record_interval_us_min_max["min"]))
        self.ui.RecordIntervalMaxButton.clicked.connect(lambda: self.set_record_interval(self.record_interval_us_min_max["max"]))

        self.ui.ChannelTcType_1.currentTextChanged.connect(lambda: self.channel_tc_type_changed(1))
        self.ui.ChannelTcType_2.currentTextChanged.connect(lambda: self.channel_tc_type_changed(2))
        self.ui.ChannelTcType_3.currentTextChanged.connect(lambda: self.channel_tc_type_changed(3))
        self.ui.ChannelTcType_4.currentTextChanged.connect(lambda: self.channel_tc_type_changed(4))
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

        self.ui.RecordLengthValue.editingFinished.connect(self.record_length_changed)
        self.ui.RecordIntervalValue.editingFinished.connect(self.record_interval_changed)

        self.ui.ViewRecordButton.clicked.connect(self.view_selected_record)
        self.ui.RenameRecordButton.clicked.connect(self.rename_selected_record)
        self.ui.DeleteRecordButton.clicked.connect(self.delete_selected_record)

    def vcp_connection_change(self):
        if self.connection_established:
            self.vcp_disconnect()
            self.connection_established = False
            self.ui.ConnectionButton.setText("Connect")
        else:
            self.connection_established = self.vcp_connect()
            if not self.connection_established:
                messagebox = QMessageBox(QMessageBox.Critical,
                                         "Connection error",
                                         "No connected logger found!",
                                         QMessageBox.Ok)
                messagebox.exec()
            else:
                self.ui.ConnectionButton.setText("Disconnect")

            # self.vcp_connect()
        self.update_enabled_widgets()

    def vcp_connect(self):
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            hwid_split = hwid.split(" ")
            if hwid_split[0] != "USB":
                continue
            vid_pid = hwid_split[1]
            vid_pid_split = vid_pid.replace("=", ":").split(":")
            vid = int(vid_pid_split[2], 16)
            pid = int(vid_pid_split[3], 16)

            if vid == SharedParameters.device_vid and pid == SharedParameters.device_pid:
                print(f"Connecting to port {port}...")
                self.serial = serial.Serial(port=port, baudrate=9600, timeout=None)
                return True

        return False

    def vcp_disconnect(self):
        self.serial.close()
        return

    def measure(self):
        self.form.setEnabled(False)

        enabled_channels = list(x.available for x in self.record.channels).count(True)
        if not enabled_channels:
            messagebox = QMessageBox(QMessageBox.Critical,
                                     "Measurement error",
                                     "Please enable at least one channel",
                                     QMessageBox.Ok)
            messagebox.exec()
            self.form.setEnabled(True)

            return

        number_of_steps = 3
        progress_dialog = QProgressDialog("Preparing...", "Cancel", 0, number_of_steps + 1, self.form)
        progress_dialog.overrideWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setWindowTitle("Measuring")
        progress_dialog.setCancelButton(None)
        progress_dialog.setAttribute(Qt.WA_DeleteOnClose)
        progress_dialog.show()

        progress_dialog.setValue(1)
        progress_dialog.setLabelText("Sending setup to MCU...")
        self.measurement_send_setup()
        progress_dialog.setLabelText("Receiving data from MCU...")
        progress_dialog.setValue(2)
        self.measurement_receive_data()
        progress_dialog.setLabelText("Saving record...")
        progress_dialog.setValue(3)
        # TODO: remove this comment
        # self.measurement_save_record()
        progress_dialog.setLabelText("Done")
        progress_dialog.setValue(4)

        self.form.setEnabled(True)

        return

    def measurement_send_setup(self):
        # Send UI settings to MCU
        setup_string = ""
        setup_string += f"RecLen:{str(self.record.length_ms)};"
        setup_string += f"RecInt:{str(self.record.interval_us)};"

        tc_sensitivity_ranking = ["E", "J", "K", "T"]
        highest_sensitivity_tc_available = "T"
        for channel in self.record.channels:
            if not channel.available:
                continue
            if tc_sensitivity_ranking.index(channel.tc_type) < tc_sensitivity_ranking.index(highest_sensitivity_tc_available):
                highest_sensitivity_tc_available = channel.tc_type
        setup_string += f"TcType:{highest_sensitivity_tc_available};"

        trigger_source_full = self.ui.TriggerSourceValue.currentText()
        if "button" in trigger_source_full:
            trigger_source_short = "btn"
        elif "trigger 1" in trigger_source_full:
            trigger_source_short = "ex1"
        else:
            trigger_source_short = "ex2"
        setup_string += f"TrgSrc:{trigger_source_short};"

        setup_string += "\0"
        self.serial.write(setup_string.encode())
        print(setup_string)

        return

    def measurement_receive_data(self):
        # Receive data from MCU

        return

    def measurement_save_record(self):
        # Save received data
        time_now_formatted = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        record_file_name = time_now_formatted + ".json"

        jsonpickle.set_encoder_options('json', indent=4)
        output_json = jsonpickle.encode(self.record)

        with open(str(SharedParameters.record_folder_dir + record_file_name), "w") as output_file:
            output_file.writelines(output_json)

        self.display_available_records()

    def display_available_records(self):
        self.ui.RecordsList.clear()
        self.ui.RecordsList.setItemAlignment(Qt.AlignRight)
        record_list = os.listdir(SharedParameters.record_folder_dir)
        for record in record_list:
            item = QListWidgetItem(record.replace(".json", ""))
            item.setTextAlignment(Qt.AlignRight)
            self.ui.RecordsList.addItem(item)

    def view_selected_record(self):
        selected_record = self.ui.RecordsList.currentItem()
        if not selected_record:
            return
        
        selected_record_file_name = selected_record.text() + ".json"
        plot_window = PlotLogic()
        plot_window.run(selected_record_file_name)

    def rename_selected_record(self):
        selected_record = self.ui.RecordsList.currentItem()
        if not selected_record:
            return

        current_name = selected_record.text()
        new_name, ok = QtWidgets.QInputDialog.getText(self.ui.RecordsList,
                                                      "Rename record",
                                                      "New record name:",
                                                      QLineEdit.Normal,
                                                      current_name)
        if not (ok and new_name):
            return

        os.rename(str(SharedParameters.record_folder_dir + current_name + ".json"), str(SharedParameters.record_folder_dir + new_name + ".json"))
        self.display_available_records()

    def delete_selected_record(self):
        selected_record = self.ui.RecordsList.currentItem()
        if not selected_record:
            return

        selected_record_name = selected_record.text()

        messagebox = QMessageBox(QMessageBox.Question,
                                 "Confirm delete",
                                 "Are you sure?",
                                 QMessageBox.Yes | QMessageBox.No)
        response = messagebox.exec()

        if response == QMessageBox.No:
            return

        os.remove(str(SharedParameters.record_folder_dir + selected_record_name + ".json"))
        self.display_available_records()

    def set_field_limit_values(self):
        max_filter_frequency_khz = (1.0 / (self.record.interval_us / 10**3)) / 2 - 0.001
        filter_field_names = QRegularExpression(r".*Frequency.*")
        filter_field_widgets = self.form.findChildren(QDoubleSpinBox, filter_field_names)
        for widget in filter_field_widgets:
            widget.setMaximum(max_filter_frequency_khz)


if __name__ == "__main__":
    main_window = MainWindowLogic()
    main_window.run()
    
