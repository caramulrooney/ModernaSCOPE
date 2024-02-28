from prompt_toolkit import PromptSession
from commands import Commands

from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexer import RegexLexer
from pygments.token import *

class CustomLexer(RegexLexer):
    tokens = {
        'root': [
            (r'^[^ ]+', Generic.Heading), # bold blue
            (r' ([0-9]*[.])?[0-9]+', Literal), # White
            (r' ([^-])([^ ])*', Literal.String), # red
            (r'--[^ ]+', Name.Decorator), # dark gray
            (r'-[^- ]+', Name.Tag), # bold green
        ]
    }

commands = Commands()
session = PromptSession()

while True:
    text = session.prompt("# ", lexer = PygmentsLexer(CustomLexer))
    # text = "measure --electrod 9 --now --max_time 120"
    # text = "clear_calibration --electrod 9 --all"
    # text = "calibrate 9"
    # text = "calibrate -h"
    try:
        commands.execute(text)
    except:
        continue
