from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from config import init_text_art, Config, StorageWritePermissionError
from commands import Commands
from lexer import CustomLexer, YesNoLexer
from sensor import Sensor
import argparse

parser = argparse.ArgumentParser("config")
parser.add_argument("config", nargs = "*", default = ["config.json"])
args = parser.parse_args()
Config.set_config(args.config[0])


commands = Commands()
session = PromptSession()

print(init_text_art)

retry_file_write = False

while True:
    if retry_file_write:
        text = session.prompt("Retry now? [Y/n] ")#, lexer = PygmentsLexer(YesNoLexer))
        if text == "Y" or text == "":
            try:
                commands.sensor.storage.write_data()
                retry_file_write = False
            except StorageWritePermissionError as ex:
                print("Could not open file for writing, likely because the file was open in a different program. Please use the 'write' command to retry, or press enter now.")
                print(ex)
                retry_file_write = True
        if text == "n":
            retry_file_write = False

    else:
        text = session.prompt("# ", lexer = PygmentsLexer(CustomLexer))
        try:
            commands.execute(text)
        except StorageWritePermissionError as ex:
            print("Could not open file for writing, likely because the file was open in a different program. Please use the 'write' command to retry, or press enter now.")
            print(ex)
            retry_file_write = True
