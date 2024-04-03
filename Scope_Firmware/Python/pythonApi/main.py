from session_runner import SessionRunner
from config import Config
import argparse
from threading import Thread, Event, Timer

# parse command line arguments
parser = argparse.ArgumentParser("config")
parser.add_argument("-c", "--config", type = str, default = "settings/config.json")
parser.add_argument("-d", "--mkdirs", action = "store_true")
args = parser.parse_args()
Config.set_config(args.config, args.mkdirs)

class IntervalTimer(Timer):
    def __init__(self, *args, daemon = True, **kwargs):
        """
        Add option to set daemon property during initialization.
        """
        super().__init__(*args, **kwargs)
        self.daemon = daemon

    def run(self):
        """
        Run indefinitely. Restart the timer as soon as it has elapased.
        """
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class Counter():
    val = 0
    def update(self):
        print(self.val)
        self.val += 1

myCounter = Counter()
background_task = IntervalTimer(1, myCounter.update, daemon = True).start()
session_runner = SessionRunner()
session_runner.run_session()
