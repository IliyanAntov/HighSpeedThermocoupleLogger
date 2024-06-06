import os
import time

from PyQt5.QtCore import QRegularExpression, Qt, QSize, QEventLoop, QTimer, pyqtSignal, QObject
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import *

from MainWindowUI import Ui_Form
from PyQt5 import QtWidgets, QtTest
import sys


class MainWindowLogic:
    def __init__(self):
        self.ui = Ui_Form()
        self.app = QtWidgets.QApplication(sys.argv)
        self.form = QtWidgets.QWidget()
        self.widgets = []
        self.connection_established = False

        self.record_length_min_max = {
            "min": 100,
            "max": 2000
        }
        self.record_interval_min_max = {
            "min": 10,
            "max": 1000
        }

        self.channel_enabled = [False, False, False, False]
        self.data_processing_enabled = [False, False, False, False]
        self.temperature_prediction_enabled = [False, False, False, False]
        self.prediction_processing_enabled = [False, False, False, False]

        self.record_folder_dir = "./data/"

    def run(self):
        self.ui.setupUi(self.form)
        self.widgets = self.form.children()

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
        tc_type_selector_widget.setEnabled(self.channel_enabled[channel_index])
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
        temperature_prediction_widgets = self.form.findChildren((QSpinBox, QDoubleSpinBox), temperature_prediction_names)
        # Enable/Disable relevant objects
        for widget in temperature_prediction_widgets:
            widget.setEnabled(self.temperature_prediction_enabled[channel_index] and self.channel_enabled[channel_index])

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
        record_length_widget = self.ui.RecordLengthValue
        self.ui.RecordLengthMinButton.clicked.connect(lambda: record_length_widget.setValue(self.record_length_min_max["min"]))
        self.ui.RecordLengthMaxButton.clicked.connect(lambda: record_length_widget.setValue(self.record_length_min_max["max"]))
        record_interval_widget = self.ui.RecordIntervalValue
        self.ui.RecordIntervalMinButton.clicked.connect(lambda: record_interval_widget.setValue(self.record_interval_min_max["min"]))
        self.ui.RecordIntervalMaxButton.clicked.connect(lambda: record_interval_widget.setValue(self.record_interval_min_max["max"]))

        self.ui.RenameRecordButton.clicked.connect(self.rename_selected_record)
        self.ui.DeleteRecordButton.clicked.connect(self.delete_selected_record)

    def vcp_connection_change(self):
        if self.connection_established:
            self.connection_established = False
            self.ui.ConnectionButton.setText("Connect")
            # self.vcp_disconnect()
        else:
            self.connection_established = True
            self.ui.ConnectionButton.setText("Disconnect")
            # self.vcp_connect()
        self.update_enabled_widgets()

    def measure(self):
        self.form.setEnabled(False)

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
        progress_dialog.setLabelText("Processing received data...")
        progress_dialog.setValue(3)
        self.measurement_process_data()
        progress_dialog.setLabelText("Done")
        progress_dialog.setValue(4)

        self.form.setEnabled(True)

        return

    def measurement_send_setup(self):
        # Send UI settings to MCU
        loop = QEventLoop()
        QTimer.singleShot(1000, loop.quit)
        loop.exec_()
        return

    def measurement_receive_data(self):
        # Receive data from MCU
        loop = QEventLoop()
        QTimer.singleShot(1000, loop.quit)
        loop.exec_()
        return

    def measurement_process_data(self):
        # Process and save received data
        loop = QEventLoop()
        QTimer.singleShot(1000, loop.quit)
        loop.exec_()
        return

    def display_available_records(self):
        self.ui.RecordsList.clear()
        self.ui.RecordsList.setItemAlignment(Qt.AlignRight)
        record_list = os.listdir(self.record_folder_dir)
        for record in record_list:
            item = QListWidgetItem(record.replace(".json", ""))
            item.setTextAlignment(Qt.AlignRight)
            self.ui.RecordsList.addItem(item)

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

        os.rename(str(self.record_folder_dir + current_name + ".json"), str(self.record_folder_dir + new_name + ".json"))
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

        os.remove(str(self.record_folder_dir + selected_record_name + ".json"))
        self.display_available_records()


if __name__ == "__main__":
    main_window = MainWindowLogic()
    main_window.run()
    
