import inspect
from storage import Storage
from config import Config
from numpy.random import rand
import numpy as np
from constants import N_ELECTRODES
from electrode_names import ElectrodeNames
from typing import Protocol
import time

def unpack_namespace(func):
    def inner(self, namespace):
        sig = inspect.signature(func)
        kwargs = vars(namespace)
        kwargs["self"] = self
        args_to_pass = [kwargs[arg] for arg in sig.parameters.keys()]
        func(*args_to_pass)
    return inner

class FloatCombiner(Protocol):
    def __call__(self, *args: int) -> float: ...

class Sensor():
    def __init__(self):
        self.storage = Storage()

    def get_voltages_single(self) -> list[float]: # TODO: get data from sensor via pySerial
        """
        Talk to the sensor and get a single voltage from each of the electrodes.
        """
        return rand(1, N_ELECTRODES)

    def get_voltages_blocking(self, n_measurements: int = 2, delay_between_measurements: float = 2, average_func: FloatCombiner = np.mean):
        """
        Perform a certain number of consecutive measurements and report the average voltage at each electrode over the duration of the measurement.
        """
        print(f"Reading {n_measurements} measurements from each electrode over {n_measurements * delay_between_measurements} seconds.")
        voltages = np.zeros((n_measurements, N_ELECTRODES)) # 2-D array, n_measurements tall and N_ELECTRODES wide
        for measurement in range(n_measurements):
            voltages[measurement] = self.get_voltages_single() # set the next row of the array
            time.sleep(delay_between_measurements)
            print(f"\tMeasurement #{measurement + 1} of {n_measurements} completed.")

        # take the average of all the voltage readings over time for each electrode
        averaged = []
        for electrode_id in range(N_ELECTRODES):
            voltages_to_combine = np.transpose(voltages)[electrode_id]
            assert voltages_to_combine.size == n_measurements
            averaged.append(average_func(voltages_to_combine))

        return averaged

    @unpack_namespace
    def measure(self, electrodes, num_measurements, time_interval, show, voltage):
        if Config.debug:
            print(f"Inside of measure, {electrodes=}, {num_measurements=}, {time_interval=}, {show=}, {voltage=}")
        electrode_ids_being_measured = ElectrodeNames.parse_electrode_input(electrodes)
        if Config.debug:
            print(f"Measuring electrodes [{ElectrodeNames.to_battleship_notation(electrode_ids_being_measured)}].")

        voltages = self.get_voltages_blocking(n_measurements = num_measurements, delay_between_measurements = time_interval)

        # set voltage reading of electrodes not being measured to None
        for electrode_id in range(N_ELECTRODES):
            if electrode_id not in electrode_ids_being_measured:
                voltages[electrode_id] = None

        print("Converting measurement to ph...")
        guid = self.storage.add_measurement(voltages)
        print(f"Storing pH measurement with GUID '{guid}'")
        if voltage:
            self.show_most_recent_measurement_voltage()
            return
        if show:
            self.show_most_recent_measurement_ph()

    @unpack_namespace
    def calibrate(self, ph, electrodes, num_measurements, time_interval, show, voltage):
        if Config.debug:
            print(f"Inside of calibrate, {electrodes=}, {ph=}, {num_measurements=}, {time_interval=}, {show=}, {voltage=}")
        electrode_ids_being_calibrated = ElectrodeNames.parse_electrode_input(electrodes)
        if Config.debug:
            print(f"Calibrating electrodes [{ElectrodeNames.to_battleship_notation(electrode_ids_being_calibrated)}].")

        voltages = self.get_voltages_blocking(n_measurements = num_measurements, delay_between_measurements = time_interval)

        # set voltage reading of electrodes not being measured to None
        for electrode_id in range(N_ELECTRODES):
            if electrode_id not in electrode_ids_being_calibrated:
                voltages[electrode_id] = None
        guid = self.storage.add_calibration(ph, voltages)
        print(f"Storing calibration entry with GUID '{guid}'")
        if voltage:
            self.show_most_recent_calibration_voltage()
            return
        if show:
            self.show_most_recent_calibration_ph()

    @unpack_namespace
    def reload_files(self, config_filename):
        if Config.debug:
            print(f"Inside of reload_files")
        if not len(config_filename) == 0:
            Config.set_config(config_filename)
        self.storage = Storage()
        print(f"Loaded data from the files specified in '{config_filename}'.")

    @unpack_namespace
    def write_files(self, config_filename):
        if Config.debug:
            print(f"Inside of write_files")
        if not len(config_filename) == 0:
            Config.set_config(config_filename)
        self.storage.write_data()
        print(f"Wrote data to the files specified in '{config_filename}'.")

    @unpack_namespace
    def show(self, ids: bool, electrodes: str, calibration_voltage: bool, calibration_ph: bool, voltage: bool, ph: bool):
        show_electrodes: bool = electrodes != ""
        if sum([ids, show_electrodes, calibration_voltage, calibration_ph, voltage, ph]) > 1:
            print("Please select only one option at a time.")
            return
        if sum([ids, show_electrodes, calibration_voltage, calibration_ph, voltage, ph]) < 1:
            ids = True
        if ids:
            ElectrodeNames.ascii_art_electrode_ids()
            return
        if electrodes:
            electrode_ids = ElectrodeNames.parse_electrode_input(electrodes)
            ElectrodeNames.ascii_art_selected(electrode_ids)
            return
        if calibration_voltage:
            self.show_most_recent_calibration_voltage()
        if calibration_ph:
            self.show_most_recent_calibration_ph()
        if voltage:
            self.show_most_recent_measurement_voltage()
        if ph:
            self.show_most_recent_measurement_ph()

    @unpack_namespace
    def generate_conversion_info(self, measurement_id: str):
        self.storage.calculate_ph(measurement_id, write_data = True)

    def show_most_recent_calibration_ph(self):
        calibration_ph = self.storage.get_most_recent_calibration_ph()
        print(f"Showing the pH value being stored for the most recent calibration run. To see the associated voltages, use 'show -c'.")
        calibration_values = self.storage.get_most_recent_calibration()
        print(ElectrodeNames.electrode_ascii_art([f"{calibration_ph:.2f}" if val is not None else None for val in calibration_values]))

    def show_most_recent_calibration_voltage(self):
        calibration_ph = self.storage.get_most_recent_calibration_ph()
        print(f"Showing voltages from the most recent calibration run in Volts. The pH value was {calibration_ph:.2f}.")
        calibration_values = self.storage.get_most_recent_calibration()
        print(ElectrodeNames.electrode_ascii_art([f"{val:.2f}V" if val is not None else None for val in calibration_values]))

    def show_most_recent_measurement_voltage(self):
        print(f"Showing voltages from the most recent measurement in Volts. To see the calculated pH values, use 'show -p'.")
        voltage_values = self.storage.get_most_recent_measurement()
        print(ElectrodeNames.electrode_ascii_art([f"{val:.2f}V" if val is not None else None for val in voltage_values]))

    def show_most_recent_measurement_ph(self):
        print(f"Showing pH values from the most recent measurement in pH units. To see the associated voltages, use 'show -v'.")
        ph_values = self.storage.get_most_recent_ph()
        print(ElectrodeNames.electrode_ascii_art([f"{val:.2f}" if val is not None else None for val in ph_values]))
