import constants
from constants import SelectionType

def id_to_row_col(electrode_id: int) -> tuple[int, int]:
    row = electrode_id // constants.N_COLUMNS
    col = electrode_id %  constants.N_COLUMNS
    return row, col

def select_range(battleship_range: str, selection_type: SelectionType) -> list[int]:
    try:
        battleships = battleship_range.split("-")
        assert len(battleships) == 2
        start = from_battleship_notation(battleships[0])
        end = from_battleship_notation(battleships[1])
    except AssertionError:
        print(f"Could not parse electrode input '{battleship_range}'. Reason: range must contain exactly one '-' character.")

    tmp_start_row, tmp_start_col = id_to_row_col(start)
    tmp_end_row, tmp_end_col = id_to_row_col(end)

    # ensure that start_row and start_col are always smaller than end_row and end_col
    start_row = min(tmp_start_row, tmp_end_row)
    end_row   = max(tmp_start_row, tmp_end_row)
    start_col = min(tmp_start_col, tmp_end_col)
    end_col   = max(tmp_start_col, tmp_end_col)

    def is_electrode_in_range(electrode_id: int) -> bool:
        row, col = id_to_row_col(electrode_id)

        if selection_type == SelectionType.ROW_WISE:
            if row == start_row == end_row:
                return start_col <= col <= end_col
            return (start_row < row < end_row) or (row == start_row and col >= start_col) or (row == end_row and col <= end_col)
        elif selection_type == SelectionType.COLUMN_WISE:
            if col == start_col == end_col:
                return start_row <= row <= end_row
            return (start_col < col < end_col) or (col == start_col and row >= start_row) or (col == end_col and row <= end_row)
        elif selection_type == SelectionType.EXCEL_LIKE:
            return row >= start_row and row <= end_row and col >= start_col and col <= end_col

    return list(filter(is_electrode_in_range, range(constants.N_ELECTRODES)))

def from_battleship_notation(battleship: str) -> int:
    # first case: a raw number
    if battleship.isdigit():
        electrode_id = int(battleship)
    else:
        try:
            # second case: battleship notation
            assert battleship[0] in constants.ROW_LETTERS
            row_num = constants.ROW_LETTERS.index(battleship[0])
            assert battleship[1:].isdigit()
            col_num = int(battleship[1:])
            electrode_id = row_num * constants.N_COLUMNS + col_num - 1
        except AssertionError:
            print(f"Could not parse electrode input '{battleship}'")
            return 0
    if electrode_id >= 0 and electrode_id < constants.N_ELECTRODES:
        return electrode_id
    # else:
    print(f"Parsed an electrode input '{battleship} that was out of bounds (evaluated to {electrode_id}).")
    return 0

def parse_electrode_input(input: str, selection_type: SelectionType = SelectionType.ROW_WISE) -> list[int]:
    electrode_ids = []
    for battleship in input.split(","):
        if "-" in battleship:
            electrode_ids.extend(select_range(battleship, selection_type))
        else:
            electrode_ids.append(from_battleship_notation(battleship))
    return electrode_ids

def to_battleship_notation(electrode_ids: list[int]) -> str:
      output = ""
      for idx, electrode_id in enumerate(electrode_ids):
        if idx != 0:
             output = output + ", "
        row = constants.ROW_LETTERS[electrode_id // constants.N_COLUMNS]
        column = str((electrode_id % constants.N_COLUMNS) + 1)
        output = output + row + column

      return output
