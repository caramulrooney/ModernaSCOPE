# Multiplex pH Sensor API

## Introduction

This is the API meant to be used with the multiplex pH sensor developed by the
Olin College SCOPE team in collaboration with Moderna. To set up the device, it
must be connected via USB cable to a computer running Windows. Then, the API
should be started by running the `main.py` script in Python. This API runs a
custom command-line interface, meaning that to perform actions like calibrating
or starting a measurement the user must type the appropriate command into a
terminal. Data are automatically stored in CSV files and can be accessed using
MS Excel or another spreadsheet-editing software.

## First-time setup

1. Open a command prompt by searching for `Command Prompt` in the Windows start
   menu.
2. Ensure Python is installed on your computer. To do this, type
   `python --version` into the command prompt. It is recommended that you have
   Python version 3.10 or higher. To download the latest version of Python,
   visit [python.org](https://www.python.org/downloads/).
3. Clone or download the code in this repo and save it to a folder which you can
   access, such as `C:\Users\your_username\Documents\multiplex-ph-sensor`. You
   can download the code from `github.com`
4. In the command prompt, use `cd path\to\your\directory` to navigate to the
   directory where this repo is downloaded. For exmple, you might type
   `cd C:\Users\your_username\Documents\multiplex-ph-sensor`.
5. Make sure the USB cable from the device is plugged in to the computer.
6. Run the command `python -m venv .venv`. This will create a virtual
   environment in which code you intall will not affect the rest of the
   computer.
7. Run the command `.venv\Scripts\activate.bat` to activate the virtual
   environment.
8. Run the command `pip install -r requirements.txt`. This will install all
   additional code needed to run the software. If this doesn't work, you can
   install the packages manually, which is outlined in the Appendix.
9. Run the command `mode | findstr COM`. This will print out a list of Serial
   COM ports connected to your computer. The COM port assigned to the device
   will vary, but it will be something like `COM 6` or `COM 10`. On some
   machines the port `COM 3` will be used by an internal device, so you should
   look for the port that is not `COM 3`. If there are multiple options
   available, you can unplug the device and re-run the command to see which COM
   port disappeared.
10. In a text-editing program, open the file `settings\config.json` in this
    repo. Find the setting named `"serial_port"`, and change its value to the
    COM port you identified in the previous step. An example would be
    `"serial_port": "COM6",`.
11. In the `settings\config.json` file, change the setting `"random_data"` to
    `false`, as in `"random_data": false`. This is a debugging setting which
    randomly generates data points instead of reading them from the sensor.
12. In the command prompt, run the command `python main.py -m`. This runs the
    Python script to launch the software. The `-m` flag in the command sets up
    the folder structure to store your data files and is only necessary the
    first time you run the software. If successful, you should see the words
    "Multiplex pH Sensor" in large text, and the text input prompt will become a
    `#` symbol.

## Launching the API

1. Make sure the USB cable from the device is plugged in to the computer.
2. Open a command prompt by searching for `Command Prompt` in the Windows start
   menu.
3. In the command prompt, use `cd path\to\your\directory` to navigate to the
   directory where this repo is downloaded. For exmple, you might type
   `cd C:\Users\your_username\Documents\multiplex-ph-sensor`.
4. Run the command `.venv\Scripts\activate.bat` to activate the virtual
   environment.
5. Run the command `python main.py` to launch the API software.

## API Command Anatomy

The API software is in the form of a command-line interface. That is, to perform
specific actions with the sensor, such as calibrating or saving data, you type
commands into the terminal and press enter to run them. Some commands are single
words, such as `measure`, and most commands have various options, or flags,
which tell the software to perform the command in a certain way. For example,
`measure` takes an optional argument `-n <your_number>` which specifies how many
data points to capture and average together to produce the measurement.

Different commands may have slightly different syntaxes based on what kinds of
arguments they take.

- Commands with optional flags

  - `action`
  - `action -<flag>`
  - `action -<flag> -<flag>`
  - Examples:
  - `measure`
  - `measure -p`
  - `measure -p -s`

- Commands with parameters (optional flags requiring arguments)

  - `action -<param> <value>`
  - `action -<param> <value> -<param> <value>`
  - `action -<param> <value> -<param> <value> -<flag>`
  - Examples:
  - `measure -n 5`
  - `measure -n 5 -e A1-A12`
  - `measure -n 5 -e A1-A12 -s`

- Commands with a required first argument
  - `action <required_argument>`
  - `action <required_argument> -<flag> -<flag>`
  - `action <required_argument> -<param> <value> -<flag>`
  - Examples:
  - `calibrate 7.0`
  - `calibrate 7.0 -p -s`
  - `calibrate 7.0 -e A1-A12 -p`

Notes:

- Most flags have two names: a one-letter name, such as `-e`, and a longer name,
  such as `--electrodes`. The two names can be used interchangeably.
- As an alternative syntax, multiple one-letter flags can be combined into one,
  as in `measure -ps`. This only works for flags that don't take a parameter.

## Command Descriptions

List of available commands:

- `measure`: Take one measurement, convert it to pH, and store it in a file.
- `calibrate`: Take one measurement and store it in a calibration data file.
- `show`: Show information about the sensor or the most recent data.
- `monitor`: Display sensor voltage readings in a continually updated fashion.
- `load`: Reload settings files.
- `write`: Re-save the most recent data, if such a save failed previously.
- `conversion_info`: Show which calibration data were used in a pH conversion.
- `help`: Display information about how to use certain functions.
- `quit`: Exit the command-line interface.

### Help

Usage: `help [-h]`

Display usage information for all commands.

Optional arguments:

- `-h`, `--help`: Show this help message and exit.

### Measure

Usage: `measure [-h] [-e ELECTRODES] [- NUM_MEASUREMENTS`] [-p] [-s] [-v]`

Measure pH of electrodes within a certain range once the measurements have
settled. Silently run in the background until measurements are settled, then
print the results in a tabular format.

Optional arguments:

- `-h`, `--help`: Show this help message and exit.
- `-e ELECTRODES`, `--electrodes ELECTRODES`: Electrode range to measure.
  Default is all 96 electrodes.
- `-n NUM_MEASUREMENTS`, `--num_measurements NUM_MEASUREMENTS`: Number of
  measurements to take and average together. Default is 5 measurements. `-p`,
  --past_data Read the past n measurements and, if so many measurements exist
  already, return immediately.
- `-s`, `--show`: Show the pH values after they are measured.
- `-v`, `--voltage`: Show the voltage values after they are measured.

### Calibrate

Usage: `calibrate [-h] [-e ELECTRODES] [- NUM_MEASUREMENTS] [-p] [-s] [-v] ph`

Calibrate electrodes with a standard pH buffer. Assume a standard buffer
solution has already been applied to the specified electrodes. Store the current
voltage for the specified electrodes in memory and use it as a comparison to
calculate the pH of those electrodes in the future. Each calibration for a new
pH value will be stored. If a new calibration is performed at a pH value that
has already been calibrated, the previous calibration will be overwritten.

Positional arguments:

- `ph`: The pH of the buffer currently applied to the electrodes being
  calibrated.

Optional arguments:

- `-h`, `--help`: Show this help message and exit..
- `-e ELECTRODES`, `--electrodes ELECTRODES`: Electrode range to calibrate.
  Default is all 96 electrodes.
- `-n NUM_MEASUREMENTS`, `--num_measurements NUM_MEASUREMENTS`: Number of
  measurements to take and average together. Default is 5 measurements.
- `-p`, `--past_data`: Read the past n measurements and, if so many measurements
  exist already, return immediately.
- `-s`, `--show`: Show the pH values after they are measured.
- `-v`, `--voltage`: Show the voltage values after they are measured.

### Monitor

Usage: `monitor [-h] [-e ELECTRODES] [-f] [-g]`

Display sensor voltage readings in a continually updated fashion.

Optional arguments:

- `-h`, `--help`: Show this help message and exit.
- `-e ELECTRODES`, `--electrodes ELECTRODES`: Only monitor selected electrodes.
  Default is all 96 electrodes.
- `-f`, `--file`: Write continually updated voltage readings to the file
  specified in the JSON configuration file.
- `-g`, `--graph`: Display continually updated voltage readings in a new window
  in graphical form.

### Show

Usage: `show [-h] [-i] [-e ELECTRODES] [-cv] [-cp] [-p] [-v]`

Display information about the selected electrodes, most recent calibrations, and
measurements.

Optional arguments:

- `-h`, `--help`: Show this help message and exit.
- `-i`, `--ids`: Show how the A1-H12 notation is mapped onto the electrode index
  in the code. This can be useful for debugging or for inspecting the CSV files
  where calibration and measurement data are stored.
- `-e ELECTRODES`, `--electrodes ELECTRODES`: Show which electrodes are selected
  by providing a range in A1-H12 notation.
- `-cv`, `--calibration_voltage`: Show the voltages on each of the electrodes
  during the most recent calibration.
- `-cp`, `--calibration_ph`: Show the pH on each of the electrodes during the
  most recent calibration.
- `-p`, `--ph`: Show the pH on each of the electrodes for the most recent
  measurement.
- `-v`, `--voltage`: Show the voltages on each of the electrodes during the most
  recent measurement.

### Load

Usage: `load [-h] [-f FILE]`

Re-load the csv file for calibration data from memory.

Optional arguments:

- `-h`, `--help`: Show this help message and exit.
- `-f FILE`, `--file FILE`: Re-load files from the specified JSON configuration
  file. Default is the configuration file used to initialize the program.

### Write

Usage: `write [-h] [-f FILE]`

Write the currently stored data to a csv file. This should be done automatically
after every measurement and calibration, except when a file write fails because
the file was open in another program at the same time.

Optional arguments:

- `-h`, `--help`: Show this help message and exit.
- `-f FILE`, `--file FILE`: Write files to the filenames specified in the JSON
  configuration file. Default is the configuration file used to initialize the
  program.

### Conversion_Info

Usage: `conversion_info [-h] [-m MEASUREMENT_ID]`

Generate conversion information for a given measurement ID to show which
calibration data points were used to convert from a voltage to a pH. Store the
resulting information as a CSV file in the folder specified in the configuration
file.

Optional arguments:

- `-h`, `--help`: Show this help message and exit.
- `-m MEASUREMENT_ID`, `--measurement_id MEASUREMENT_ID`: Measurement ID for
  which to generate conversion information.

### Quit

Usage: `quit [-h]`

Exit the program.

Optional arguments:

- `-h`, `--help`: Show this help message and exit.

## Example Workflow

Suppose you want to measure the pH of 30 different samples. These will easily
fit onto one 96-well plate. You want to calibrate the electrode, then place your
samples, wait for the pH readings to settle, and then take the average of 100
sensor readings at each electrode and compare the results to known pH values.

First, you have to choose which wells of the electrode to use, since you will
only be using 30 out of 96 wells. Let's say you choose the first 30 wells,
starting with A1 and counting along the rows (A1, A2, A3, ... B1, B2, B3, ...
C1, C2, C3, ... C6) until C6, which is the 30th well. This can be represented by
the notation `"A1-C6:rowwise"`. To check that this notation is correct, use the
command `show --electrodes A1-C6:rowwise`. Indeed, we see that this notation is
correct.

Before you start performing calibrations and measurements, you probably want to
have a way to visualize the data as it comes in, so you can get an idea of when
a measurement has settled. One way to do this is to run
`monitor --graph --electrodes A1-C6:rowwise`. This will pull up a set of graphs
of the voltages on each of the electrodes we care about, and the graphs will be
updated continuously as new data come in from the sensor.

Now, you want to calibrate the electrode. Through prior knowledge, you assume a
3-point calibration curve with pH buffers of 4.0, 7.0, and 10.0 pH will produce
an accurate reading. First, place the pH 4 buffer solution onto each of the
electrodes you will be using for the measurement. Watch the graphs to see the
voltages change and approach a new value. Once they appear to have settled, run
the command `calibrate 4.0 -n 10 -e A1-C6:rowwise`. This will collect another
ten data points, average them together, and save the voltages at each electrode
to the calibration data file. Since the sensor reads at a rate of one sample per
second, this takes ten seconds to complete. If instead of waiting for ten more
data points to occur you wanted to use the ten most recent data points and
complete instantaneously, you could have added the `--past_data` flag, or `-p`
for short, as in `calibrate 4.0 -n 10 -e A1-C6:rowwise -p`.

Remove the pH 4 buffer solution, rinse the electrode, and apply the pH 7
solution. Watch the voltages and wait for them to settle, then run
`calibrate 7.0 -n 10 -e A1-C6:rowwise`. Follow the same procedure to calibrate
at pH 10.

You can now verify that your calibration data were logged correctly. In a file
explorer, navigate to the directory containing this repo, then go into the
folder named `sensor_data`. Inside, you will find a file named
`calibration_data.csv`. Open this file in Excel and verify that the three most
recent entries are the ones you just performed. The timestamps for the last
three rows should match the time of the calibration, and only the first 30 cells
should have values; the rest of the columns should be blank. When you are done
viewing the data, you must close Excel, because this interferes with the
software accessing the same data to perform calibrations.

Now it's time to take the measurement. Rinse the electrode and place your sample
solution into the 30 wells you just calibrated. Watch the voltages and wait for
them to settle, then run `measure -n 100 -e A1-C6:rowwise`. Since you are taking
the average of 100 sensor readings, it will take about 100 seconds to complete,
during which time you cannot perform any other commands. Once the measurement is
complete, it will print a message and allow you to type again.

The average of the voltage values at each electrode will be stored as a row in
the `sensor_data` folder in a file named `measurement_data.csv`. The pH value
calculated using the conversion data will be stored as a row in the
`ph_result.csv` file. Open the `ph_result.csv` file in Excel and look at the
most recent row to view the results of the measurement.

## Sensor Data Files

### Calibration Data File

When a calibration is performed with the `calibrate` command, the data are
stored to a file called `sensor_data/calibration_data.csv`. Each calibration is
saved as its own row in the spreadsheet and contains:

- The timestamp at which the calibration was performed
- A globally unique identifier ([GUID](https://www.guidgenerator.com/)), which
  is a long string of hexadecimal characters used to refer to the specific
  calibration in other contexts
- The pH of buffer solution applied for the calibration
- A column for the user to flag invalid data points, along with notes about why
  they are invalid
- The voltage at each electrode when the pH buffer was applied (96 columns in
  total)

If you believe a calibration was performed incorrectly, you can manually change
the value in the `is_valid` column of the spreadsheet and optionally leave a
note as to why in the `invalid_reason` column. This will ensure that the data
from that calibration run will not be used.

By default, calibration data older than 12 hours will be invalid (although this
wil not be denoted in the `is_valid` column).

### Measurement Data File

When a measurement is performed with the `measure` command, the data are stored
to a file called `sensor_data/measurement_data.csv`. Each measurement is saved
as its own row in the spreadsheet and contains:

- The timestamp at which the measurement was performed
- A globally unique identifier ([GUID](https://www.guidgenerator.com/)), which
  is a long string of hexadecimal characters used to refer to the specific
  measurement in other contexts
- The voltage at each electrode for that measurement (96 columns in total)

Additionally, the data are automatically converted into pH values and stored in
a separate file named `sensor_data/ph_result.csv`. The timestamps and GUIDs of
the data in this file should correspond to the those of the
`measurement_data.csv` file.

### Calibration Map

A list of which calibration data points were used for this conversion will be
stored in the `sensor_data/calibration_map` folder. Since this information can
be complex, a new file is generated for each measurement. The file name will
contain the timestamp and GUID of the measurement. For example, the file
`2024_04_24_14_38_40_243106_Measurement_ID_(cbdac8cf-5f5b-43c2-a5b6-326db986b4d0).csv`
contains pH calibration information for the measurement performed at time
`2024_04_24_14_38_40_243106` (April 24th 2024 at 2:38 PM and 40.24106 seconds)
with GUID `cbdac8cf-5f5b-43c2-a5b6-326db986b4d0`.

For the calibration map data file for a specific measurement, the rows represent
the GUIDs of each of the calibration data points that could have been used in
the pH conversion, and the columns indicate whether that calibration data point
was used for each electrode. The most common case is if the same calibration
data were used for all 96 electrodes, in which case the `All electrodes` column
is `TRUE`. However, it is possible that different electrodes were calibrated at
different times, in which case the calibration data points used for each
electrode may be different.

For example, if the file
`2024_04_24_14_38_40_243106_Measurement_ID_(cbdac8cf-5f5b-43c2-a5b6-326db986b4d0).csv`
contained the following, it would mean that for the measurement performed on
April 24th, the first calibration data point was considered for all electrodes,
whereas the second calibration data point only applied for electrode_0 (A1), and
the third calibratino data point only applied for electrode_1 (A2). This could
have come about if a calibration had to be redone for just the A2 electrode
using the `calibrate <pH> --electrodes A2` command, such that the new
calibration data point was used instead of the calibration data for the rest of
the electrodes.

| Calibration ID                       | All electrodes | electrode_0 | electrode_1 |
| ------------------------------------ | -------------- | ----------- | ----------- |
| 09e6d75b-a094-409d-9e0e-491ef1353446 | TRUE           | TRUE        | TRUE        |
| 2da028c7-016d-4b88-a315-4121304cec54 | FALSE          | TRUE        | FALSE       |
| 4fb73a8f-0e05-4291-8d02-a22532fb53ed | FALSE          | FALSE       | TRUE        |

### Determining Which Calibration Data are Used

A multi-step algorithm is used to determine which calibration data should be
used in the conversion from voltage to pH of a given measurement.

1. Per Macias Sensors' specifications, calibration data are not valid after 12
   hours. Therefore, older calibration data will not be considered.
2. If multiple calibrations were performed successively with the same pH, only
   the most recent calibration will be considered. Two calibrations are taken to
   be the same if their pH differs by less than 0.5.
3. Among the remaining calibration data points, the two closest calibrations are
   linearly interpolated between to find the pH of the measurement.

This algorithm is performed individually for each electrode, since the
calibration history may differ from electrode to electrode. The files in the
`calibration_map` folder describe which calibration data points were used for
each electrode in a given measurement.

## Specifying Electrodes

### Battleship Notation

Sometimes you may want to apply a command to only a specific range of
electrodes. Most commands have a `-e` parameter to specify an electrode range.

- A single electrode can be identified by its battleship notation
  - `A1`
  - `B2`
- A range of electrodes is specified with a `-`
  - By default, the range is interpreted as 'Excel-like'; that is, only
    electrodes within a rectangle spanning the range will be included.
    - `A1-B3` expands to `A1, A2, A3, B1, B2, B3`
    - `D12-H12` expands to `D12, F12, G12, H12`
  - There are two other selection options. 'Row-wise' includes electrodes
    horizontally, starting with the first electrode in the range and wrapping
    around rows until it reaches the last electrode in the range.
    - `A1-B3:rowwise` expands to
      `A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, A12, B1, B2, B3`
  - `Column-wise` includes electrodes vertically, starting with the first
    electrode in the range and wrapping around columns until it reaches the last
    electrode in the range.
    - `A1-B3:columnwise` expands to
      `A1, B1, C1, D1, E1, F1, G1, H1, A2, B2, C2, D2, E2, F2, G2, H2, A3, B3`.
- Multiple electrodes or ranges of electrodes can be concatenated with a `,`
  (but no space character)
  - `A1,B2`
  - `A1-A12:rowwise,A12-H12:columnwise`

Note: the words `rowwise`, `columnwise`, and `excellike` don't need to be typed
out. The letters `r`, `c`, and `e` will also be recognized, as will any shorter
prefix, such as `row`.

If you want some practice creating electrode ranges, or if you want to check
your notation before starting a measurement, you can use the `show -e` command,
as in `show -e A1-B3:rowwise`. This will display a visual map of the electrode
card with the selected electrodes marked.

### Electrode ID Notation

Electrodes can also be specified using a unique number from 0 to 95. This
notation is often used internally to the software. This notation is also used
for column names in the data files. The electrodes are named numerically,
starting with `A1 = electrode_0`, and incrementing row-wise, as follows:

- `A1 = electrode_0`
- `A2 = electrode_1`
- `A3 = electrode_2`
- ...
- `B1 = electrode_12`
- `B2 = electrode_13`
- `B3 = electrode_14`
- ...
- `H12 = electrode_95`

To see a complete mapping of battleship notation to electrode ids, run the
command `show` without any arguments.

```
               1       2      3        4       5       6       7       8       9       10      11      12
       __________________________________________________________________________________________________________
      |                                                                                                          |
      |                                                                                                          |
  A   |      ~ 0 ~   ~ 1 ~   ~ 2 ~   ~ 3 ~   ~ 4 ~   ~ 5 ~   ~ 6 ~   ~ 7 ~   ~ 8 ~   ~ 9 ~   ~ 10 ~  ~ 11 ~      |
      |                                                                                                          |
  B   |      ~ 12 ~  ~ 13 ~  ~ 14 ~  ~ 15 ~  ~ 16 ~  ~ 17 ~  ~ 18 ~  ~ 19 ~  ~ 20 ~  ~ 21 ~  ~ 22 ~  ~ 23 ~      |
      |                                                                                                          |
  C   |      ~ 24 ~  ~ 25 ~  ~ 26 ~  ~ 27 ~  ~ 28 ~  ~ 29 ~  ~ 30 ~  ~ 31 ~  ~ 32 ~  ~ 33 ~  ~ 34 ~  ~ 35 ~      |
      |                                                                                                          |
  D   |      ~ 36 ~  ~ 37 ~  ~ 38 ~  ~ 39 ~  ~ 40 ~  ~ 41 ~  ~ 42 ~  ~ 43 ~  ~ 44 ~  ~ 45 ~  ~ 46 ~  ~ 47 ~      |
      |                                                                                                          |
  E   |      ~ 48 ~  ~ 49 ~  ~ 50 ~  ~ 51 ~  ~ 52 ~  ~ 53 ~  ~ 54 ~  ~ 55 ~  ~ 56 ~  ~ 57 ~  ~ 58 ~  ~ 59 ~      |
      |                                                                                                          |
  F   |      ~ 60 ~  ~ 61 ~  ~ 62 ~  ~ 63 ~  ~ 64 ~  ~ 65 ~  ~ 66 ~  ~ 67 ~  ~ 68 ~  ~ 69 ~  ~ 70 ~  ~ 71 ~      |
      |                                                                                                          |
  G   |      ~ 72 ~  ~ 73 ~  ~ 74 ~  ~ 75 ~  ~ 76 ~  ~ 77 ~  ~ 78 ~  ~ 79 ~  ~ 80 ~  ~ 81 ~  ~ 82 ~  ~ 83 ~      |
       \                                                                                                         |
  H     \    ~ 84 ~  ~ 85 ~  ~ 86 ~  ~ 87 ~  ~ 88 ~  ~ 89 ~  ~ 90 ~  ~ 91 ~  ~ 92 ~  ~ 93 ~  ~ 94 ~  ~ 95 ~      |
         \                                                                                                       |
          \______________________________________________________________________________________________________|
```

## Configuration Settings

Some settings in the software, notably the serial port the device is connected
to and certain file locations, can be modified from the configuration file,
named `config.json`. The JSON file is structured as a series of key-value pairs
with the syntax `"key": "value"`. To change a setting, simply replace the value
and save the file, then re-launch the software. For example, during setup, you
had to change the `serial_monitor` setting to something like
`"serial_monitor": "COM7"`.

The available configuration settings are

- `serial_port`: The serial port to attempt to connect to the device on. This
  will vary from computer to computer and sometimes run to run. See the
  first-time setup instructions for how to determine which serial port the
  device is connected on. On Windows, the serial port is usually the word "COM"
  followed by a number, such as `COM7` or `COM10`.
- `board_revision`: The version of the printed circuit board (PCB) hardware
  inside the device, in case the electrode mapping changes from version to
  version. As of May 2024, the most recent board revision was `2`.
- `measurement_interval`: Time between successive measurements in seconds. This
  controls how frequently the `monitor` command is updated, as well as how long
  it takes to perform repeated measurements and average them together, as in the
  `measure -n 10` command. The minimum measurement interval is determined by the
  electronics, so a measurement interval of at least one second is recommended.
- `voltage_display_filename`: Name of the file to update during use of the
  `monitor -f` command.
- `monitor_datasets_folder`: Path to folder in which to store running data
  points stored during use of the `monitor` command.
- `calibration_data_filename`: Name of the file in which to store calibration
  data.
- `measurement_data_filename`: Name of the file in which to store measured
  electrode voltage data.
- `ph_result_filename`: Name of the file in which to store the pH values
  calculated as the result of the voltage measurements.
- `calibration_map_folder`: Path to folder in which to generate calibration map
  files to show which calibration data points were used in the conversion of
  each pH measurement.
- `prompt_history_filename`: Name of the file used to keep track of the command
  history from session to session, which enables use of the up arrow to access
  previous commands.
- `calibration_invalid_time`: The amount of time after a calibration is
  performed during which the calibration is valid. When performing a pH
  conversion, calibration data taken before this time will not be considered.
- `timezone`: The time zone in which the measurement and calibration timestamps
  should be saved. The list of valid timezone names is
  [here](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568).
- `random_data`: For debugging purposes, generate random data instead of reading
  data from the sensor. This allows the software to be tested without having the
  physical device plugged in.

The default configuration settings are

```json
{
  "serial_port": "COM10",
  "board_revision": 2,
  "measurement_interval": 1,
  "voltage_display_filename": "display/voltage_display.txt",
  "monitor_datasets_folder": "display/monitor_datasets/",
  "calibration_data_filename": "sensor_data/calibration_data.csv",
  "measurement_data_filename": "sensor_data/measurement_data.csv",
  "ph_result_filename": "sensor_data/ph_result.csv",
  "calibration_map_folder": "sensor_data/calibration_map/",
  "prompt_history_filename": "settings/prompt_history.txt",
  "calibration_invalid_time": "12 hours",
  "timezone": "US/Eastern",
  "random_data": false
}
```

## Exiting the API

To exit the API, press `Ctrl+C`, or enter the `quit` command.
