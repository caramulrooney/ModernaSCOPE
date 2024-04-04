from numpy.random import rand
from collections import deque
from constants import N_ELECTRODES
from threading import Event

class MeasurementRequest():
    def __init__(self, n_data_points: int, n_points_remaining: int):
        self.n_data_points = n_data_points
        self.n_points_remaining = n_points_remaining
        self.ready = Event()
        self.data = None
        self.has_been_read = Event()

    def set_data(self, data):
        self.data = data
        self.ready.set()

class SensorInterface():
    def __init__(self, cache_size: int = 100):
        self.cache_size = cache_size
        self.cache = deque()
        self.measurements_pending: deque[MeasurementRequest] = deque()

    def get_voltages_single(self) -> list[float]: # TODO: get data from sensor via pySerial
        """
        Talk to the sensor and get a single voltage from each of the electrodes.
        """
        return rand(1, N_ELECTRODES)

    def store_voltages_in_cache(self):
        if len(self.cache) >= self.cache_size:
            self.cache.popleft()
        # then, always:
        self.cache.append(self.get_voltages_single())

    def run(self):
        self.store_voltages_in_cache()
        for i, measurement_request in enumerate(self.measurements_pending):
            measurement_request.n_points_remaining -= 1
            self.check_if_promises_are_fulfilled(measurement_request)
            if measurement_request.has_been_read:
                self.measurements_pending.pop(i)

    def check_if_promise_is_fulfilled(self, measurement_request):
        if measurement_request.n_points_remaining <= 0:
            measurement_request.set_data(self.get_past_voltages(measurement_request.n_data_points))

    def get_voltages_promise(self, n, future = True):
        assert n < self.cache_size, f"Requested {n} measurements, which is more than are stored in memory at once (maximum of {self.cache_size})."
        if future:
            new_measurement_request = MeasurementRequest(n, n)
        else: # if past:
            if len(self.cache) >= n:
                new_measurement_request = MeasurementRequest(n, 0)
            else:
                new_measurement_request = MeasurementRequest(n, n - len(self.cache))
        self.check_if_promise_is_fulfilled(new_measurement_request)
        self.measurements_pending.append(new_measurement_request)
        return new_measurement_request

    def get_past_voltages(self, n: int):
        assert len(self.cache) >= n
        return list(self.cache[-n:])

    @classmethod
    def evaluate_promise_blocking(cls, promise: MeasurementRequest):
        promise.ready.wait()
        return_data = promise.data
        promise.has_been_read.set() # flag it to be cleared out

    def get_future_voltages_blocking(self, n: int):
        return self.evaluate_promise_blocking(self.get_voltages_promise(n, future = True))

    def get_past_voltages_blocking(self, n: int):
        return self.evaluate_promise_blocking(self.get_voltages_promise(n, future = False))
