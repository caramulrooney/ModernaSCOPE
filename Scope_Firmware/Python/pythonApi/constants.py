from enum import Enum
import datetime as dt

# electrode plate dimensions
N_ELECTRODES = 96
N_COLUMNS = 12
N_ROWS = 8

# used for pattern matching during electrode range parsing
ROW_LETTERS = "ABCDEFGH"
COL_NUMBERS = "0123456789"

# string to refer to all electrodes during electrode range parsing
ALL_ELECTRODES_KEYWORD = "all"
# delimiter for command line arguments
CLI_SPLIT_CHARS = " "

# conversion for timing units
SECONDS_TO_MILLISECONDS = 1000

# raise a warning if fewer than this number of calibration data points would be used in a conversion
MIN_CALIBRATIONS_RECOMMENDED = 3
# treat calibration data as duplicates if two calibrations were performed with pH within this amount of each other
PH_EPSILON = 0.5

class SelectionType(Enum):
    """
    Used to determine parsing behavior on an electrode range.

    For `ROW_WISE` selection, start at the start cell and move rightward until the end cell is reached, wrapping right-to-left as necessary. For `A1-B2`, return the electrode ids corresponding to [A1, A2, ... A12, B1, B2].

    For `COLUMN_WISE` selection, start at the start cell and move downward until the end cell is reached, wrapping bottom-to-top as necessary. For `A1-B2`, return the electrode ids corresponding to [A1, B1, C1, ... H1, A2, B2].

    For `EXCEL_LIKE` selection, select cells in a box, with the start cell as the top-left corner and the end cell as the bottom-right corner. For `A1-B2`, return the electrode ids corresponding to [A1, A2, B1, B2].
    """
    ROW_WISE = 0
    COLUMN_WISE = 1
    EXCEL_LIKE = 2

# string identifiers used in parsing electrode range selection type
# prefixes are also allowed
selection_type_names = {
    "rowwise": SelectionType.ROW_WISE,
    "row_wise": SelectionType.ROW_WISE,
    "columnwise": SelectionType.COLUMN_WISE,
    "column_wise": SelectionType.COLUMN_WISE,
    "excellike": SelectionType.EXCEL_LIKE,
    "excel_like": SelectionType.EXCEL_LIKE,
    "excelwise": SelectionType.EXCEL_LIKE,
    "excel_wise": SelectionType.EXCEL_LIKE,
}

# https://patorjk.com/software/taag/#p=display&f=Doom&t=Multiplex%20%20%20PH%20%20%20Sensor
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
