from enum import Enum

N_ELECTRODES = 96
N_COLUMNS = 12
N_ROWS = 8
ROW_LETTERS = "ABCDEFGH"
COL_NUMBERS = "0123456789"
ALL_ELECTRODES_KEYWORD = "all"

class SelectionType(Enum):
    ROW_WISE = 0
    COLUMN_WISE = 1
    EXCEL_LIKE = 2

init_text_art = """

___  ___      _ _   _       _              ______ _   _     _____
|  \/  |     | | | (_)     | |             | ___ \ | | |   /  ___|
| .  . |_   _| | |_ _ _ __ | | _____  __   | |_/ / |_| |   \ `--.  ___ _ __  ___  ___  _ __
| |\/| | | | | | __| | '_ \| |/ _ \ \/ /   |  __/|  _  |    `--. \/ _ \ '_ \/ __|/ _ \| '__|
| |  | | |_| | | |_| | |_) | |  __/>  <    | |   | | | |   /\__/ /  __/ | | \__ \ (_) | |
\_|  |_/\__,_|_|\__|_| .__/|_|\___/_/\_\   \_|   \_| |_/   \____/ \___|_| |_|___/\___/|_|
                     | |
                     |_|

"""
