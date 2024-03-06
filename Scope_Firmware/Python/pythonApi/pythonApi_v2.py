from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from global_enums import init_text_art
from commands import Commands
from lexer import CustomLexer

commands = Commands()
session = PromptSession()

print(init_text_art)

while True:
    text = session.prompt("# ", lexer = PygmentsLexer(CustomLexer))
    commands.execute(text)
