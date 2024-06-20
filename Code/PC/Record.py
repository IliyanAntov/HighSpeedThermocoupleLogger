from PC.Channel import Channel


class Record:
    def __init__(self, number_of_channels=1):
        self.length_ms = 100
        self.interval_us = 10
        self.cold_junction_temperature = 0
        self.analog_reference_voltage = 0
        self.applied_voltage_offset = 0

        self.num_of_channels = number_of_channels
        self.channels = []
        for i in range(self.num_of_channels):
            self.channels.append(Channel())

