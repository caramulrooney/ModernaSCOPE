from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from constants import init_text_art
from commands import Commands
from lexer import CustomLexer, YesNoLexer
from storage import StorageWritePermissionError

def handle_storage_write_exception(func):
    def inner_func(self, *args, **kwargs):
        try:
            func(self, *args ,**kwargs)
        except StorageWritePermissionError:
            print("Could not open file for writing, likely because the file was open in a different program. Please use the 'write' command to retry, or press enter now.")
            self.retry_file_write()
    return inner_func

class SessionRunner():
    def __init__(self):
        self.commands = Commands()
        self.session = PromptSession()
        print(init_text_art)

    @handle_storage_write_exception
    def retry_file_write(self):
        while True:
            text = self.session.prompt("Retry now? [Y/n] ", lexer = PygmentsLexer(YesNoLexer))
            if text == "Y" or text == "":
                self.commands.sensor.storage.write_data()
                print(f"Wrote data successfully.")
                return
            if text == "n":
                return
            print("Invalid response.")

    @handle_storage_write_exception
    def execute(self, text):
        self.commands.execute(text)

    def run_session(self):
        while True:
            text = self.session.prompt("# ", lexer = PygmentsLexer(CustomLexer))
            self.execute(text)
