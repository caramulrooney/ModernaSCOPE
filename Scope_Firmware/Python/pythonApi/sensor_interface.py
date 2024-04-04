from numpy.random import rand
from collections import deque
from constants import N_ELECTRODES
from threading import Event, Timer

class IntervalTimer(Timer):
    def __init__(self, *args, **kwargs):
        """
        Set daemon property to True during initialization.
        """
        super().__init__(*args, **kwargs)
        self.daemon = True

    def run(self):
        """
        Run indefinitely. Restart the timer as soon as it has elapased.
        """
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class MeasurementRequest():
    def __init__(self, n_data_points: int, n_points_remaining: int):
        self.n_data_points = n_data_points
        self.n_points_remaining = n_points_remaining
        self.ready = Event()
        self.data = None
        self.has_been_read = Event()

class SensorInterface():
    def __init__(self, cache_size: int = 100):
        self.cache_size = cache_size
        self.cache = deque()
        self.measurements_pending: deque[MeasurementRequest] = deque()

    def get_voltages_single(self) -> list[float]: # TODO: get data from sensor via pySerial
        """
        Talk to the sensor and get a single voltage from each of the electrodes.
        """
        return rand(N_ELECTRODES).tolist()

    def __store_voltages_in_cache(self):
        if len(self.cache) >= self.cache_size:
            self.cache.popleft()
        # then, always:
        self.cache.append(self.get_voltages_single())

    def update(self):
        self.__store_voltages_in_cache()
        print(f"Number of measurements pending: {len(self.measurements_pending)}")
        for measurement_request in self.measurements_pending:
            self.__check_if_promise_is_fulfilled(measurement_request)

        print(f"length of data deque: {len(self.cache)}")

    def __check_if_promise_is_fulfilled(self, measurement_request):
        print(f"checking promise. n_points_remaining = {measurement_request.n_points_remaining}")
        measurement_request.n_points_remaining -= 1
        if measurement_request.n_points_remaining <= 0:
            print("setting data")
            measurement_request.ready.set()

    def __get_voltages_promise(self, n, future = True):
        assert n < self.cache_size, f"Requested {n} measurements, which is more than are stored in memory at once (maximum of {self.cache_size})."
        if future:
            new_measurement_request = MeasurementRequest(n, n)
        else: # if past:
            if len(self.cache) >= n:
                new_measurement_request = MeasurementRequest(n, 0)
            else:
                new_measurement_request = MeasurementRequest(n, n - len(self.cache))
        self.__check_if_promise_is_fulfilled(new_measurement_request)
        self.measurements_pending.append(new_measurement_request)
        return new_measurement_request

    def __get_cache(self, n: int) -> list[float]:
        assert len(self.cache) >= n
        return list(self.cache)[-n:]

    def evaluate_promise_blocking(self, promise: MeasurementRequest) -> list[float]:
        promise.ready.wait()
        print("promise is ready!")
        return_data = self.__get_cache(promise.n_data_points)
        del promise
        return return_data

    def get_future_voltages_blocking(self, n: int) -> list[float]:
        return self.evaluate_promise_blocking(self.__get_voltages_promise(n, future = True))

    def get_past_voltages_blocking(self, n: int) -> list[float]:
        return self.evaluate_promise_blocking(self.__get_voltages_promise(n, future = False))
