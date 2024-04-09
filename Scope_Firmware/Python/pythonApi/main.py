from session_runner import SessionRunner
from config import Config
import argparse

def main():
    Config.set_config(args.config, args.mkdirs)
    session_runner = SessionRunner()
    session_runner.run_session()

if __name__ == '__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser("config")
    parser.add_argument("-c", "--config", type = str, default = "settings/config.json")
    parser.add_argument("-d", "--mkdirs", action = "store_true")
    args = parser.parse_args()

    # run main function
    main()
