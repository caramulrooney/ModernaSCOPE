from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from constants import init_text_art
from commands import Commands
from lexer import CustomLexer
from sensor import Sensor

sensor = Sensor()
commands = Commands(sensor)
session = PromptSession()

print(init_text_art)

# include the GUID of the three calibrations that were used to convert the voltage to a pH value for a given measurement

while True:
    text = session.prompt("# ", lexer = PygmentsLexer(CustomLexer))
    commands.execute(text)
