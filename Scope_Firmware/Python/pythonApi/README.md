# Sensor Python API

## To run:

1. Open a command terminal, and navigate to the directory containig this file.
2. Type `python3 main.py` or `python main.py`. This will run the main python
   script in your terminal.
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
