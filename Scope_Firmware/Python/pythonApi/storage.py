import pandas as pd
import datetime as dt
from pytz import timezone
import operator
from constants import N_ELECTRODES
from os.path import exists
from uuid import uuid4
from typing import Optional

class Storage():
    my_tz = timezone('US/Eastern')
    max_calibration_time = dt.timedelta(hours = 12)

    def __init__(self, calibration_data_filename: str, sensor_data_filename: str):
        self.calibration_data_filename = calibration_data_filename
        self.sensor_data_filename = sensor_data_filename

        if exists(calibration_data_filename):
            self.calibration_data = pd.read_csv(calibration_data_filename)
        else:
            self.calibration_data = self.make_calibration_data_file()
        if exists(sensor_data_filename):
            self.sensor_data = pd.read_csv(sensor_data_filename)
        else:
            self.sensor_data = self.make_sensor_data_file()

    def make_calibration_data_file(self) -> pd.DataFrame:
        columns = [
            "timestamp",
            "guid",
            "calibration_ph",
            "is_valid",
            "invalid_reason",
        ]
        columns.extend([f"V_calibration_{i}" for i in range(N_ELECTRODES)])
        return pd.DataFrame(columns = columns).set_index("timestamp")

    def make_sensor_data_file(self) -> pd.DataFrame:
        columns = [
            "timestamp",
            "guid",
        ]
        columns.extend([f"V_electrode_{i}" for i in range(N_ELECTRODES)])
        return pd.DataFrame(columns = columns).set_index("timestamp")

    def add_calibration(self, ph: float, voltages: list[Optional[float]]):
        assert(len(voltages) == N_ELECTRODES)
        timestamp = dt.datetime.now(tz = self.my_tz)
        guid = uuid4()

        new_row_values = {
            "timestamp": str(timestamp),
            "guid": str(guid),
            "calibration_ph": ph,
            "is_valid": True,
            "invalid_reason": "",
        }
        new_row_values.update({f"V_calibration_{i}": [voltages[i]] for i in range(N_ELECTRODES)})
        new_row = pd.DataFrame(new_row_values)

        self.calibration_data = pd.concat([self.calibration_data, new_row], axis = "index", ignore_index = True)

    def add_measurement(self, voltages: list[Optional[float]]):
        assert(len(voltages) == N_ELECTRODES)
        timestamp = dt.datetime.now(tz = self.my_tz)
        guid = uuid4()

        new_row_values = {
            "timestamp": str(timestamp),
            "guid": str(guid),
        }
        new_row_values.update({f"V_electrode_{i}": [voltages[i]] for i in range(N_ELECTRODES)})
        new_row = pd.DataFrame(new_row_values)

        self.sensor_data = pd.concat([self.sensor_data, new_row], axis = "index", ignore_index = True)

    def write_data(self):
        self.calibration_data.set_index("timestamp").to_csv(self.calibration_data_filename)
        self.sensor_data.set_index("timestamp").to_csv(self.sensor_data_filename)
