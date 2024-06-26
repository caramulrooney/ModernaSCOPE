# External libraries
from serial import SerialException
from threading import Timer, Thread

# Prompt and autocompletion features
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import NestedCompleter, WordCompleter
from prompt_toolkit.patch_stdout import patch_stdout

# Lexer and styling features
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from pygments.lexer import RegexLexer
from pygments.style import Style
from pygments.token import Token

# From this project
from constants import init_text_art
from commands import Commands
from sensor_data import DataWritePermissionError, CalibrationError
from sensor_interface import MeasurementInterrupt
from electrode_names import ElectrodeNames, ElectrodeNameParseError
from config import Config
from sensor_interface import SensorInterface
from sensor_display import SensorDisplay

class IntervalTimer(Timer):
    def __init__(self, *args, **kwargs):
        """
        Set daemon property to True during initialization.
        """
        super().__init__(*args, **kwargs)
        self.daemon = True

    def run(self):
        """
        Run indefinitely. Restart the timer as soon as it has elapased.
        """
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class CliStyle(Style):
    styles = {
        Token.Command:  'bold #CC0000',
        Token.Number: '#00CC88',
        Token.ElectrodeRange.Range: '#FFCC00',
        Token.ElectrodeRange.SelectionType: 'italic ansibrightyellow',
        Token.ShortFlag:'bold #00FF00',
        Token.LongFlag: 'italic #005500',
    }

class YesNoStyle(Style):
    styles = {
        Token.YesNo.Yes: 'bold #00CC88',
        Token.YesNo.No: 'bold #CC0000',
        Token.Invalid: '#888888',
    }

class CliLexer(RegexLexer):
    tokens = {
        'root': [
            (r'^[^ ]+', Token.Command),
            (r',', Token.ElectrodeRange.SelectionType),
            (r'(?<= )[0-9.]+(?=( ?))', Token.Number),
            (r'[a-hA-H]1?[0-9](-[a-hA-H]1?[0-9])?', Token.ElectrodeRange.Range),
            (r'((?<=[, ])[rceRCE].*?:)|(:[rceRCE][^, ]*)', Token.ElectrodeRange.SelectionType),
            (r'--[^ ]+', Token.LongFlag),
            (r'(?<= )-[^- ]+', Token.ShortFlag),
        ]
    }

class YesNoLexer(RegexLexer):
    tokens = {
        'root': [
            (r'[^yYnN].*', Token.Invalid),
            (r'[yY]', Token.YesNo.Yes),
            (r'[nN]', Token.YesNo.No),
        ]
    }

def handle_data_write_exception(func):
    """
    Decorator for handling `DataWritePermissionError` exceptions. This occurs when a command tries to write a file which is open in another program. When this exception is encountered, pause and ask the user to close the file, then prompt them to retry.
    """
    def inner_func(self, *args, **kwargs):
        try:
            func(self, *args ,**kwargs)
        except DataWritePermissionError:
            print("Could not open file for writing, likely because the file was open in a different program. Please use the 'write' command to retry, or press enter now.")
            self.retry_file_write()
    return inner_func

def handle_non_fatal_exception(func):
    """
    Decorator for handling specific non-fatal exceptions that occur while executing commands. For this type of exception, the command is aborted, but the the session should not be exited. Print the exception message and return to the main prompt.
    """
    def inner_func(self, *args, **kwargs):
        try:
            func(self, *args ,**kwargs)
        except (CalibrationError, ElectrodeNameParseError, MeasurementInterrupt, SerialException) as ex:
            print(ex)
    return inner_func

class SessionRunner():
    """
    Main process to initialize the command prompt and respond to user input.
    """
    # mirroring the structure in commands.py
    # used for prompt autocompletion
    # used for prompt autocompletion
    command_list = {
        "measure": WordCompleter(['-e', '--electrodes', '-n', '--num_measurements', '-p', '--past_data', '-s', '--show', '-v', '--voltage', ]),
        "calibrate": WordCompleter(['-e', '--electrodes', '-n', '--num_measurements', '-p', '--past_data', '-s', '--show', '-v', '--voltage', ]),
        "show": WordCompleter(['-i', '--ids', '-e', '--electrodes', '-cv', '--calibration_voltage', '-cp', '--calibration_ph', '-p', '--ph', '-v', '--voltage']),
        "monitor": WordCompleter(['-e', '--electrodes', '-f', '--file', '-g', '--graph']),
        "load": WordCompleter(['-f', '--file', ]),
        "write": WordCompleter(['-f', '--file', ]),
        "conversion_info": WordCompleter(['-m', '--measurement_id', ]),
        "help": None,
        "quit": None,
    }

    def __init__(self):
        """
        Initialize prompt session.
        """
        sensor_interface = SensorInterface()
        IntervalTimer(Config.measurement_interval, sensor_interface.update).start()

        sensor_display = SensorDisplay(sensor_interface)

        self.commands = Commands(sensor_interface, sensor_display)
        self.session = PromptSession(history=FileHistory(Config.prompt_history_filename))

    @handle_data_write_exception
    def retry_file_write(self):
        """
        Called during handling of a `DataWritePermissionError` because a command tried to write a file which is open in another program. Pause and ask the user to close the file, then prompt them to retry.
        """
        with patch_stdout():
            while True:
                text = self.session.prompt("Retry now? [Y/n] ",
                    style = style_from_pygments_cls(YesNoStyle),
                    lexer = PygmentsLexer(YesNoLexer)
                )
                text = text.strip()
                if text == "Y" or text == "":
                    self.commands.sensor_data.write_data()
                    print(f"Wrote data successfully.")
                    return
                if text == "n":
                    return
                print("Invalid response.")

    @handle_data_write_exception
    @handle_non_fatal_exception
    def execute(self, text):
        """
        Parse and execute a line of user input.
        """
        self.commands.execute(text)

    def run_session(self):
        """
        Start prompt session and respond to user input. This is a blocking loop and runs forever.
        """
        with patch_stdout():
            print(init_text_art)
            while True:
                text = self.session.prompt("# ",
                    lexer = PygmentsLexer(CliLexer),
                    style = style_from_pygments_cls(CliStyle),
                    completer = NestedCompleter.from_nested_dict(self.command_list)
                )
                text = text.strip()
                self.execute(text)
