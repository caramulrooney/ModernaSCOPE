import pandas as pd
import datetime as dt
from pytz import timezone
import dateutil.parser
import operator
from config import N_ELECTRODES, Config, StorageWritePermissionError
from os.path import exists
from uuid import uuid4
from typing import Optional
import numpy as np
from pathlib import Path

class Storage():
    my_tz = timezone('US/Eastern')
    max_calibration_time = dt.timedelta(hours = 12)
    ph_epsilon = 0.5

    def __init__(self):
        self.calibration_data_filename = Config.calibration_data_filename
        self.sensor_data_filename = Config.sensor_data_filename
        self.ph_data_filename = Config.ph_data_filename
        self.calibration_map_folder = Config.calibration_map_folder

        if exists(self.calibration_data_filename):
            self.calibration_data = pd.read_csv(
                self.calibration_data_filename,
                parse_dates = ["timestamp"],
            ).set_index("timestamp")
        else:
            self.calibration_data = self.make_calibration_data_file()

        if exists(self.sensor_data_filename):
            self.sensor_data = pd.read_csv(
                self.sensor_data_filename,
                parse_dates = ["timestamp"],
            ).set_index("timestamp")
        else:
            self.sensor_data = self.make_sensor_data_file()

        if exists(self.ph_data_filename):
            self.ph_data = pd.read_csv(
                self.ph_data_filename,
                parse_dates = ["timestamp"],
            ).set_index("timestamp")
        else:
            self.ph_data = self.make_ph_data_file()

        self.calibration_map: dict[str: list[str]] = {} # placeholder; will be overwritten by self.calculate_ph()


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

    def add_calibration(self, ph: float, voltages: list[Optional[float]], write_data: bool = True) -> str:
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
        self.calibration_map = {}
        if write_data:
            self.write_data()
        return str(guid)

    def add_measurement(self, voltages: list[Optional[float]], write_data: bool = True) -> str:
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

        if write_data:
            self.write_data()
        return str(guid)

    def write_data(self):
        try:
            self.calibration_data.to_csv(self.calibration_data_filename)
            self.sensor_data.to_csv(self.sensor_data_filename)
            self.ph_data.to_csv(self.ph_data_filename)

            if len(self.calibration_map) == 0:
                # after a calibration or some other operation which left self.calibration_map empty, erase the file
                calibration_map_df = pd.DataFrame()
                return

            calibration_map_df = self.calibration_map_to_dataframe(self.calibration_map)
            calibration_map_guid = calibration_map_df.index.name
            calibration_map_ts = self.sensor_data[self.sensor_data["guid"] == calibration_map_guid].index[0]
            calibration_map_name = f"{calibration_map_ts.strftime('%Y_%m_%d_%H_%M_%S_%f')}_Measurement_ID_({calibration_map_guid}).csv"
            # calibration_map_name = f"2024-03-20:50.5g.csv"# GUID( {calibration_map_guid} ).csv"
            print("Calibration map name is ")
            print(calibration_map_name)
            calibration_map_path = Path(self.calibration_map_folder) / calibration_map_name
            calibration_map_df.to_csv(str(calibration_map_path), index = False)

        except PermissionError:
            # bump it to the top level program
            raise StorageWritePermissionError

    def calibration_map_to_dataframe(self, calibration_map) -> pd.DataFrame:
        # convert calibration_map into a dataframe by normalizing the lengths of all of its arrays
        print(calibration_map)
        measurement_guid = calibration_map["measurement_guid"]
        calibration_map_no_guid = dict(calibration_map) # make a copy so we can delete the guid entry
        del calibration_map_no_guid["measurement_guid"]

        max_len = max([len(val) for key, val in calibration_map_no_guid.items()])
        normalized_len_calibration_map = {key: sorted(val) + [None] * (max_len - len(val)) for key, val in calibration_map_no_guid.items()}
        calibration_map_df = pd.DataFrame(normalized_len_calibration_map)
        # print(calibration_map_df)
        # print(calibration_map_df.eq(calibration_map_df.iloc[:, 0], axis = "index"))
        # print(calibration_map_df.eq(calibration_map_df.iloc[:, 0], axis = "index").all(axis = "columns"))
        # calibration_map_df.insert(loc = 0, column = "all_guids_equal",
        #     value = calibration_map_df.eq(calibration_map_df.iloc[:, 0], axis = "index").all(axis = "columns")
        # )
        # print(calibration_map_df)
        pivoted_df = self.pivot_calibration_map_df(calibration_map_df)
        pivoted_df.index.rename(measurement_guid, inplace = True)
        pivoted_df.insert(loc = 1, column = "All electrodes", value = pivoted_df.all(axis = "columns"))

        return pivoted_df

    def pivot_calibration_map_df(self, calibration_map_df: pd.DataFrame) -> pd.DataFrame:
        pivoted_df = calibration_map_df.iloc[0:0]
        # print(pivoted_df)
        unique_guids = pd.melt(calibration_map_df)["value"].unique()
        # new_row_df = pd.DataFrame(new_row_values).dropna(axis = "columns").set_index("timestamp")
        # self.sensor_data = pd.concat([self.sensor_data if not self.sensor_data.empty else None, new_row_df], axis = "index")

        # print(unique_guids)

        for guid in unique_guids:
            if guid is None:
                continue
            new_row_df = pd.DataFrame(calibration_map_df.eq(guid).any(axis = "index")).T
            new_row_df.insert(loc = 0, column = "Calibration ID", value = guid)
            pivoted_df = pd.concat([pivoted_df if not pivoted_df.empty else None, new_row_df], axis = "index")
        return pivoted_df


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
            if self.is_close_to_another_ph(ph_list, row["ph"]) or pd.isna(row["voltage"]):
                df.drop(index = index, inplace = True)
            else:
                ph_list.append(row["ph"])
        return df

    def calibration_list_to_ph(self, calibration_list: pd.DataFrame, measured_voltage: float) -> float:
        df = calibration_list.copy().sort_values("ph", ascending = True)
        if not np.all(np.diff(df["voltage"])):
            print(f"WARNING: Calibration voltages are not monotonic with pH. It is strongly suggested that you re-calibrate the sensor. Check the file {self.calibration_data_filename} to see details of the calibrations or to flag certain calibrations as invalid.")
        return np.interp(measured_voltage, df["voltage"], df["ph"])

    def calculate_ph(self, measurement_guid: str, write_data: bool = False) -> str:
        relevant_calibration_data = self.get_relevant_calibration_data(measurement_guid)
        measurement_df = self.sensor_data[self.sensor_data["guid"] == measurement_guid]
        assert len(measurement_df.index) == 1
        self.calibration_map["measurement_guid"] = measurement_guid

        new_row_values = {
            "timestamp": measurement_df.index[0],
            "guid": measurement_guid,
        }

        guids_all_the_same = True
        prev_guids = pd.Series()
        for i, electrode_id in enumerate(range(N_ELECTRODES)):
            if all(pd.isna(relevant_calibration_data[f"V_calibration_{electrode_id}"])):
                new_row_values[f"ph_electrode_{electrode_id}"] = None
                continue
            calibration_list = self.calibration_list_for_electrode(electrode_id, relevant_calibration_data)
            ph = self.calibration_list_to_ph(calibration_list, measurement_df[f"V_electrode_{electrode_id}"])
            new_row_values[f"ph_electrode_{electrode_id}"] = ph

            # check if all calibrations were performed with the same set of GUIDs
            if i > 0:
                self.calibration_map[f"electrode_{electrode_id}"] = calibration_list["guid"].to_list()
                compare_guids = prev_guids.reset_index().equals(calibration_list["guid"].reset_index())
                if not compare_guids:
                    print("Guids are not all the same!")
                    guids_all_the_same = False
            prev_guids = calibration_list["guid"]

        if not guids_all_the_same:
            print(f"WARNING: Using different calibration data points for different measurements. Please review the file {self.calibration_data_filename} to see details of the calibrations or to flag certain calibrations as invalid.")

        new_row_df = pd.DataFrame(new_row_values).dropna(axis = "columns").set_index("timestamp")
        self.ph_data = pd.concat([self.ph_data if not self.ph_data.empty else None, new_row_df], axis = "index")
        if write_data:
            self.write_data()
        return measurement_guid

    def get_most_recent_calibration_ph(self) -> float:
        last_row = self.calibration_data.sort_index(ascending = True).tail(1)
        calibration_ph = last_row["calibration_ph"].iloc[0]
        return calibration_ph

    def get_most_recent_calibration(self) -> list[Optional[float]]:
        last_row = self.calibration_data.sort_index(ascending = True).tail(1)
        calibration_values = []
        for electrode_id in range(N_ELECTRODES):
            calibration_value = last_row[f"V_calibration_{electrode_id}"].iloc[0]
            calibration_values.append(calibration_value if pd.notna(calibration_value) else None)
        return calibration_values

    def get_most_recent_measurement(self) -> list[Optional[float]]:
        last_row = self.sensor_data.sort_index(ascending = True).tail(1)
        voltage_values = []
        for electrode_id in range(N_ELECTRODES):
            voltage_value = last_row[f"V_electrode_{electrode_id}"].iloc[0]
            voltage_values.append(voltage_value if pd.notna(voltage_value) else None)
        return voltage_values

    def get_most_recent_ph(self) -> list[Optional[float]]:
        last_row = self.ph_data.sort_index(ascending = True).tail(1)
        ph_values = []
        for electrode_id in range(N_ELECTRODES):
            ph_value = last_row[f"ph_electrode_{electrode_id}"].iloc[0]
            ph_values.append(ph_value if pd.notna(ph_value) else None)
        return ph_values
