import json
from pathlib import Path

class Config():
    config_filename = "settings/config.json"
    calibration_data_filename = "sensor_data/calibration_data.csv"
    sensor_data_filename = "sensor_data/sensor_data.csv"
    ph_data_filename = "sensor_data/ph_data.csv"
    calibration_map_folder = "sensor_data/calibration_map/"
    prompt_history_filename = "settings/prompt_history.txt"
    timezone = "US/Eastern"
    debug = False

    @classmethod
    def set_config(cls, config_filename, mkdirs):
        cls.config_filename = config_filename
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
        if "calibration_map_folder" in data.keys():
            cls.calibration_map_folder = data["calibration_map_folder"]
        if "prompt_history" in data.keys():
            cls.prompt_history_filename = data["prompt_history_filename"]
        if "timezone" in data.keys():
            cls.timezone = data["timezone"]
        if "debug" in data.keys():
            cls.debug = data["debug"]

        if mkdirs:
            cls.make_directories()

    @classmethod
    def make_directories(cls):
        Path(cls.calibration_map_folder).mkdir(parents = True, exist_ok = True)
        for path in [cls.calibration_data_filename, cls.sensor_data_filename, cls.ph_data_filename, cls.prompt_history_filename]:
            Path(path).parent.mkdir(parents = True, exist_ok = True)
