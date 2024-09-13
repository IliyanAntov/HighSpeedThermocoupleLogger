import math
import os
import threading
from datetime import datetime

import jsonpickle as jsonpickle
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QRegularExpression, Qt, QSize
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication
from send2trash import send2trash
from serial import SerialTimeoutException, SerialException

from MainWindowUI import Ui_Form
from MeasurementData.LogData import Record
import MeasurementData.Parameters as Parameters
from PlotWindowLogic import PlotLogic

from PyQt5 import QtWidgets, QtGui
import sys


class MainWindowLogic:

    def __init__(self):
        self.ui = Ui_Form()
        self.app = QtWidgets.QApplication(sys.argv)
        self.app.setWindowIcon(QtGui.QIcon("UI/icon.png"))
        self.app.aboutToQuit.connect(self.stop_serial_ports)
        self.form = QtWidgets.QWidget()
        self.current_folder = Parameters.record_folder_dir
        self.record = Record(number_of_channels=4)
        self.serial = None
        self.serial_gen = None
        self.connection_established = False
        self.connection_established_gen = False

        self.log_parameter_names = None
        self.log_data = None

        self.read_thread_gen = None
        self.read_thread_active = False

        self.waiting_for_trigger = False
        self.receiving_temp_data = False
        self.save_generator_log = False
        self.gen_log_received = False

    def run(self):
        self.ui.setupUi(self.form)
        self.form.setWindowTitle("High Speed Thermocouple Logger")

        self.ui.CurrentDirectoryLine.setText(self.current_folder)
        self.ui.DirectoryUpButton.setIcon(QIcon("UI/folder_up.png"))
        self.ui.NewDirectoryButton.setIcon(QIcon("UI/new_folder.png"))
        self.ui.RecordLengthValue.setValue(self.record.length_ms)
        self.ui.RecordIntervalValue.setValue(self.record.interval_us)

        # Generator UI
        self.set_available_comports_gen()
        self.update_enabled_widgets_gen()
        self.assign_button_functions_gen()

        self.form.show()

        # Logger UI
        self.update_enabled_widgets()
        self.assign_button_functions()
        self.refresh_record_explorer()

        sys.exit(self.app.exec_())

    def update_enabled_widgets(self):
        self.measurement_ui_enabled(False)

        if not self.connection_established:
            self.update_connection_widgets_enable_status(False)
        else:
            self.update_connection_widgets_enable_status(True)

    def set_available_comports_gen(self):
        self.ui.GeneratorComPort.clear()

        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            self.ui.GeneratorComPort.addItem(port)

        return

    def update_enabled_widgets_gen(self):
        if not self.connection_established_gen:
            self.update_connection_widgets_enable_status_gen(False)
        else:
            self.update_connection_widgets_enable_status_gen(True)

    def update_connection_widgets_enable_status(self, status):
        self.ui.MeasureButton.setEnabled(status)
        self.ui.BurstMeasureButton.setEnabled(status)

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
            channel_enable_checkbox_names = QRegularExpression(r"ChannelEnabled_\d")
            channel_enable_checkbox_widgets = self.form.findChildren(QCheckBox, channel_enable_checkbox_names)
            for widget in channel_enable_checkbox_widgets:
                widget.setEnabled(True)

            for i in range(4):
                self.update_channel_widgets_enable_status(i + 1)

    def update_connection_widgets_enable_status_gen(self, status):
        self.ui.GeneratorCommand.setEnabled(status)
        self.ui.GeneratorSendCommandButton.setEnabled(status)
        self.ui.GeneratorOutputList.setEnabled(status)
        self.ui.GeneratorOutputClearButton.setEnabled(status)

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
        self.ui.BurstMeasureButton.clicked.connect(self.burst_measure)

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
        self.ui.RecordLengthMinButton.clicked.connect(lambda: self.set_record_length(Parameters.record_length_ms_min_max["min"]))
        self.ui.RecordLengthMaxButton.clicked.connect(lambda: self.set_record_length(Parameters.record_length_ms_min_max["max"]))
        self.ui.RecordIntervalMinButton.clicked.connect(lambda: self.set_record_interval(Parameters.record_interval_us_min_max["min"]))
        self.ui.RecordIntervalMaxButton.clicked.connect(lambda: self.set_record_interval(Parameters.record_interval_us_min_max["max"]))

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

        self.ui.RecordsList.itemDoubleClicked.connect(self.view_selected_record)
        self.ui.DirectoryUpButton.clicked.connect(self.directory_up)
        self.ui.NewDirectoryButton.clicked.connect(self.new_directory)

        self.ui.ViewRecordButton.clicked.connect(self.view_selected_record)
        self.ui.RenameRecordButton.clicked.connect(self.rename_selected_record)
        self.ui.DeleteRecordButton.clicked.connect(self.delete_selected_record)

    def assign_button_functions_gen(self):
        self.ui.GeneratorCommand.setText("therapy start 25 65 25000 0 1000")
        self.ui.GeneratorConnectionButton.clicked.connect(self.connection_change_gen)
        self.ui.GeneratorSendCommandButton.clicked.connect(self.send_command_gen)
        self.ui.GeneratorOutputClearButton.clicked.connect(self.clear_output_gen)
        self.ui.GeneratorComPortRefreshButton.clicked.connect(self.set_available_comports_gen)
        self.ui.GeneratorOutputList.model().rowsInserted.connect(lambda: self.ui.GeneratorOutputList.scrollToBottom())
        self.ui.GeneratorOutputList.setWordWrap(True)
        self.ui.GeneratorSendCommandButton.setShortcut("S")
        # for sequence in ("Enter", "Return",):
        #     shortcut = QtWidgets.QShortcut(sequence, self.ui.GeneratorSendCommandButton)
        #     shortcut.activated.connect(self.ui.GeneratorSendCommandButton.click)
        self.ui.MeasureButton.setShortcut("M")
        self.ui.DeleteRecordButton.setShortcut("D")
        self.ui.RenameRecordButton.setShortcut("R")
        self.ui.ViewRecordButton.setShortcut("V")
        self.ui.ChannelEnabled_1.setShortcut("Ctrl+1")
        self.ui.ChannelEnabled_2.setShortcut("Ctrl+2")
        self.ui.ChannelEnabled_3.setShortcut("Ctrl+3")
        self.ui.ChannelEnabled_4.setShortcut("Ctrl+4")
        self.ui.RenameRecordButton.setShortcut("F2")
        self.ui.DeleteRecordButton.setShortcut("Delete")

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

            if vid == Parameters.device_vid and pid == Parameters.device_pid:
                print(f"Connecting to port {port}...")
                self.serial = serial.Serial(port=port, baudrate=9600, timeout=None)
                return True

        return False

    def vcp_disconnect(self):
        self.serial.close()
        return

    def connection_change_gen(self):
        if self.connection_established_gen:
            self.disconnect_gen()
            self.connection_established_gen = False
            self.ui.GeneratorConnectionButton.setText("Connect")
            self.set_available_comports_gen()
        else:
            self.connection_established_gen = self.connect_gen()
            if not self.connection_established_gen:
                messagebox = QMessageBox(QMessageBox.Critical,
                                         "Connection error",
                                         "Connection to generator unsuccessful!",
                                         QMessageBox.Ok)
                messagebox.exec()
            else:
                self.ui.GeneratorConnectionButton.setText("Disconnect")

        self.update_enabled_widgets_gen()

    def connect_gen(self):
        selected_port = self.ui.GeneratorComPort.currentText()

        try:
            self.serial_gen = serial.Serial(port=selected_port,
                                            baudrate=115200,
                                            bytesize=8,
                                            parity="N",
                                            stopbits=1,
                                            write_timeout=0.1,
                                            timeout=0.1)
        except SerialException:
            return False

        try:
            self.serial_gen.write(b"ConnCheck")
        except SerialTimeoutException:
            self.serial_gen.close()
            return False

        try:
            received_data = self.serial_gen.read_until(b"generator>")
            if len(received_data) == 0:
                self.serial_gen.close()
                return False
        except SerialTimeoutException:
            self.serial_gen.close()
            return False

        self.serial_gen.timeout = 10

        self.read_thread_gen = threading.Thread(target=self.read_data_gen)
        self.read_thread_active = True
        self.read_thread_gen.start()

        self.ui.GeneratorComPort.setEnabled(False)
        self.ui.GeneratorComPortRefreshButton.setEnabled(False)
        return True

    def read_data_gen(self):
        while self.read_thread_active:
            try:
                if self.serial_gen.inWaiting():
                    data_line = self.serial_gen.read_until(b"\r").decode().strip()
                    if data_line == Parameters.therapy_parameters_first_line and self.save_generator_log:
                        log = self.serial_gen.read_until(Parameters.therapy_parameters_last_line.encode()).decode()
                        log_split = log.split("\r")
                        self.log_parameter_names = log_split[0]
                        self.log_data = log_split[1:-1]
                        self.gen_log_received = True
                        continue

                    item = QListWidgetItem(data_line)
                    if data_line == self.ui.GeneratorCommand.text():
                        item.setBackground(QColor("#b9c9fa"))
                    elif data_line == "generator>":
                        # item = QListWidgetItem("END")
                        item.setBackground(QColor("#dbdbdb"))

                    if data_line != "":
                        self.ui.GeneratorOutputList.addItem(item)
            except SerialException:
                self.connection_change_gen()

    def disconnect_gen(self):
        self.read_thread_active = False
        self.serial_gen.close()

        self.ui.GeneratorComPort.setEnabled(True)
        self.ui.GeneratorComPortRefreshButton.setEnabled(True)
        return

    def send_command_gen(self):
        command = self.ui.GeneratorCommand.text()
        self.serial_gen.write(command.encode())

        if "therapy start" in command and self.waiting_for_trigger:
            self.save_generator_log = True
            self.gen_log_received = False
            self.record.generator_command = command

        return

    def clear_output_gen(self):
        self.ui.GeneratorOutputList.clear()
        return

    def measurement_ui_enabled(self, status):
        if status:
            self.ui.ConnectMeasureButtonsFrame.hide()
            self.ui.MeasurementProgressBar.show()
            self.ui.MeasurementProgressText.show()
        else:
            self.ui.ConnectMeasureButtonsFrame.show()
            self.ui.MeasurementProgressBar.hide()
            self.ui.MeasurementProgressText.hide()

    def measure(self, left_of_burst=0):
        self.check_channels_enabled()

        number_of_steps = 8
        left_of_burst_str = (' (' + str(left_of_burst) + ' measurement(s) left)') if left_of_burst > 0 else ''
        self.ui.MeasurementProgressText.setText(f"Preparing...{left_of_burst_str}")
        self.ui.MeasurementProgressBar.setRange(1, number_of_steps)

        self.measurement_ui_enabled(True)

        self.ui.MeasurementProgressText.setText(f"Measuring{left_of_burst_str}")
        self.ui.MeasurementProgressBar.setValue(1)
        self.ui.MeasurementProgressText.setText(f"Sending setup to MCU...{left_of_burst_str}")
        self.measurement_send_setup()
        self.ui.MeasurementProgressText.setText(f"Receiving parameters from MCU...{left_of_burst_str}")
        self.ui.MeasurementProgressBar.setValue(2)
        if not self.measurement_receive_parameters():
            print("Error")
            self.ui.MeasurementProgressBar.setValue(7)
            self.measurement_ui_enabled(False)
            return

        self.waiting_for_trigger = True
        self.ui.MeasurementProgressText.setText(f"Waiting for trigger signal...{left_of_burst_str}")
        self.ui.MeasurementProgressBar.setValue(3)
        while not self.serial.inWaiting():
            QApplication.processEvents()
        self.waiting_for_trigger = False

        self.receiving_temp_data = True
        self.ui.MeasurementProgressText.setText(f"Receiving data from MCU...{left_of_burst_str}")
        self.ui.MeasurementProgressBar.setValue(4)
        self.measurement_receive_data()
        self.receiving_temp_data = False
        if self.save_generator_log:
            self.ui.MeasurementProgressText.setText(f"Reading impedance data from generator...{left_of_burst_str}")
            self.ui.MeasurementProgressBar.setValue(5)
            self.read_impedance_data()
            self.save_generator_log = False
        self.ui.MeasurementProgressText.setText(f"Receiving measurement report from MCU...{left_of_burst_str}")
        self.ui.MeasurementProgressBar.setValue(6)
        self.measurement_receive_report()
        self.ui.MeasurementProgressText.setText(f"Saving record...{left_of_burst_str}")
        self.ui.MeasurementProgressBar.setValue(7)
        self.measurement_save_record()
        self.ui.MeasurementProgressText.setText(f"Done{left_of_burst_str}")
        self.ui.MeasurementProgressBar.setValue(8)
        self.measurement_ui_enabled(False)
        return

    def burst_measure(self):
        self.check_channels_enabled()

        number_of_measurements, ok = QtWidgets.QInputDialog.getInt(self.ui.BurstMeasureButton,
                                                                   "Burst measurement",
                                                                   "Number of measurements:",
                                                                   QLineEdit.Normal)
        if not (ok and number_of_measurements):
            return

        for i in range(number_of_measurements):
            self.measure(left_of_burst=(number_of_measurements-i))

    def check_channels_enabled(self):
        enabled_channels = list(x.available for x in self.record.channels).count(True)
        if not enabled_channels:
            messagebox = QMessageBox(QMessageBox.Critical,
                                     "Measurement error",
                                     "Please enable at least one channel",
                                     QMessageBox.Ok)
            messagebox.exec()
            return

    def measurement_send_setup(self):
        # Send UI settings to MCU
        setup_string = ""
        setup_string += f"RecLen:{str(self.record.length_ms)};"
        setup_string += f"RecInt:{str(self.record.interval_us)};"

        enabled_channels = [0, 0, 0, 0]
        tc_sensitivity_ranking = ["E", "J", "K", "T"]
        highest_sensitivity_tc_available = "T"
        for i in range(len(self.record.channels)):
            channel = self.record.channels[i]
            if not channel.available:
                continue
            enabled_channels[i] = 1
            if tc_sensitivity_ranking.index(channel.tc_type) < tc_sensitivity_ranking.index(highest_sensitivity_tc_available):
                highest_sensitivity_tc_available = channel.tc_type
        setup_string += f"TcType:{highest_sensitivity_tc_available};"
        enabled_channels_format = "|".join(str(x) for x in enabled_channels)
        setup_string += f"EnChan:{enabled_channels_format};"

        setup_string += "\0"

        self.serial.write(setup_string.encode())
        print(setup_string)

        return

    def measurement_receive_parameters(self):
        while not self.serial.inWaiting():
            QApplication.processEvents()

        parameters_raw = self.serial.readline(Parameters.service_msg_size)
        try:
            parameters = parameters_raw.decode().rstrip("\n")
        except UnicodeDecodeError:
            self.serial.read(self.serial.inWaiting())
            return False
        parameters_split = parameters.split(";")

        for parameter in parameters_split:
            parameter_name_value = parameter.split(":")
            parameter_name = parameter_name_value[0]
            parameter_value = parameter_name_value[1]

            if parameter_name == "CjcTmp":
                self.record.cold_junction_temperature = float(parameter_value)
            elif parameter_name == "AlgRfr":
                self.record.analog_reference_voltage = float(parameter_value)
            elif parameter_name == "AplOfs":
                self.record.applied_offset_voltage = float(parameter_value)
            elif parameter_name == "AdcBuf":
                self.record.adc_buffer_size = int(parameter_value)
            elif parameter_name == "PktCnt":
                self.record.target_packet_count = int(parameter_value)

        return True

    def measurement_receive_data(self):
        print(f"Buffers to receive: {self.record.target_packet_count}")

        channel_buffers = {}
        self.record.usb_buffer_size = 0
        for i in range(self.record.num_of_channels):
            if not self.record.channels[i].available:
                continue
            channel_buffers[i] = []
            self.record.usb_buffer_size += self.record.adc_buffer_size

        # Receive data from MCU
        buffers = []
        for i in range(self.record.target_packet_count):
            usb_packet = self.serial.read(self.record.usb_buffer_size)
            buffers.append(usb_packet)

        # Process received data
        for buffer in buffers:
            start_index = 0
            end_index = self.record.adc_buffer_size
            for i in range(self.record.num_of_channels):
                if not self.record.channels[i].available:
                    continue
                channel_buffers[i].extend(buffer[start_index:end_index])
                start_index = end_index
                end_index += self.record.adc_buffer_size

        record_amount = int((self.record.length_ms * 1000.0) / self.record.interval_us)
        for channel_index, channel_data in channel_buffers.items():
            for i in range(0, record_amount * 2, 2):
                adc_reading_num = (channel_data[i] << 8) + channel_data[i + 1]
                adc_reading_voltage = adc_reading_num / pow(2, 16) * self.record.analog_reference_voltage
                temperature = self.calculate_thermocouple_temperature(measured_voltage=adc_reading_voltage,
                                                                      tc_type=self.record.channels[channel_index].tc_type)
                # if temperature is None or temperature > 220 or temperature < -20:
                if temperature is None:

                    temperature = -20
                self.record.channels[channel_index].raw_data.append(temperature)

        return

    def measurement_receive_report(self):
        while not self.serial.inWaiting():
            QApplication.processEvents()

        parameters_raw = self.serial.readline(Parameters.service_msg_size)
        try:
            parameters = parameters_raw.decode().rstrip("\n")
        except UnicodeDecodeError:
            self.serial.read(self.serial.inWaiting())
            return False
        parameters_split = parameters.split(";")

        for parameter in parameters_split:
            parameter_name_value = parameter.split(":")
            parameter_name = parameter_name_value[0]
            parameter_value = parameter_name_value[1]

            if parameter_name == "TrsErr":
                transmission_error = int(parameter_value)
                if transmission_error != 0:
                    print(f"Transmission error! Code: {transmission_error}")
            elif parameter_name == "DrpPkt":
                dropped_packets = int(parameter_value)
                if dropped_packets != 0:
                    print(f"Dropped packet(s) detected! Amount: {dropped_packets}")

        return True

    def calculate_thermocouple_temperature(self, measured_voltage, tc_type):
        if measured_voltage > 0:
            tc_voltage = (measured_voltage - self.record.applied_offset_voltage) / Parameters.inamp_gain
            tc_voltage_uv = tc_voltage * 10**6

            cold_junction_dir = "+" if self.record.cold_junction_temperature > 0 else "-"
            cold_junction_voltage_uv = 0
            for i in range(len(Parameters.temp_to_voltage[tc_type][cold_junction_dir])):
                cold_junction_voltage_uv += Parameters.temp_to_voltage[tc_type][cold_junction_dir][i] * (self.record.cold_junction_temperature ** i)
            if tc_type == "K" and cold_junction_dir == "+":
                cold_junction_voltage_uv += Parameters.temp_to_voltage[tc_type]["alpha"][0] * \
                                            math.exp(Parameters.temp_to_voltage[tc_type]["alpha"][1] * ((self.record.cold_junction_temperature - 126.9686)**2))

            tc_voltage_uv += cold_junction_voltage_uv

            tc_temperature_dir = "+" if tc_voltage_uv > 0 else "-"
            tc_temperature = 0
            for j in range(len(Parameters.voltage_to_temp[tc_type][tc_temperature_dir])):
                tc_temperature += Parameters.voltage_to_temp[tc_type][tc_temperature_dir][j] * (tc_voltage_uv ** j)

            return tc_temperature

    def read_impedance_data(self):
        while not self.gen_log_received:
            QApplication.processEvents()

        parameter_names_list = [x.strip() for x in self.log_parameter_names.split(",")]
        parameter_names_list = list(filter(None, parameter_names_list))

        parameter_dict = {}
        for name in parameter_names_list:
            parameter_dict[name] = []

        for i in range(len(self.log_data)):
            current_row = self.log_data[i]
            current_row_list = current_row.split(",")

            parameter_index = 0
            for key in parameter_dict.keys():
                parameter_dict[key].append(current_row_list[parameter_index])
                parameter_index += 1

        for parameter in ["U", "I", "Z", "P", "Phase"]:
            parameter_list = parameter_dict[Parameters.log_column_names[parameter]]
            parameter_list_float = [round(float(x) * Parameters.log_column_scales[parameter],
                                          Parameters.log_meaningful_float_characters[parameter])
                                    for x in parameter_list]

            self.record.generator_raw_data[parameter] = parameter_list_float

    def measurement_save_record(self):
        # Save received data
        time_now_formatted = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        record_file_name = time_now_formatted + ".json"
        self.record.log_date_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        jsonpickle.set_encoder_options('json', indent=4)
        output_json = jsonpickle.encode(self.record)

        i = 2
        if os.path.isfile(str(self.current_folder + record_file_name)):
            record_file_name += "_1"
            while os.path.isfile(str(self.current_folder + record_file_name)):
                record_file_name = record_file_name[:-2]
                record_file_name += ("_" + str(i))
                i += 1

        with open(str(self.current_folder + record_file_name), "w") as output_file:
            output_file.writelines(output_json)

        self.refresh_record_explorer()

        # Reset channel data
        for channel in self.record.channels:
            channel.raw_data = []

        self.record.impedance_raw_data = []

    def refresh_record_explorer(self):
        self.ui.CurrentDirectoryLine.setText(self.current_folder)

        self.ui.RecordsList.clear()
        self.ui.RecordsList.setItemAlignment(Qt.AlignLeft)

        root, dir_list, record_list = next(os.walk(self.current_folder))
        folder_icon = QIcon("UI/folder.png")
        temp_item = QListWidgetItem("_-_temp_-_")
        self.ui.RecordsList.addItem(temp_item)

        for directory in dir_list:
            item = QListWidgetItem(directory)
            item.setIcon(folder_icon)
            item.setTextAlignment(Qt.AlignLeft)
            item.setBackground(QColor("#fff0d6"))
            item.setSizeHint(QSize(2000, self.ui.RecordsList.sizeHintForRow(0)))
            self.ui.RecordsList.addItem(item)

        first_item = None
        for record in record_list:
            if ".json" not in record:
                continue
            item = QListWidgetItem(record.replace(".json", ""))
            item.setTextAlignment(Qt.AlignLeft)
            item.setSizeHint(QSize(2000, self.ui.RecordsList.sizeHintForRow(0)))

            date_in_name = record.split("-")[0]
            try:
                int(date_in_name)
                self.ui.RecordsList.insertItem(len(dir_list) + 1, item)
                first_item = item
            except ValueError:
                self.ui.RecordsList.addItem(item)

        self.ui.RecordsList.takeItem(self.ui.RecordsList.row(temp_item))
        self.ui.RecordsList.setCurrentItem(first_item)

    def view_selected_record(self):
        selected_record = self.ui.RecordsList.currentItem()
        if not selected_record:
            return

        if os.path.isdir(self.current_folder + selected_record.text()):
            self.current_folder = self.current_folder + selected_record.text() + "/"
            self.refresh_record_explorer()
            return

        selected_record_file_name = selected_record.text() + ".json"
        plot_window = PlotLogic(self.current_folder, selected_record_file_name)
        plot_window.run()

    def directory_up(self):
        current_directory_levels = self.current_folder.rstrip("/").split("/")
        if len(current_directory_levels) > 1:
            self.current_folder = "/".join(current_directory_levels[:-1])
            self.current_folder += "/"
            self.refresh_record_explorer()

    def new_directory(self):
        folder_name, ok = QtWidgets.QInputDialog.getText(self.ui.RecordsList,
                                                         "Create folder",
                                                         "Folder name:",
                                                         QLineEdit.Normal)
        if not (ok and folder_name):
            return

        try:
            print(self.current_folder + folder_name + "/")
            os.mkdir(self.current_folder + folder_name + "/")
        except FileExistsError:
            messagebox = QMessageBox(QMessageBox.Critical,
                                     "Folder creation error",
                                     "Folder already exists!",
                                     QMessageBox.Ok)
            messagebox.exec()
            return

        self.refresh_record_explorer()


    def rename_selected_record(self):
        selected_record = self.ui.RecordsList.currentItem()
        if not selected_record:
            return

        current_name = selected_record.text()
        new_name, ok = QtWidgets.QInputDialog.getText(self.ui.RecordsList,
                                                      "Rename",
                                                      "New name:",
                                                      QLineEdit.Normal,
                                                      current_name)
        if not (ok and new_name):
            return

        if not os.path.isdir(str(self.current_folder + current_name + "/")):
            new_name += ".json"
            current_name += ".json"

        os.rename(str(self.current_folder + current_name), str(self.current_folder + new_name))
        self.refresh_record_explorer()

    def delete_selected_record(self):
        selected_record = self.ui.RecordsList.currentItem()
        if not selected_record:
            return

        selected_record_name = selected_record.text()

        if not os.path.isdir(self.current_folder + selected_record_name + "/"):
            selected_record_name += ".json"

        messagebox = QMessageBox(QMessageBox.Question,
                                 "Confirm delete",
                                 f"Are you sure you want to delete \"{selected_record_name}\"?",
                                 QMessageBox.Yes | QMessageBox.No)
        response = messagebox.exec()

        if response == QMessageBox.No:
            return

        send2trash(str(self.current_folder + selected_record_name))
        self.refresh_record_explorer()
        self.ui.RecordsList.setCurrentRow(0)

    def set_field_limit_values(self):
        max_filter_frequency_khz = (1.0 / (self.record.interval_us / 10**3)) / 2 - 0.001
        filter_field_names = QRegularExpression(r".*Frequency.*")
        filter_field_widgets = self.form.findChildren(QDoubleSpinBox, filter_field_names)
        for widget in filter_field_widgets:
            widget.setMaximum(max_filter_frequency_khz)

    def stop_serial_ports(self):
        self.read_thread_active = False
        if self.connection_established:
            self.serial.close()
        if self.connection_established_gen:
            self.serial_gen.close()


if __name__ == "__main__":
    main_window = MainWindowLogic()
    main_window.run()
    
