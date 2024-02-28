from prompt_toolkit import PromptSession
from commands import Commands

from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexer import RegexLexer
from pygments.token import *

class CustomLexer(RegexLexer):
    tokens = {
        'root': [
            (r'^[^ ]+', Generic.Heading),
            (r' ([0-9]*[.])?[0-9]+', Literal),
            (r' ([^-])([^ ])*', Literal.String),
            (r'--[^ ]+', Name.Decorator),
            (r'-[^- ]+', Name.Tag),
        ]
    }

commands = Commands()
session = PromptSession()

while True:
    text = session.prompt("# ", lexer = PygmentsLexer(CustomLexer))
    commands.execute(text)
