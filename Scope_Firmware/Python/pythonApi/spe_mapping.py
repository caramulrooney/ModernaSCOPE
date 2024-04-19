from constants import N_ELECTRODES
from electrode_names import ElectrodeNames
from typing import Optional
import numpy as np

class electrodeMap():
    _sensor_index_to_electrode_id_battleship = {
        "A6":  "H12",
        "A8":  "H11",
        "A9":  "H10",
        "A7":  "H9",
        "A4":  "H8",
        "A1":  "H7",
        "A1":  "H6",
        "A5":  "H5",
        "B2":  "H4",
        "B4":  "H3",
        "B5":  "H2",
        "B3":  "H1",
        "A12": "G12",
        "A11": "G11",
        "A10": "G10",
        "B1":  "G9",
        "B10": "G8",
        "B12": "G7",
        "C1":  "G6",
        "B11": "G5",
        "A1":  "G4",
        "B7":  "G3",
        "B6":  "G2",
        "B9":  "G1",
        "C6":  "F12",
        "C8":  "F11",
        "C9":  "F10",
        "C7":  "F9",
        "C4":  "F8",
        "C3":  "F7",
        "C2":  "F6",
        "C5":  "F5",
        "A1":  "F4",
        "D4":  "F3",
        "D5":  "F2",
        "D3":  "F1",
        "C12": "E12",
        "C11": "E11",
        "C10": "E10",
        "D1":  "E9",
        "D10": "E8",
        "D12": "E7",
        "E1":  "E6",
        "D11": "E5",
        "D8":  "E4",
        "D7":  "E3",
        "D6":  "E2",
        "D9":  "E1",
        "A1":  "D12",
        "A1":  "D11",
        "A1":  "D10",
        "A1":  "D9",
        "A1":  "D8",
        "A1":  "D7",
        "A1":  "D6",
        "A1":  "D5",
        "A1":  "D4",
        "A1":  "D3",
        "A1":  "D2",
        "A1":  "D1",
        "A1":  "C12",
        "A1":  "C11",
        "A1":  "C10",
        "A1":  "C9",
        "H10": "C8",
        "H12": "C7",
        "A1":  "C6",
        "H11": "C5",
        "H8":  "C4",
        "H7":  "C3",
        "H6":  "C2",
        "H9":  "C1",
        "H2":  "B12",
        "H4":  "B11",
        "H5":  "B10",
        "H3":  "B9",
        "G12": "B8",
        "G11": "B7",
        "G10": "B6",
        "H1":  "B5",
        "G6":  "B4",
        "G8":  "B3",
        "G9":  "B2",
        "G7":  "B1",
        "G4":  "A12",
        "G3":  "A11",
        "G2":  "A10",
        "G5":  "A9",
        "F6":  "A8",
        "A1":  "A7",
        "A1":  "A6",
        "A1":  "A5",
        "A1":  "A4",
        "A1":  "A3",
        "A1":  "A2",
        "A1":  "A1",
    }

    def __init__(self):
        self.sensor_index_to_electrode_id = {
            ElectrodeNames.parse_electrode_input(key)[0]: ElectrodeNames.parse_electrode_input(val)[0]
            for key, val in self._sensor_index_to_electrode_id_battleship.items()
        }
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

    def remap_sensor_array(self, sensor_array: np.ndarray[float]) -> np.ndarray[float]:
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

e = electrodeMap()
print(e.remap_sensor_array(np.arange(N_ELECTRODES, dtype = float)))
print(e.remap_sensor_list(list(range(N_ELECTRODES))))
