import pandas as pd
import datetime as dt
from pytz import timezone
import dateutil.parser
import operator
from constants import N_ELECTRODES
from os.path import exists
from uuid import uuid4
from typing import Optional
import numpy as np

class Storage():
    my_tz = timezone('US/Eastern')
    max_calibration_time = dt.timedelta(hours = 12)
    ph_epsilon = 0.5

    def __init__(self, calibration_data_filename: str, sensor_data_filename: str, ph_data_filename):
        self.calibration_data_filename = calibration_data_filename
        self.sensor_data_filename = sensor_data_filename
        self.ph_data_filename = ph_data_filename

        if exists(calibration_data_filename):
            self.calibration_data = pd.read_csv(
                calibration_data_filename,
                parse_dates = ["timestamp"],
            ).set_index("timestamp")
        else:
            self.calibration_data = self.make_calibration_data_file()

        if exists(sensor_data_filename):
            self.sensor_data = pd.read_csv(
                sensor_data_filename,
                parse_dates = ["timestamp"],
            ).set_index("timestamp")
        else:
            self.sensor_data = self.make_sensor_data_file()

        if exists(ph_data_filename):
            self.ph_data = pd.read_csv(
                ph_data_filename,
                parse_dates = ["timestamp"],
            ).set_index("timestamp")
        else:
            self.ph_data = self.make_ph_data_file()


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

    def make_ph_data_file(self) -> pd.DataFrame:
        columns = [
            "timestamp",
            "guid",
        ]
        columns.extend([f"ph_electrode_{i}" for i in range(N_ELECTRODES)])
        return pd.DataFrame(columns = columns).set_index("timestamp")

    def add_calibration(self, ph: float, voltages: list[Optional[float]]) -> str:
        assert(len(voltages) == N_ELECTRODES)
        timestamp = dt.datetime.now(tz = self.my_tz)
        guid = uuid4()

        new_row_values = {
            "timestamp": timestamp,
            "guid": str(guid),
            "calibration_ph": ph,
            "is_valid": True,
            "invalid_reason": "",
        }
        new_row_values.update({f"V_calibration_{i}": [voltages[i]] for i in range(N_ELECTRODES)})

        new_row_df = pd.DataFrame(new_row_values).dropna(axis = "columns").set_index("timestamp")
        self.calibration_data = pd.concat([self.calibration_data if not self.calibration_data.empty else None, new_row_df], axis = "index")
        self.write_data()
        return str(guid)

    def add_measurement(self, voltages: list[Optional[float]]) -> str:
        assert(len(voltages) == N_ELECTRODES)
        timestamp = dt.datetime.now(tz = self.my_tz)
        guid = uuid4()

        new_row_values = {
            "timestamp": timestamp,
            "guid": str(guid),
        }
        new_row_values.update({f"V_electrode_{i}": [voltages[i]] for i in range(N_ELECTRODES)})

        new_row_df = pd.DataFrame(new_row_values).dropna(axis = "columns").set_index("timestamp")
        self.sensor_data = pd.concat([self.sensor_data if not self.sensor_data.empty else None, new_row_df], axis = "index")
        self.calculate_ph(str(guid))

        self.write_data()
        return str(guid)

    def write_data(self):
        self.calibration_data.to_csv(self.calibration_data_filename)
        self.sensor_data.to_csv(self.sensor_data_filename)
        self.ph_data.to_csv(self.ph_data_filename)

    def get_relevant_calibration_data(self, measurement_guid: str) -> pd.DataFrame:
        """
        Relevant calibration data must
        1) be valid (the `is_valid` flag is set to `True`), meaning it has not been dropped by the user
        2) have been collected prior to the time of the measurement in question, and
        3) have been collected no more than 12 hours before the measurement for the calibration to be valid.
        """
        measurement_df = self.sensor_data[self.sensor_data["guid"] == measurement_guid]
        measurement_ts =  measurement_df.index[0]
        relevant_calibration_data = self.calibration_data[
            (self.calibration_data.index < measurement_ts) &
            (self.calibration_data.index > measurement_ts - self.max_calibration_time) &
            (self.calibration_data["is_valid"])
        ]
        return relevant_calibration_data

    def is_close_to_another_ph(self, ph_list: list[float], ph: float):
        return any(abs(np.array(ph_list) - ph) < self.ph_epsilon)

    def calibration_list_for_electrode(self, electrode_id: int, relevant_calibration_data: pd.DataFrame) -> pd.DataFrame:
        # prepare dataframe
        df = relevant_calibration_data.copy()[["guid", "calibration_ph", f"V_calibration_{electrode_id}"]]
        df.rename(columns = {"calibration_ph": "ph", f"V_calibration_{electrode_id}": "voltage"}, inplace = True)
        df.sort_index(ascending = False, inplace = True) # reverse the values

        ph_list = []
        for index, row in df.iterrows():
            if self.is_close_to_another_ph(ph_list, row["ph"]):
                df.drop(index = index, inplace = True)
            else:
                ph_list.append(row["ph"])
        return df

    def calibration_list_to_ph(self, calibration_list: pd.DataFrame, measured_voltage: float) -> float:
        df = calibration_list.sort_values("ph", ascending = True)
        return np.interp(measured_voltage, df["voltage"], df["ph"])


    def calculate_ph(self, measurement_guid: str) -> str:
        relevant_calibration_data = self.get_relevant_calibration_data(measurement_guid)
        measurement_df = self.sensor_data[self.sensor_data["guid"] == measurement_guid]
        assert len(measurement_df.index) == 1

        new_row_values = {
            "timestamp": measurement_df.index[0],
            "guid": measurement_guid,
        }

        for electrode_id in range(N_ELECTRODES):
            if relevant_calibration_data[f"V_calibration_{electrode_id}"] is None:
                new_row_values[f"ph_electrode_{electrode_id}"] = None
                continue
            calibration_list = self.calibration_list_for_electrode(electrode_id, relevant_calibration_data)
            ph = self.calibration_list_to_ph(calibration_list, measurement_df[f"V_electrode_{electrode_id}"])
            new_row_values[f"ph_electrode_{electrode_id}"] = ph

        new_row_df = pd.DataFrame(new_row_values).dropna(axis = "columns").set_index("timestamp")
        self.ph_data = pd.concat([self.ph_data if not self.ph_data.empty else None, new_row_df], axis = "index")
        self.write_data()
        return measurement_guid
