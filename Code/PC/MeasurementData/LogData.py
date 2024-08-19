from datetime import datetime
import PC.MeasurementData.Parameters as Parameters


class Record:
    def __init__(self, number_of_channels=1):
        self.length_ms = 100
        self.interval_us = 10
        self.log_date_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        self.generator_command = None
        self.cold_junction_temperature = 0
        self.analog_reference_voltage = 0
        self.applied_offset_voltage = 0
        self.number_of_conversions = 0
        self.adc_buffer_size = 0
        self.usb_buffer_size = 0
        self.target_packet_count = 0

        self.generator_log_interval_ms = Parameters.generator_log_interval_ms
        self.generator_log_start_time_ms = Parameters.generator_log_start_time_ms
        self.generator_raw_data = {}

        # NOTE: for backwards compatibility
        self.impedance_raw_data = None

        self.num_of_channels = number_of_channels
        self.channels = []
        for i in range(self.num_of_channels):
            self.channels.append(Channel())


class Channel:
    def __init__(self):
        self.available = False

        self.raw_data = []
        self.tc_type = "J"

        self.data_processing_enabled = False
        self.data_filter_order = 3
        self.data_filter_freq_khz = 10.0

        self.temperature_prediction_enabled = False
        self.prediction_time_constant_ms = 100.0
        self.prediction_queue_length = 10

        self.prediction_processing_enabled = False
        self.post_process_filter_order = 3
        self.post_process_filter_freq_khz = 10.0
