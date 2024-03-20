from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from config import init_text_art, Config
from commands import Commands
from lexer import CustomLexer
from sensor import Sensor
import argparse

parser = argparse.ArgumentParser("config")
parser.add_argument("config", nargs = "*", default = ["config.json"])
args = parser.parse_args()
Config.set_config(args.config[0])


sensor = Sensor()
commands = Commands(sensor)
session = PromptSession()

print(init_text_art)

# include the GUID of the three calibrations that were used to convert the voltage to a pH value for a given measurement

while True:
    text = session.prompt("# ", lexer = PygmentsLexer(CustomLexer))
    commands.execute(text)
