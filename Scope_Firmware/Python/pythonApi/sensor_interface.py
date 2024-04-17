from numpy.random import rand
from collections import deque
from constants import N_ELECTRODES
from threading import Event, Timer
from config import Config
from electrode_names import ElectrodeNames
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
        self.electrode_id_to_spe = self.create_spe_mapping()
        self.cache_size = cache_size
        self.cache = deque()
        self.measurements_pending: deque[MeasurementRequest] = deque()

    def get_voltages_single(self) -> list[float]:
        """
        Talk to the sensor and get a single voltage from each of the electrodes.
        """
        if Config.random_data:
            return rand(N_ELECTRODES).tolist()
        # else
        n_tries = 5
        for i in range(n_tries):
            try:
                with serial.Serial('COM4', 115200, timeout=1) as ser: # TO DO: change serial port
                    ser.write(b'e') # send request for electrode data
                    response = ser.readline().decode().strip() # read response
                    if Config.debug:
                        print(response)
                    electrode_data = json.loads(response) # parse json data
                    if Config.debug:
                        print("Electrode voltages: ", electrode_data)
                    return self.remap_electrode_ids(electrode_data)
            except (UnicodeDecodeError, serial.SerialException):
                # if Config.debug:
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
        if Config.debug:
            print(f"Number of measurements pending: {len(self.measurements_pending)}")
        requests_to_delete = []
        for i, measurement_request in enumerate(self.measurements_pending):
            measurement_request.n_points_remaining -= 1
            self.__check_if_promise_is_fulfilled(measurement_request)
            if measurement_request.has_been_read:
                requests_to_delete.append(i)
        # delete the elements in a second step
        for n_deleted_already, i in enumerate(requests_to_delete):
            if Config.debug:
                print(f"deleting measurement request {i}, offset by position {n_deleted_already}.")
            del self.measurements_pending[i - n_deleted_already]
            if Config.debug:
                print(f"length of data deque: {len(self.cache)}")

    def __check_if_promise_is_fulfilled(self, measurement_request):
        if Config.debug:
            print(f"checking promise. n_points_remaining = {measurement_request.n_points_remaining}")
        if measurement_request.n_points_remaining <= 0:
            if Config.debug:
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
            if Config.debug:
                print("promise is ready!")
            return_data = self.__get_cache(promise.n_data_points)
            promise.has_been_read = True # flag the request as completed so it can be deleted
            return return_data

    def get_future_voltages_blocking(self, n: int) -> list[float]:
        return self.evaluate_promise_blocking(self.__get_voltages_promise(n, future = True))

    def get_past_voltages_blocking(self, n: int) -> list[float]:
        return self.evaluate_promise_blocking(self.__get_voltages_promise(n, future = False))

    def create_spe_mapping(self) -> dict[int:int]:
        electrode_id_battleship_to_spe = {
            "A6":  95,
            "A8":  94,
            "A9":  93,
            "A7":  92,
            "A4":  91,
            # "A1":  90,
            # "A1":  89,
            "A5":  88,
            "B2":  87,
            "B4":  86,
            "B5":  85,
            "B3":  84,
            "A12": 83,
            "A11": 82,
            "A10": 81,
            "B1":  80,
            "B10": 79,
            "B12": 78,
            "C1":  77,
            "B11": 76,
            # "A1":  75,
            "B7":  74,
            "B6":  73,
            "B9":  72,
            "C6":  71,
            "C8":  70,
            "C9":  69,
            "C7":  68,
            "C4":  67,
            "C3":  66,
            "C2":  65,
            "C5":  64,
            # "A1":  63,
            "D4":  62,
            "D5":  61,
            "D3":  60,
            "C12": 59,
            "C11": 58,
            "C10": 57,
            "D1":  56,
            "D10": 55,
            "D12": 54,
            "E1":  53,
            "D11": 52,
            "D8":  51,
            "D7":  50,
            "D6":  49,
            "D9":  48,
            # "A1":  47,
            # "A1":  46,
            # "A1":  45,
            # "A1":  44,
            # "A1":  43,
            # "A1":  42,
            # "A1":  41,
            # "A1":  40,
            # "A1":  39,
            # "A1":  38,
            # "A1":  37,
            # "A1":  36,
            # "A1":  35,
            # "A1":  34,
            # "A1":  33,
            # "A1":  32,
            "H10": 31,
            "H12": 30,
            # "A1":  29,
            "H11": 28,
            "H8":  27,
            "H7":  26,
            "H6":  25,
            "H9":  24,
            "H2":  23,
            "H4":  22,
            "H5":  21,
            "H3":  20,
            "G12": 19,
            "G11": 18,
            "G10": 17,
            "H1":  16,
            "G6":  15,
            "G8":  14,
            "G9":  13,
            "G7":  12,
            "G4":  11,
            "G3":  10,
            "G2":  9,
            "G5":  8,
            "F6":  7,
            # "A1":  6,
            # "A1":  5,
            # "A1":  4,
            # "A1":  3,
            # "A1":  2,
            # "A1":  1,
            # "A1":  0,
        }
        electrode_id_to_spe = {ElectrodeNames.parse_electrode_input(key)[0]: val for key, val in electrode_id_battleship_to_spe.items()}
        return electrode_id_to_spe

    def remap_electrode_ids(self, voltages: list[float]) -> list[float]:
        remapped_voltages = [0 for x in range(N_ELECTRODES)]
        for idx, value in enumerate(voltages):
            if idx in self.electrode_id_to_spe.keys():
                remapped_voltages[self.electrode_id_to_spe[idx]] = value
            # else, leave it at zero
        return remapped_voltages
