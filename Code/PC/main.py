from PyQt5.QtCore import QRegularExpression
from PyQt5.QtWidgets import *

from MainWindowUI import Ui_Form
from PyQt5 import QtWidgets
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

    def run(self):
        self.ui.setupUi(self.form)
        self.widgets = self.form.children()

        self.update_enabled_widgets()
        self.assign_button_functions()

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

        channel_parameters_widgets = []
        for widget_index in range(self.ui.ChannelParametersLayout.count()):
            widget = self.ui.ChannelParametersLayout.itemAt(widget_index).widget()
            if widget is None:
                continue
            elif isinstance(widget, QLabel):
                widget.setEnabled(True)
            else:
                widget.setEnabled(False)
                channel_parameters_widgets.append(widget)

        if status:
            self.update_channel_widgets_enable_status()

    def update_channel_widgets_enable_status(self):
        data_processing_checkbox_names = QRegularExpression(r"Data.*Enabled_\d")
        data_processing_checkbox_widgets = sorted(self.form.findChildren(QCheckBox, data_processing_checkbox_names), key=lambda x: x.objectName())
        prediction_checkbox_names = QRegularExpression(r"PredictionEnabled_\d")
        prediction_checkbox_widgets = sorted(self.form.findChildren(QCheckBox, prediction_checkbox_names), key=lambda x: x.objectName())
        prediction_processing_checkbox_names = QRegularExpression(r"Prediction.+Enabled_\d")
        prediction_processing_checkbox_widgets = sorted(self.form.findChildren(QCheckBox, prediction_processing_checkbox_names), key=lambda x: x.objectName())

        tc_type_names = QRegularExpression(r"ChannelTcType_\d")
        tc_type_widgets = sorted(self.form.findChildren(QComboBox, tc_type_names), key=lambda x: x.objectName())

        channel_enabled_checkbox_names = QRegularExpression(r"ChannelEnabled_\d")
        channel_enabled_checkbox_widgets = sorted(self.form.findChildren(QCheckBox, channel_enabled_checkbox_names), key=lambda x: x.objectName())
        for widget in channel_enabled_checkbox_widgets:
            widget.setEnabled(True)

        for i in range(len(data_processing_checkbox_widgets)):
            data_processing_checkbox_widgets[i].setEnabled(channel_enabled_checkbox_widgets[i].isChecked())
            prediction_checkbox_widgets[i].setEnabled(channel_enabled_checkbox_widgets[i].isChecked())
            prediction_processing_checkbox_widgets[i].setEnabled(channel_enabled_checkbox_widgets[i].isChecked())
            tc_type_widgets[i].setEnabled(channel_enabled_checkbox_widgets[i].isChecked())

        data_processing_names = QRegularExpression(r"Data.*_\d")
        data_processing_widgets = sorted(self.form.findChildren((QSpinBox, QDoubleSpinBox), data_processing_names), key=lambda x: x.objectName())
        for i in range(len(data_processing_widgets)):
            if channel_enabled_checkbox_widgets[i % 4].isChecked():
                data_processing_widgets[i].setEnabled(data_processing_checkbox_widgets[i % 4].isChecked())
            else:
                data_processing_widgets[i].setEnabled(False)

        prediction_names = QRegularExpression(r"Prediction[^LowPass].*_\d")
        prediction_widgets = sorted(self.form.findChildren((QSpinBox, QDoubleSpinBox), prediction_names), key=lambda x: x.objectName())
        for i in range(len(prediction_widgets)):
            if channel_enabled_checkbox_widgets[i % 4].isChecked():
                prediction_widgets[i].setEnabled(prediction_checkbox_widgets[i % 4].isChecked())
            else:
                prediction_widgets[i].setEnabled(False)

        prediction_processing_names = QRegularExpression(r"PredictionLowPass.*_\d")
        prediction_processing_widgets = sorted(self.form.findChildren((QSpinBox, QDoubleSpinBox), prediction_processing_names), key=lambda x: x.objectName())
        for i in range(len(prediction_widgets)):
            if channel_enabled_checkbox_widgets[i % 4].isChecked():
                prediction_processing_widgets[i].setEnabled(prediction_processing_checkbox_widgets[i % 4].isChecked())
            else:
                prediction_processing_widgets[i].setEnabled(False)


    def assign_button_functions(self):
        self.ui.ConnectionButton.clicked.connect(self.vcp_connection_change)
        self.ui.ChannelEnabled_1.clicked.connect(self.update_channel_widgets_enable_status)
        self.ui.ChannelEnabled_2.clicked.connect(self.update_channel_widgets_enable_status)
        self.ui.ChannelEnabled_3.clicked.connect(self.update_channel_widgets_enable_status)
        self.ui.ChannelEnabled_4.clicked.connect(self.update_channel_widgets_enable_status)
        self.ui.DataLowPassEnabled_1.clicked.connect(self.update_channel_widgets_enable_status)
        self.ui.DataLowPassEnabled_2.clicked.connect(self.update_channel_widgets_enable_status)
        self.ui.DataLowPassEnabled_3.clicked.connect(self.update_channel_widgets_enable_status)
        self.ui.DataLowPassEnabled_4.clicked.connect(self.update_channel_widgets_enable_status)
        self.ui.PredictionEnabled_1.clicked.connect(self.update_channel_widgets_enable_status)
        self.ui.PredictionEnabled_2.clicked.connect(self.update_channel_widgets_enable_status)
        self.ui.PredictionEnabled_3.clicked.connect(self.update_channel_widgets_enable_status)
        self.ui.PredictionEnabled_4.clicked.connect(self.update_channel_widgets_enable_status)
        self.ui.PredictionLowPassEnabled_1.clicked.connect(self.update_channel_widgets_enable_status)
        self.ui.PredictionLowPassEnabled_2.clicked.connect(self.update_channel_widgets_enable_status)
        self.ui.PredictionLowPassEnabled_3.clicked.connect(self.update_channel_widgets_enable_status)
        self.ui.PredictionLowPassEnabled_4.clicked.connect(self.update_channel_widgets_enable_status)
        record_length_widget = self.ui.RecordLengthValue
        self.ui.RecordLengthMinButton.clicked.connect(lambda: record_length_widget.setValue(self.record_length_min_max["min"]))
        self.ui.RecordLengthMaxButton.clicked.connect(lambda: record_length_widget.setValue(self.record_length_min_max["max"]))
        record_interval_widget = self.ui.RecordIntervalValue
        self.ui.RecordIntervalMinButton.clicked.connect(lambda: record_interval_widget.setValue(self.record_interval_min_max["min"]))
        self.ui.RecordIntervalMaxButton.clicked.connect(lambda: record_interval_widget.setValue(self.record_interval_min_max["max"]))

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


if __name__ == "__main__":
    main_window = MainWindowLogic()
    main_window.run()
    
