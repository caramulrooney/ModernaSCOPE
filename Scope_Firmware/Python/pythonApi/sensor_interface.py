from numpy.random import rand
from collections import deque
from constants import N_ELECTRODES
from threading import Event, Timer
from config import Config
from electrode_names import ElectrodeNames
from spe_mapping import ElectrodeMap
import numpy as np
import serial
import json

class MeasurementInterrupt(KeyboardInterrupt):
    """
    Exception for handling a keyboard interrupt during a measurement. The top-level program should handle a keyboard interrupt during this action and abort the measurement but continue running at the main prompt.
    """

class MeasurementRequest():
    def __init__(self, n_data_points: int, n_points_remaining: int):
        self.n_data_points = n_data_points
        self.n_points_remaining = n_points_remaining
        self.ready = Event()
        self.data = None
        self.has_been_read = False

class SensorInterface():
    def __init__(self, cache_size: int = 100):
        self.cache_size = cache_size
        self.cache = deque()
        self.measurements_pending: deque[MeasurementRequest] = deque()
        self.electrode_map = ElectrodeMap(rev = Config.board_revision)

    def get_voltages_single(self) -> list[float]:
        """
        Talk to the sensor and get a single voltage from each of the electrodes.
        """
        if Config.random_data:
            return rand(N_ELECTRODES).tolist()
        if Config.debug.serial.com_port:
            print(f"Trying to connect on Serial COM port '{Config.serial_port}'")
        # else
        n_tries = 5
        for i in range(n_tries):
            try:
                with serial.Serial(Config.serial_port, 115200, timeout=1) as ser: # TO DO: change serial port
                    ser.write(b'e') # send request for electrode data
                    response = ser.readline().decode().strip() # read response
                    if Config.debug.serial.readline.raw:
                        print(response)
                    electrode_data = json.loads(response) # parse json data
                    if Config.debug.serial.readline.loads:
                        print("Electrode voltages: ", electrode_data)
                    return self.electrode_map.remap_sensor_list(electrode_data)
            except json.decoder.JSONDecodeError:
                print(f"Could not decode message: '{response}'.")
            except (UnicodeDecodeError, serial.SerialException):
                if Config.debug.serial.connection.error:
                    print(f"Error connecting to serial port. Retrying up to {n_tries - i - 1} more times.")
                pass
        raise serial.SerialException("Error connecting to serial port. Please check the connection and retry, or change the COM port in the config.json file and then type 'load'.")


    def __store_voltages_in_cache(self):
        if len(self.cache) >= self.cache_size:
            self.cache.popleft()
        # then, always:
        self.cache.append(self.get_voltages_single())

    def update(self):
        self.__store_voltages_in_cache()
        if Config.debug.threading.inside_thread.sensor_interface.measurements_pending.count:
            print(f"Number of measurements pending: {len(self.measurements_pending)}")
        requests_to_delete = []
        for i, measurement_request in enumerate(self.measurements_pending):
            measurement_request.n_points_remaining -= 1
            self.__check_if_promise_is_fulfilled(measurement_request)
            if measurement_request.has_been_read:
                requests_to_delete.append(i)
        # delete the elements in a second step
        for n_deleted_already, i in enumerate(requests_to_delete):
            if Config.debug.threading.inside_thread.sensor_interface.measurements_pending.delete:
                print(f"deleting measurement request {i}, offset by position {n_deleted_already}.")
            del self.measurements_pending[i - n_deleted_already]
            if Config.debug.threading.inside_thread.sensor_interface.measurements_pending.count:
                print(f"length of data deque: {len(self.cache)}")

    def __check_if_promise_is_fulfilled(self, measurement_request):
        if Config.debug.threading.inside_thread.sensor_interface.measurements_pending.count:
            print(f"checking promise. n_points_remaining = {measurement_request.n_points_remaining}")
        if measurement_request.n_points_remaining <= 0:
            if Config.debug.threading.inside_thread.sensor_interface.measurements_pending.count:
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
        try:
            while not promise.ready.wait(0.1):
                pass
        except KeyboardInterrupt:
            promise.has_been_read = True
            raise MeasurementInterrupt("Aborting measurement due to keyboard interrupt.")
        else:
            if Config.debug.threading.inside_thread.sensor_interface.promise.ready:
                print("promise is ready!")
            return_data = self.__get_cache(promise.n_data_points)
            promise.has_been_read = True # flag the request as completed so it can be deleted
            return return_data

    def get_future_voltages_blocking(self, n: int) -> list[float]:
        return self.evaluate_promise_blocking(self.__get_voltages_promise(n, future = True))

    def get_past_voltages_blocking(self, n: int) -> list[float]:
        return self.evaluate_promise_blocking(self.__get_voltages_promise(n, future = False))
