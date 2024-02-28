from prompt_toolkit import PromptSession
from commands import Commands

session = PromptSession()

commands = Commands()
# text = session.prompt("What would you like to say?\n")
# text = "measure --electrod 9 --now --max_time 120"
text = "clear_calibration --electrod 9 --all"
# text = "calibrate 9"
# text = "calibrate -h"
commands.execute(text)
