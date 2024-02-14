# Ph Measurement Device API Description

## Measurement

- be able to record the serial number (unique identifier) for the specific
  electrode
- status: online, offline, error state, communication protocol, etc.
- proper error messages, success messages, etc.

`measure [-e/electrode/s <electrode range>] [-n/ow] [t/ime/_steps <interval>] [max_time <max time>] [-v/oltage/_only]`

Measure pH of electrodes within a certain range once the measurements have
settled. Silently run in the background until measurements are settled, then
print the results in a tabular format.

- `-electrodes`: Electrode range to measure. Default is all 96 electrodes.
- `-now`: Do not wait for measurements to settle; report pH measurements now.
- `-time_steps`: Print out the pH values every n seconds until it settles
  (default: 1 second).
- `-max_time`: Wait at most n seconds for the measurement to settle. Default is
  all 96 electrodes.
- `-voltage_only`: Report voltage values, not pH values.

## Calibration

`calibrate <pH> [-e/elctrode/s <electrode range>]`

Calibrate electrodes with a standard pH buffer. Assume a standard buffer
solution has already been applied to the specified electrodes. Store the current
voltage for the specified electrodes in memory and use it as a comparison to
calculate the pH of those electrodes in the future.

Each calibration for a new pH value will be stored. If a new calibration is
performed at a pH value that has already been calibrated, the previous
calibration will be overwritten.

- `pH`: The pH of the buffer currently applied to the electrodes being
  calibrated.
- `-electrodes`: Electrode range to calibrate. Default is all 96 electrodes.

---

`show_calibration [-e/elctrode/s <electrode range>] [-p/H <pH>] [-s/ort/_by_pH]`

Show calibrated voltage values for each calibrated electrode, along with the the
timestamp and temperature of each calibration.

- `-electrodes`: Electrode range to show calibrated voltages for. Default is all
  96 electrodes.
- `-pH`: Each electrode may have multiple calibration voltages for different pH
  values. Show only the calibration voltage corresponding to a single pH.
- `-sort_by_pH`: Sort values in ascending order of pH. Default is to sort by
  timestamp.

---

`clear_calibration [-e/elctrode/s <electrode range>] [-p/H <pH>] [-a/ll]`

Clear the most recent calibration values for the specified electrodes.

- `-electrodes`: Electrode range to clear calibrated voltages for. Default is
  all 96 electrodes.
- `-pH`: Clear the calibration voltage corresponding to a specified pH.
- `-all`: Clear calibration voltages for all pH values for the specified
  electrodes.
