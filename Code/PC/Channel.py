class Channel:
    def __init__(self):
        self.available = True

        self.raw_data = None
        self.tc_type = None

        self.data_processing_enabled = False
        self.data_filter_order = None
        self.data_filter_freq_khz = None

        self.temperature_prediction_enabled = False
        self.prediction_time_constant_ms = None
        self.prediction_queue_length = None

        self.prediction_processing_enabled = False
        self.post_process_filter_order = None
        self.post_process_filter_freq_khz = None
