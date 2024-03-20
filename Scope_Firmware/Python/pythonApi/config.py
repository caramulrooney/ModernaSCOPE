from enum import Enum
import json

class Config():
    calibration_data_filename = "sensor_data/calibration_data.csv"
    sensor_data_filename = "sensor_data/sensor_data.csv"
    ph_data_filename = "sensor_data/ph_data.csv"
    calibration_map_filename = "sensor_data/calibration_map.csv"
    debug = False

    @classmethod
    def set_config(cls, config_filename):
        try:
            f = open(config_filename)
        except FileNotFoundError:
            print(f"Could not open file {config_filename}. Using default configuration settings instead.")
            return

        data = json.load(f)
        if "calibration_data_filename" in data.keys():
            cls.calibration_data_filename = data["calibration_data_filename"]
        if "sensor_data_filename" in data.keys():
            cls.sensor_data_filename = data["sensor_data_filename"]
        if "ph_data_filename" in data.keys():
            cls.ph_data_filename = data["ph_data_filename"]
        if "calibration_map_filename" in data.keys():
            cls.calibration_map_filename = data["calibration_map_filename"]
        if "debug" in data.keys():
            cls.debug = data["debug"]

class StorageWritePermissionError(PermissionError):
    """
    PermissionError that specifically came from the Storage.write_data() function. This needs its own error type because the top-level program needs to know which function to call back when it receives such an error.
    """

N_ELECTRODES = 96
N_COLUMNS = 12
N_ROWS = 8
ROW_LETTERS = "ABCDEFGH"
COL_NUMBERS = "0123456789"
ALL_ELECTRODES_KEYWORD = "all"

class SelectionType(Enum):
    ROW_WISE = 0
    COLUMN_WISE = 1
    EXCEL_LIKE = 2

init_text_art = """

___  ___      _ _   _       _              ______ _   _     _____
|  \/  |     | | | (_)     | |             | ___ \ | | |   /  ___|
| .  . |_   _| | |_ _ _ __ | | _____  __   | |_/ / |_| |   \ `--.  ___ _ __  ___  ___  _ __
| |\/| | | | | | __| | '_ \| |/ _ \ \/ /   |  __/|  _  |    `--. \/ _ \ '_ \/ __|/ _ \| '__|
| |  | | |_| | | |_| | |_) | |  __/>  <    | |   | | | |   /\__/ /  __/ | | \__ \ (_) | |
\_|  |_/\__,_|_|\__|_| .__/|_|\___/_/\_\   \_|   \_| |_/   \____/ \___|_| |_|___/\___/|_|
                     | |
                     |_|

"""
