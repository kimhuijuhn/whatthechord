import time

class Timestamp:
    def __init__(self):
        self.start_time: float
        self.end_time: float

    def start(self):
        self.start_time = time.perf_counter()

    def capture(self):
        return time.perf_counter()