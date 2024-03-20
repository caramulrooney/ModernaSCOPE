from session_runner import SessionRunner
from config import Config
import argparse

parser = argparse.ArgumentParser("config")
parser.add_argument("config", nargs = "*", default = ["config.json"])
args = parser.parse_args()
Config.set_config(args.config[0])

session_runner = SessionRunner()
session_runner.run_session()
