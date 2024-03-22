from session_runner import SessionRunner
from config import Config
import argparse
import asyncio

# parse command line arguments
parser = argparse.ArgumentParser("config")
parser.add_argument("-c", "--config", type = str, default = "settings/config.json")
parser.add_argument("-d", "--mkdirs", action = "store_true")
args = parser.parse_args()
Config.set_config(args.config, args.mkdirs)

async def print_counter():
    """
    Coroutine that prints counters.
    """
    try:
        i = 0
        while True:
            print("Counter: %i" % i)
            i += 1
            await asyncio.sleep(3)
    except asyncio.CancelledError:
        print("Background task cancelled.")

async def main():
    background_task = asyncio.create_task(print_counter())
    session_runner = SessionRunner()
    await session_runner.run_session()

asyncio.run(main())
