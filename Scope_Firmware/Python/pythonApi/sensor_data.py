import pandas as pd
import datetime as dt
from pytz import timezone
from config import Config
from constants import N_ELECTRODES, MIN_CALIBRATIONS_RECOMMENDED
import constants
from os.path import exists
from uuid import uuid4
from typing import Optional
import numpy as np
from pathlib import Path

class DataWritePermissionError(PermissionError):
    """
    PermissionError that specifically came from the SensorData.write_data() function. This needs its own error type because the top-level program needs to know which function to call back when it receives such an error.
    """
class CalibrationError(Exception):
    """
    Too few calibrations exist to meaningfully convert the data.
    """

class SensorData():
    def __init__(self):
        """
        Initialize CSV files for permanent data storage, or load their contents into memory if they exist.

        `calibration_data_filename`: CSV file to store a historical record of every calibration that has been performed. Only calibrations more recent than 12 hours will be used. There is also a field in the CSV file called `is_valid`; use this to mark calibration attempts that should be ignored without deleting rows from the table. Each calibration has a unique GUID and a timestamp associated with it.

        `measurement_data_filename`: CSV file to store a historical record of every measurement that has been performed. Only the raw measured voltage is stored in this file. The voltages can be converted into pH values in post-processing (and indeed, this processing is dones automatically and stored in a separate file called `ph_result_filename`. Each voltage measurement has a unique GUID and a timestamp associated with it.

        `ph_result_filename`: CSV file containing the pH values at each electrode that have been calculated during post-processing of the electrode voltages in `measurement_data_filename`. The GUID and timestamp of each entry in `ph_result_filename` is shared with a row in that table.

        `calibration_map_folder`: A calibration map is a CSV file documenting which calibration data points were used to calculate the pH of a given measurement. Each time a measurement is converted into a pH, a new file is created in this folder with a name consisting of a timestamp and a GUID corresponding to the measurement ID.
        """
        self.calibration_data_filename = Config.calibration_data_filename
        self.measurement_data_filename = Config.measurement_data_filename
        self.ph_result_filename = Config.ph_result_filename
        self.calibration_map_folder = Config.calibration_map_folder

        if exists(self.calibration_data_filename):
            self.calibration_data = pd.read_csv(
                self.calibration_data_filename,
                parse_dates = ["timestamp"],
            ).set_index("timestamp")
        else:
            self.calibration_data = self.make_calibration_data_file()

        if exists(self.measurement_data_filename):
            self.measurement_data = pd.read_csv(
                self.measurement_data_filename,
                parse_dates = ["timestamp"],
            ).set_index("timestamp")
        else:
            self.measurement_data = self.make_measurement_data_file()

        if exists(self.ph_result_filename):
            self.ph_result = pd.read_csv(
                self.ph_result_filename,
                parse_dates = ["timestamp"],
            ).set_index("timestamp")
        else:
            self.ph_result = self.ph_result_data_file()

        self.calibration_map: dict[str: list[str]] = {} # placeholder; will be overwritten by self.calculate_ph()


    def make_calibration_data_file(self) -> pd.DataFrame:
        """
        Initialize a dataframe to hold calibration data, including columns for metadata and one column for the voltage at each electrode during calibration. Return the empty dataframe.
        """
        columns = [
            "timestamp",
            "guid",
            "calibration_ph",
            "is_valid",
            "invalid_reason",
        ]
        columns.extend([f"V_calibration_{i}" for i in range(N_ELECTRODES)])
        return pd.DataFrame(columns = columns).set_index("timestamp")

    def make_measurement_data_file(self) -> pd.DataFrame:
        """
        Initialize a dataframe to hold measurement data, including columns for metadata and one column for the voltage at each electrode during the measurement. Return the empty dataframe.
        """
        columns = [
            "timestamp",
            "guid",
        ]
        columns.extend([f"V_electrode_{i}" for i in range(N_ELECTRODES)])
        return pd.DataFrame(columns = columns).set_index("timestamp")

    def ph_result_data_file(self) -> pd.DataFrame:
        """
        Initialize a dataframe to hold pH data, including columns for metadata and one column for the pH at each electrode resulting from the voltage-to-pH conversion. Return the empty dataframe.
        """
        columns = [
            "timestamp",
            "guid",
        ]
        columns.extend([f"ph_electrode_{i}" for i in range(N_ELECTRODES)])
        return pd.DataFrame(columns = columns).set_index("timestamp")

    def add_calibration(self, ph: float, voltages: list[Optional[float]], write_data: bool = True) -> str:
        """
        Insert a new row in self.calibration_data with the given pH value and a list of electrode voltages. Electrode voltages should be passed as a list of 96 numbers, with None for the electrodes that are excluded. Create the necessary metadata for the record, including a unique GUID and timestamp. Automatically write the new row to the CSV file `calibration_data_filename` unless `write_data` is set to `False`.
        """
        assert(len(voltages) == N_ELECTRODES)
        timestamp = dt.datetime.now(tz = timezone(Config.timezone))
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
        """
        Insert a new row in self.measurement_data with a list of electrode voltages. Electrode voltages should be passed as a list of 96 numbers, with None for the electrodes that are excluded. Create the necessary metadata for the record, including a unique GUID and timestamp. Automatically write the new row to the CSV file `measurement_data_filename` unless `write_data` is set to `False`. Automatically call self.calculate_ph() to insert a corresponding row in self.ph_result and write that to the CSV file `ph_result_filename` as well.
        """
        assert(len(voltages) == N_ELECTRODES)
        timestamp = dt.datetime.now(tz = timezone(Config.timezone))
        guid = uuid4()

        new_row_values = {
            "timestamp": timestamp,
            "guid": str(guid),
        }
        new_row_values.update({f"V_electrode_{i}": [voltages[i]] for i in range(N_ELECTRODES)})

        new_row_df = pd.DataFrame(new_row_values).dropna(axis = "columns").set_index("timestamp")
        self.measurement_data = pd.concat([self.measurement_data if not self.measurement_data.empty else None, new_row_df], axis = "index")
        self.calculate_ph(str(guid))

        if write_data:
            self.write_data()
        return str(guid)

    def write_data(self):
        """
        Write calibration data, measurement data, and converted pH data stored in memory to their respective CSV files. For the calibration map file, create a new file name by combining the timestamp and the measurement guid of the measurement being converted.

        In case of a PermissionError, which occurs when one of the required files is open in another program, raise a DataWritePermissionError which is handled by the top-level prompt script to ask the user to close the other program and retry.
        """
        try:
            self.calibration_data.to_csv(self.calibration_data_filename)
            self.measurement_data.to_csv(self.measurement_data_filename)
            self.ph_result.to_csv(self.ph_result_filename)

            if len(self.calibration_map) == 0:
                # after a calibration or some other operation which left self.calibration_map empty, erase the file
                calibration_map_df = pd.DataFrame()
                return

            calibration_map_df = self.calibration_map_to_dataframe(self.calibration_map)
            calibration_map_guid = calibration_map_df.index.name
            calibration_map_ts = self.measurement_data[self.measurement_data["guid"] == calibration_map_guid].index[0]
            calibration_map_name = f"{calibration_map_ts.strftime('%Y_%m_%d_%H_%M_%S_%f')}_Measurement_ID_({calibration_map_guid}).csv"
            if Config.debug.cli.feedback.write_data:
                print(f"Storing calibration map in file: {calibration_map_name}")
            calibration_map_path = Path(self.calibration_map_folder) / calibration_map_name
            calibration_map_df.to_csv(str(calibration_map_path), index = False)

        except PermissionError:
            # bump it to the top level program
            raise DataWritePermissionError

    def calibration_map_to_dataframe(self, calibration_map: dict[str: list[str]]) -> pd.DataFrame:
        """
        Convert conversion data into the desired format for the calibration map CSV file.

        In the conversion process, a list of calibration data points are used in the calculation of each electrode, and this list may be different depending on the calibration history for each electrode. For example, if a more recent calibration were performed but only on a subset of the electrodes, then the rest of the electrodes would use the older calibration data, provided it was still valid (taken less than 12 hours prior).

        Take in a dictionary which maps each electrode id to the list of calibration guids used in its conversion, and convert it into a row-wise boolean dataframe, where each row is a unique calibration guid, each column is a different electrode, and the cells are true or false based on whether that calibration guid was used in conversion of that electrode.

        Also include other metadata, such as whether a certain calibration guid was used for all electrodes or only some of them. The index.name property is the assigned to be guid of the measurement being converted. This is a convenient way to pass this data out of hte function rather than returning a tuple.

        Input example:
        ```
        {
            'measurement_guid': 'my_measurement_guid',
            'electrode_1': [cal_guid 1],
            'electrode_2': [cal_guid 1],
            ... ,
            'electrode_95': [cal_guid 2, cal_guid 1]
        }
        ```

        Output example:
        ```
                               Calibration ID  Calibration pH  ...  electrode_94  electrode_95
        'my_measurement_guid'
              (as index name)
        0                          cal_guid 2             8.0  ...         False          True
        0                          cal_guid 1             5.0  ...          True          True
        ```
        """
        # extract the measurement guid and remove it from the dictionary
        measurement_guid = calibration_map["measurement_guid"]
        calibration_map_no_guid = dict(calibration_map) # make a copy so we can delete the guid entry
        del calibration_map_no_guid["measurement_guid"]

        # convert calibration_map into a dataframe by normalizing the lengths of all of its arrays
        max_len = max([len(val) for key, val in calibration_map_no_guid.items()])
        normalized_len_calibration_map = {key: sorted(val) + [None] * (max_len - len(val)) for key, val in calibration_map_no_guid.items()}
        calibration_map_df = pd.DataFrame(normalized_len_calibration_map)

        # convert to row-wise boolean dataframe for saving
        pivoted_df = self.pivot_calibration_map_df(calibration_map_df)
        pivoted_df.index.rename(measurement_guid, inplace = True)
        pivoted_df.insert(loc = 2, column = "All electrodes", value = pivoted_df.all(axis = "columns"))

        return pivoted_df

    def pivot_calibration_map_df(self, calibration_map_df: pd.DataFrame) -> pd.DataFrame:
        """
        Intermediate function to break up `self.calibration_map_to_dataframe`. Take in a dataframe where each column contains the list of the calibration ids used in the conversion of that measurement (padded with None so all columns have the same length), and return a row-wise boolean dataframe where each row is a unique calibration guid, each column is a different electrode, and the cells are true or false based on whether that calibration guid was used in conversion of that electrode.

        Input example:
        ```
           electrode_1  electrode_2  electrode_3  ...  electrode_95
        0   cal_guid_1   cal_guid_1   cal_guid_1  ...    cal_guid_1
        1         None         None         None  ...    cal_guid_2
        ```

        Output example:
        ```
           Calibration ID  Calibration pH  electrode_1  electrode_2  ...  electrode_95
        0      cal_guid_1             5.0         True         True  ...          True
        0      cal_guid_2             8.0        False        False  ...          True
        ```
        """
        pivoted_df = calibration_map_df.iloc[0:0]
        unique_guids = pd.melt(calibration_map_df)["value"].unique()

        if Config.debug.sensor_data.pivot:
            print(unique_guids)

        for guid in unique_guids:
            if guid is None:
                continue
            new_row_df = pd.DataFrame(calibration_map_df.eq(guid).any(axis = "index")).T
            new_row_df.insert(loc = 0, column = "Calibration pH",
                value = self.calibration_data[self.calibration_data["guid"] == guid]["calibration_ph"].iloc[0]
            )
            new_row_df.insert(loc = 0, column = "Calibration ID", value = guid)
            pivoted_df = pd.concat([pivoted_df if not pivoted_df.empty else None, new_row_df], axis = "index")
        return pivoted_df


    def get_relevant_calibration_data(self, measurement_guid: str) -> pd.DataFrame:
        """
        Filter stored calibration data and return relevant rows.
        Relevant calibration data must
        1) be valid (the `is_valid` flag is set to `True`), meaning it has not been dropped by the user
        2) have been collected prior to the time of the measurement in question, and
        3) have been collected no more than 12 hours before the measurement for the calibration to be valid.

        Return a dataframe containing the relevant rows of the calibration data table.
        """
        measurement_df = self.measurement_data[self.measurement_data["guid"] == measurement_guid]
        measurement_ts =  measurement_df.index[0]
        relevant_calibration_data = self.calibration_data[
            (self.calibration_data.index < measurement_ts) &
            (self.calibration_data.index > measurement_ts - constants.MAX_CALIBRATION_TIME) &
            (self.calibration_data["is_valid"])
        ]
        return relevant_calibration_data

    def is_close_to_another_ph(self, ph_list: list[float], ph: float):
        """
        Given a list of the most recent pH calibration values, determine if an older calibration pH value is close enough to any of the more recent values to be considered a duplicate. For example, if there are more recent pH calibration values of 4 and 7, then pH values of 4.1 or 7.1 would be considered duplicates, whereas a pH value of 10 would be accepted.
        """
        return any(abs(np.array(ph_list) - ph) < constants.PH_EPSILON)

    def calibration_list_for_electrode(self, electrode_id: int, relevant_calibration_data: pd.DataFrame) -> pd.DataFrame:
        """
        For a single electrode, filter the calibration data to contain only the most recent calibration data point at each pH. For example, if there are multiple calibrations that occurred at ph 7, select only the most recent one. Calibration values with very similar pH (such as 7 and 7.1) will be treated as the same and only the most recent one will be used. `self.is_close_to_another_ph()` determines what qualifies as similar enough to be a duplicate calibration.

        Return a dataframe containing only the non-duplicate rows of the calibration data table.
        """
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
        """
        Given a dataframe representing the pH and voltage of the most recent calibration data at a single electrode, calculate the pH value for a new voltage measurement at that electrode. Return the pH value.
        """
        df = calibration_list.copy().sort_values("ph", ascending = True)
        if not np.all(np.diff(df["voltage"])):
            print(f"WARNING: Calibration voltages are not monotonic with pH. It is strongly suggested that you re-calibrate the sensor. Check the file {self.calibration_data_filename} to see details of the calibrations or to flag certain calibrations as invalid.")
        return np.interp(measured_voltage, df["voltage"], df["ph"])

    def calculate_ph(self, measurement_guid: str, write_data: bool = False) -> str:
        """
        Insert a new row in self.ph_result using measurement data corresponding to `measurement_guid`. Since this function is normally called from `self.add_measurement()` which takes care of writing data, this function does not write to a file automatically unless `write_data` is set to `True`.
        """
        relevant_calibration_data = self.get_relevant_calibration_data(measurement_guid)
        if len(relevant_calibration_data.index) < MIN_CALIBRATIONS_RECOMMENDED:
            print(f"WARNING: Fewer than {MIN_CALIBRATIONS_RECOMMENDED} valid calibration points are available (calibrations are only valid for 12 hours and may be invalidated for other reasons). It is strongly suggested that you re-calibrate the sensor.")
        if len(relevant_calibration_data.index) <= 0:
            raise CalibrationError("No valid calibration points are available. A pH conversion cannot occur.")

        measurement_df = self.measurement_data[self.measurement_data["guid"] == measurement_guid]
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
                    if Config.debug.sensor_data.ph_conversion.compare_guids:
                        print("Guids are not all the same!")
                    guids_all_the_same = False
            prev_guids = calibration_list["guid"]

        if not guids_all_the_same:
            print(f"WARNING: Using different calibration data points for different measurements. Please review the file {self.calibration_data_filename} to see details of the calibrations or to flag certain calibrations as invalid.")

        new_row_df = pd.DataFrame(new_row_values).dropna(axis = "columns").set_index("timestamp")
        self.ph_result = pd.concat([self.ph_result if not self.ph_result.empty else None, new_row_df], axis = "index")
        if write_data:
            self.write_data()
        return measurement_guid

    def get_most_recent_calibration_ph(self) -> float:
        """
        Return the pH value of the most recent calibration.
        """
        last_row = self.calibration_data.sort_index(ascending = True).tail(1)
        calibration_ph = last_row["calibration_ph"].iloc[0]
        return calibration_ph

    def get_most_recent_calibration(self) -> list[Optional[float]]:
        """
        Return a list of the voltages at each electrode for the most recent calibration. For excluded electrodes, the corresponding entry is None.
        """
        last_row = self.calibration_data.sort_index(ascending = True).tail(1)
        calibration_values = []
        for electrode_id in range(N_ELECTRODES):
            calibration_value = last_row[f"V_calibration_{electrode_id}"].iloc[0]
            calibration_values.append(calibration_value if pd.notna(calibration_value) else None)
        return calibration_values

    def get_most_recent_measurement(self) -> list[Optional[float]]:
        """
        Return a list of the voltages at each electrode for the most recent measurement. For excluded electrodes, the corresponding entry is None.
        """
        last_row = self.measurement_data.sort_index(ascending = True).tail(1)
        voltage_values = []
        for electrode_id in range(N_ELECTRODES):
            voltage_value = last_row[f"V_electrode_{electrode_id}"].iloc[0]
            voltage_values.append(voltage_value if pd.notna(voltage_value) else None)
        return voltage_values

    def get_most_recent_ph(self) -> list[Optional[float]]:
        """
        Return a list of the pH values at each electrode for the most recent conversion. For excluded electrodes, the corresponding entry is None.
        """
        last_row = self.ph_result.sort_index(ascending = True).tail(1)
        ph_values = []
        for electrode_id in range(N_ELECTRODES):
            ph_value = last_row[f"ph_electrode_{electrode_id}"].iloc[0]
            ph_values.append(ph_value if pd.notna(ph_value) else None)
        return ph_values
