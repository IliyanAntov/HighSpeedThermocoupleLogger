from PC.Channel import Channel


class Record:
    def __init__(self):
        self.interval_us = None
        self.length_ms = None

        self.num_of_channels = 4
        self.channels = []
        for i in range(self.num_of_channels):
            self.channels.append(Channel())

