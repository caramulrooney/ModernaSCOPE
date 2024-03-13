import inspect
from storage import Storage
from numpy.random import rand
import constants
from constants import N_ELECTRODES
from electrode_names import ElectrodeNames

def unpack_namespace(func):
    def inner(self, namespace):
        sig = inspect.signature(func)
        kwargs = vars(namespace)
        kwargs["self"] = self
        args_to_pass = [kwargs[arg] for arg in sig.parameters.keys()]
        func(*args_to_pass)
    return inner

def parse_battleship_notation(self, battleship):
    return [0, 1, 2, 3, 4]

class Sensor():
    calibrations = []
    measurement_in_progress = False

    def __init__(self):
        self.storage = Storage(
            calibration_data_filename = "Scope_Firmware/Python/pythonApi/sensor_data/calibration_data.csv",
            sensor_data_filename = "Scope_Firmware/Python/pythonApi/sensor_data/sensor_data.csv"
        )

    def get_voltages(self): # TODO: get data from sensor via pySerial
        return rand(1, N_ELECTRODES)

    @unpack_namespace
    def measure(self, electrodes, now, time_steps, max_time, voltage_only):
        print(f"Inside of measure, {electrodes=}, {now=}, {time_steps=}, {max_time=}, {voltage_only=}")
        voltages = self.get_voltages()
        electrode_ids = ElectrodeNames.parse_electrode_input(electrodes)
        print(ElectrodeNames.to_battleship_notation(electrode_ids))


    @unpack_namespace
    def calibrate(self, electrodes, ph):
        print(f"Inside of calibrate, {electrodes=}, {ph=}")
        voltages = self.get_voltages()
        electrode_ids = self.parse_battleship_notation(electrodes)
        for i in electrode_ids:
            self.calibrations[i].add_calibration(ph, voltages[i])

    @unpack_namespace
    def show_calibration(self, electrodes, ph, sort_by_ph):
        print(f"Inside of calibrate, {electrodes=}, {ph=}, {sort_by_ph=}")
        electrode_ids = self.parse_battleship_notation(electrodes)
        for i in electrode_ids:
            print(f"Electrode {i}: {self.calibrations[i].get_recent_calibrations()[0]}")

    @unpack_namespace
    def clear_calibration(self, electrodes, ph, all):
        print(f"Inside of calibrate, {electrodes=}, {ph=}, {all=}")
