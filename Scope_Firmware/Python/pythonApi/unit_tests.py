from electrode_names import ElectrodeNames
from constants import SelectionType
from storage import Storage

ElectrodeNames.run_unit_tests()

print("Starting unit tests for DataStorage object")
# storage = Storage("Scope_Firmware/Python/pythonApi/sensor_data/calibration_data.csv", "Scope_Firmware/Python/pythonApi/sensor_data/sensor_data.csv")
storage = Storage("sensor_data/calibration_data.csv", "sensor_data/sensor_data.csv", "sensor_data/ph_data.csv")
storage.add_calibration(2.1, [0.21] * 96)
storage.add_calibration(4.0, [0.40, None] * int(96 / 2))
storage.add_calibration(6.5, [0.65] * 96)
storage.add_calibration(7.3, [0.73] * 96)
storage.add_measurement([0.3] * 96)
print(".")
storage.add_measurement([0.4] * 96)
print(".")
storage.add_measurement([0.5] * 96)
print(".")
storage.add_measurement([0.6] * 96)
print(".")

print("All tests passed!")
