from electrode_names import ElectrodeNames
from constants import SelectionType
from storage import Storage

ElectrodeNames.run_unit_tests()

print("Starting unit tests for DataStorage object")
storage = Storage("Scope_Firmware/Python/pythonApi/sensor_data/calibration_data.csv", "Scope_Firmware/Python/pythonApi/sensor_data/sensor_data.csv")

storage.add_calibration(4.0, list(range(96)))
storage.add_calibration(6.5, list(reversed(range(96))))
storage.add_calibration(7.3, list(reversed(range(96))))
storage.add_calibration(2.1, list(range(96)))

storage.add_measurement(list(range(96)))
storage.add_measurement(list(reversed(range(96))))
storage.add_measurement(list(reversed(range(96))))
storage.add_measurement(list(range(96)))

storage.write_data()

print("All tests passed!")
