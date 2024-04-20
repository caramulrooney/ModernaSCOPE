from constants import N_ELECTRODES
from electrode_names import ElectrodeNames
from typing import Optional
import numpy as np

class ElectrodeMap():
    _sensor_index_to_electrode_id_battleship = {
        "H12": "A6"  ,
        "H11": "A8"  ,
        "H10": "A9"  ,
        "H9": "A7"   ,
        "H8": "A4"   ,
        "H7": None   ,
        "H6": None   ,
        "H5": "A5"   ,
        "H4": "B2"   ,
        "H3": "B4"   ,
        "H2": "B5"   ,
        "H1": "B3"   ,
        "G12": "A12" ,
        "G11": "A11" ,
        "G10": "A10" ,
        "G9": "B1"   ,
        "G8": "B10"  ,
        "G7": "B12"  ,
        "G6": "C1"   ,
        "G5": "B11"  ,
        "G4": None   ,
        "G3": "B7"   ,
        "G2": "B6"   ,
        "G1": "B9"   ,
        "F12": "C6"  ,
        "F11": "C8"  ,
        "F10": "C9"  ,
        "F9": "C7"   ,
        "F8": "C4"   ,
        "F7": "C3"   ,
        "F6": "C2"   ,
        "F5": "C5"   ,
        "F4": None   ,
        "F3": "D4"   ,
        "F2": "D5"   ,
        "F1": "D3"   ,
        "E12": "C12" ,
        "E11": "C11" ,
        "E10": "C10" ,
        "E9": "D1"   ,
        "E8": "D10"  ,
        "E7": "D12"  ,
        "E6": "E1"   ,
        "E5": "D11"  ,
        "E4": "D8"   ,
        "E3": "D7"   ,
        "E2": "D6"   ,
        "E1": "D9"   ,
        "D12": None  ,
        "D11": None  ,
        "D10": None  ,
        "D9": None   ,
        "D8": None   ,
        "D7": None   ,
        "D6": None   ,
        "D5": None   ,
        "D4": None   ,
        "D3": None   ,
        "D2": None   ,
        "D1": None   ,
        "C12": None  ,
        "C11": None  ,
        "C10": None  ,
        "C9": None   ,
        "C8": "H10"  ,
        "C7": "H12"  ,
        "C6": None   ,
        "C5": "H11"  ,
        "C4": "H8"   ,
        "C3": "H7"   ,
        "C2": "H6"   ,
        "C1": "H9"   ,
        "B12": "H2"  ,
        "B11": "H4"  ,
        "B10": "H5"  ,
        "B9": "H3"   ,
        "B8": "G12"  ,
        "B7": "G11"  ,
        "B6": "G10"  ,
        "B5": "H1"   ,
        "B4": "G6"   ,
        "B3": "G8"   ,
        "B2": "G9"   ,
        "B1": "G7"   ,
        "A12": "G4"  ,
        "A11": "G3"  ,
        "A10": "G2"  ,
        "A9": "G5"   ,
        "A8": "F6"   ,
        "A7": None   ,
        "A6": None   ,
        "A5": None   ,
        "A4": None   ,
        "A3": None   ,
        "A2": None   ,
        "A1": "A1"   ,
    }

    def __init__(self):
        self.sensor_index_to_electrode_id = {
            ElectrodeNames.parse_electrode_input(key)[0]: ElectrodeNames.parse_electrode_input(val)[0]
            if val is not None else -1
            for key, val in self._sensor_index_to_electrode_id_battleship.items()
        }
        print(self.sensor_index_to_electrode_id)
        self.electrode_id_array = np.array([-1 for x in range(N_ELECTRODES)], dtype = int)
        for key, val in self.sensor_index_to_electrode_id.items():
            self.electrode_id_array[key] = val
        self.undefined_locs = self.electrode_id_array == -1
        print(f"Electrode mapping contains {np.sum(self.undefined_locs)} undefined electrodes.")

    def get_electrode_id(self, sensor_index: int) -> Optional[int]:
        if sensor_index in self.sensor_index_to_electrode_id.keys():
            return self.sensor_index_to_electrode_id[sensor_index]
        # else:
        return None

    def remap_sensor_array(self, sensor_array: np.ndarray) -> np.ndarray:
        assert len(sensor_array) == N_ELECTRODES
        remapped = sensor_array[self.electrode_id_array]
        remapped[self.undefined_locs] = None
        return remapped

    def remap_sensor_list(self, sensor_array: list[float]) -> list[Optional[float]]:
        """
        Call remap_sensor_array on a list input and returning a list output. NaN values are converted to None.
        """
        remapped = list(self.remap_sensor_array(np.array(sensor_array, dtype = float)))
        remapped = [None if np.isnan(x) else x for x in remapped]
        return remapped

    def unit_tests(self):
        print(self.remap_sensor_array(np.arange(N_ELECTRODES, dtype = float)))
        print(self.remap_sensor_list(list(range(N_ELECTRODES))))
