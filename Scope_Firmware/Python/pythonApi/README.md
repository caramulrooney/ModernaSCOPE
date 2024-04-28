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
`calibrate 7.0 -n 10`. Follow the same procedure to calibrate at pH 10.

You can now verify that your calibration data were logged correctly. In a file
explorer, navigate to the directory containing this repo, then go into the
folder named `sensor_data`. Inside, you will find a file named
`calibration_data.csv`. Open this file in Excel and verify that the three most
recent entries are the ones we just performed. The timestamps for the last three
rows should match the time of the calibration, and only the first 30 cells
should have values; the rest of the columns should be blank.

### TODO:

- Finish workflow example
- Settings descriptions
- Battleship notation
- Calibration logic
- Modifying the code
  - Settings
  - Simple functions
  - editing the code (forks, etc.)
