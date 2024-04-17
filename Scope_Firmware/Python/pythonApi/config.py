import json
from pathlib import Path
from types import SimpleNamespace

class Config():
    """
    Configuration information that may need to be changed by the user, such as file paths to measurement and calibration data. Properties defined in this class are distinct from those defined in constants.py in that they might need to change from one session to the next. All properties and methods belong to the class and can be accessed without instantiation.

    Load the config parameters from a json file with set_config().

    If necessary, use make_directories() to initialize the folder structure so the data files can be created at runtime.
    """
    serial_port = "COM4"
    measurement_interval = 1 # second
    voltage_display_filename = "display/voltage_display.txt"
    calibration_data_filename = "sensor_data/calibration_data.csv"
    measurement_data_filename = "sensor_data/measurement_data.csv"
    ph_result_filename = "sensor_data/ph_result.csv"
    calibration_map_folder = "sensor_data/calibration_map/"
    prompt_history_filename = "settings/prompt_history.txt"
    timezone = "US/Eastern"
    debug = False
    random_data = True

    @classmethod
    def set_config(cls, config_filename: str, mkdirs: bool) -> bool:
        """
        Read in configuration parameters as a json file and store the relevant fields as class properties. If a field is not provided, the default value is kept. Additional fields are ignored.

        `calibration_data_filename`: File in which to store calibration records.

        `measurement_data_filename`: File in which to store measurement records.

        `ph_result_filename`: File in which to store the results of pH conversion when a measurement is performed.

        `calibration_map_folder`: Directory in which to generate a new calibration map file for each measurement that is performed, to indicate which calibration data were used in the conversion of that measurement.

        `prompt_history_filename`: File in which to store the command line session history, so that previous commands can be accessed with the up arrow even if the terminal is closed and then re-opened.

        `timezone`: Time zone in which to store calibration and measurement records.

        `debug`: If true, display a small number of additional error messages for diagnostic purposes.
        """
        try:
            f = open(config_filename)
        except FileNotFoundError:
            print(f"Could not open file '{config_filename}'. Using default configuration settings instead.")
            return False

        data = json.load(f)
        if "serial_port" in data.keys():
            cls.serial_port = data["serial_port"]
        if "measurement_interval" in data.keys():
            cls.measurement_interval = float(data["measurement_interval"])
        if "voltage_display_filename" in data.keys():
            cls.voltage_display_filename = data["voltage_display_filename"]
        if "calibration_data_filename" in data.keys():
            cls.calibration_data_filename = data["calibration_data_filename"]
        if "measurement_data_filename" in data.keys():
            cls.measurement_data_filename = data["measurement_data_filename"]
        if "ph_result_filename" in data.keys():
            cls.ph_result_filename = data["ph_result_filename"]
        if "calibration_map_folder" in data.keys():
            cls.calibration_map_folder = data["calibration_map_folder"]
        if "prompt_history" in data.keys():
            cls.prompt_history_filename = data["prompt_history_filename"]
        if "timezone" in data.keys():
            cls.timezone = data["timezone"]
        if "debug" in data.keys():
            cls.debug = data["debug"]
        if "random_data" in data.keys():
            cls.random_data = data["random_data"]

        if mkdirs:
            cls.make_directories()
        return True

    @classmethod
    def make_directories(cls):
        """
        Initialize the folder structure required by the file paths so the files can be created at runtime.
        """
        Path(cls.calibration_map_folder).mkdir(parents = True, exist_ok = True)
        for path in [cls.calibration_data_filename, cls.measurement_data_filename, cls.ph_result_filename, cls.prompt_history_filename, cls.voltage_display_filename]:
            Path(path).parent.mkdir(parents = True, exist_ok = True)

class debugNamespace(SimpleNamespace):
    def from_json(self, json_file_name):
        data = json.load(json_file_name)
        for val in data.values():
            assert isinstance(val, bool)
        self.__dict__.update(data)

    def __getitem__(self, key):
        if key in self.__dict__.keys():
            return self.__dict__[key]
        # else:
        return False
