class Channel:
    def __init__(self):
        self.available = False

        self.raw_data = None
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
