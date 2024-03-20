from electrode_names import ElectrodeNames
from config import N_ELECTRODES
from storage import Storage
from numpy.random import rand, uniform
from pathlib import Path
from shutil import rmtree
import numpy as np
from random import shuffle

ElectrodeNames.run_unit_tests()

print("Starting unit tests for DataStorage object")
epsilon = 1e-5

test_folder_path = "TEST_sensor_data/"
def reset_test_folder():
    rmtree(test_folder_path)
    Path(test_folder_path).mkdir(parents = True, exist_ok = True)

print("Test 0: two data points for each electrode and interpolate between them")
reset_test_folder()
storage = Storage(f"{test_folder_path}/TEST_calibration_data.csv", f"{test_folder_path}/TEST_sensor_data.csv", f"{test_folder_path}/TEST_ph_data.csv")
test_data = rand(3, N_ELECTRODES)
test_data.sort(axis = 0)
ph_1 = 2
ph_2 = 12
storage.add_calibration(ph_1, test_data[0])
storage.add_calibration(ph_2, test_data[2])
guid = storage.add_measurement(test_data[1])
for electrode_id in range(N_ELECTRODES):
    expected = (test_data[1][electrode_id] - test_data[0][electrode_id]) / (test_data[2][electrode_id] - test_data[0][electrode_id]) * (ph_2 - ph_1) + ph_1
    result = storage.ph_data[storage.ph_data["guid"] == guid][f"ph_electrode_{electrode_id}"].iloc[0]
    error = expected - result
    assert(np.abs(error < epsilon))


print("Test 1: check that extraneous calibrations don't impact the relevant interp region")
reset_test_folder()
storage = Storage(f"{test_folder_path}/TEST_calibration_data.csv", f"{test_folder_path}/TEST_sensor_data.csv", f"{test_folder_path}/TEST_ph_data.csv")

test_data = rand(7, N_ELECTRODES) * 2
test_data.sort(axis = 0)
ph_0 = 1
ph_1 = 3
ph_2 = 5
ph_3 = 7
ph_4 = 9
ph_5 = 11
ph_6 = 13

storage.add_calibration(ph_0, test_data[0])
storage.add_calibration(ph_1, test_data[1])
storage.add_calibration(ph_2, test_data[2])
# storage.add_calibration(ph_3, test_data[3])
storage.add_calibration(ph_4, test_data[4])
storage.add_calibration(ph_5, test_data[5])
storage.add_calibration(ph_6, test_data[6])

guid = storage.add_measurement(test_data[3])
for electrode_id in range(N_ELECTRODES):
    expected = (test_data[3][electrode_id] - test_data[2][electrode_id]) / (test_data[4][electrode_id] - test_data[2][electrode_id]) * (ph_4 - ph_2) + ph_2
    result = storage.ph_data[storage.ph_data["guid"] == guid][f"ph_electrode_{electrode_id}"].iloc[0]
    error = expected - result
    assert(np.abs(error < epsilon))

print("Test 2: adding a bunch of calibrations close to ph_1 and ph_2")
reset_test_folder()
storage = Storage(f"{test_folder_path}/TEST_calibration_data.csv", f"{test_folder_path}/TEST_sensor_data.csv", f"{test_folder_path}/TEST_ph_data.csv")

test_data = rand(3, N_ELECTRODES) # same test data as before
test_data.sort(axis = 0)
ph_1 = 2
ph_2 = 12

for i in range(5):
    storage.add_calibration(ph_1 + uniform(-0.4, 0.4), rand(N_ELECTRODES) * 5)
    storage.add_calibration(ph_2 + uniform(-0.4, 0.4), rand(N_ELECTRODES) * 5)

# overwrite the noisy data points with original random numbers
storage.add_calibration(ph_1, test_data[0])
storage.add_calibration(ph_2, test_data[2])

guid = storage.add_measurement(test_data[1])
for electrode_id in range(N_ELECTRODES):
    expected = (test_data[1][electrode_id] - test_data[0][electrode_id]) / (test_data[2][electrode_id] - test_data[0][electrode_id]) * (ph_2 - ph_1) + ph_1
    result = storage.ph_data[storage.ph_data["guid"] == guid][f"ph_electrode_{electrode_id}"].iloc[0]
    error = expected - result
    assert(np.abs(error < epsilon))

print("Test 3: back to test 0 but spacing out calibrations with NaNs")
reset_test_folder()
storage = Storage(f"{test_folder_path}/TEST_calibration_data.csv", f"{test_folder_path}/TEST_sensor_data.csv", f"{test_folder_path}/TEST_ph_data.csv")

test_data = rand(3, N_ELECTRODES)
test_data.sort(axis = 0)
ph_1 = 2
ph_2 = 12

def assign_calibrations(ph_value, test_data_row):
    electrode_order = list(range(N_ELECTRODES))
    shuffle(electrode_order)
    n_electrodes_per_calibration = 8
    for i in range(int(N_ELECTRODES / n_electrodes_per_calibration)):
        electrodes_to_include = electrode_order[i * n_electrodes_per_calibration:(i + 1) * n_electrodes_per_calibration]
        data_to_add = []
        for electrode_id in range(N_ELECTRODES):
            if electrode_id in electrodes_to_include:
                data_to_add.append(test_data[test_data_row, electrode_id])
            else:
                data_to_add.append(None)
        # print(data_to_add)
        storage.add_calibration(ph_value, data_to_add)

assign_calibrations(ph_1, 0)
assign_calibrations(ph_2, 2)

guid = storage.add_measurement(test_data[1])
for electrode_id in range(N_ELECTRODES):
    expected = (test_data[1][electrode_id] - test_data[0][electrode_id]) / (test_data[2][electrode_id] - test_data[0][electrode_id]) * (ph_2 - ph_1) + ph_1
    result = storage.ph_data[storage.ph_data["guid"] == guid][f"ph_electrode_{electrode_id}"].iloc[0]
    error = expected - result
    assert(np.abs(error < epsilon))

print("All tests passed!")
