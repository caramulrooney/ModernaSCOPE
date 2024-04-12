# Sensor Python API

## To upload the firmware to the board

1. Open VS Code, make sure Platformio is installed, and open the Platformio
   sidebar. From the Platformio sidebar, click "Open Project".

2. In the file explorer, nagivate to the folder
   `ModernaSCOPE/Scope_Firmware/Platformio/electrodeReader`. When opening a
   Platformio folder, you should always open a directory containing a
   `platformio.ini` file and a `src` subdirectory. The actual code will live in
   the `src` directory, but you need to open that parent folder. Once the
   correct folder is open in VS Code, open up the `src/main.cpp` file and make
   edits as necessary. This might be needed when switching between code for the
   ESP8266 and the Teensy 4.1.

3. Once VSCode has opened the `electordeReader` folder, and along the bottome
   bar, you will notice a little check symbol next to an arrow symbol. The check
   mark is for compile; the arrow symbol is for compile and upload (just like
   the Arduino IDE). Upload the code to the board. If there is a serial
   connection error, make sure no other programs are using the serial port, such
   as the serial monitor.

4. The `electrodeReader` code will wait until a character is sent over Serial.
   When it receives an `e` character, it will respond with a list of the
   voltages at each of the electrodes. That is its only task. All averaging,
   calibration, and data storage occurs on the python interface side. You can
   test the `electrodeReader` code by opening up a serial monitor (either from
   VS Code or the Arduino IDE) and entering the letter `e` and pressing send.
   You should see a list of numbers separated by commas printed to the serial
   monitor.

## To run the Multiplex pH Sensor API:

1. Open a command terminal, and navigate to the
   `ModernaSCOPE/Scope_Firmware/Python/pythonApi` folder.
2. In the command terminal, type `python3 main.py` or `python main.py`. This
   will run the main python script in your terminal.
3. If any "cannot find package" errors arise, you must install the proper python
   packages. Very soon, I'm planning on implementing a `requirements.txt` file
   which will allow you to install all the packages at once.
4. If all goes well, you should see the header text displayed, saying "Multiplex
   pH Sensor". Then you will be running inside the python prompt loop, with a
   `#` symbol to prompt you.
5. It may give you a "trying to connect to Serial" warning followed by a serial
   error message. When this happens, press Ctrl+C to interrupt the program, and
   then run `python3 main.py` or `python main.py` again. I'm working on a fix so
   it can connect to the serial port on the first try.
6. If that is working, you can enter commands at the `#` prompt. One useful
   command is `help`. This will display some basic information about the
   available commands. You can also enter the name of any command followed by
   `-h` to display the help information for that command.
7. The most useful command for you to run right now is `monitor -g`. This will
   launch the window with graphs to display the voltage at each of the
   electrodes.
