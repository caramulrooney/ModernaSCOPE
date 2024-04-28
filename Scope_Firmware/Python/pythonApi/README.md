# Multiplex pH Sensor API

- Liquid added at

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

## Running the API
