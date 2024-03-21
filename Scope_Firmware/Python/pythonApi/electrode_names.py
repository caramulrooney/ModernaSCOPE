from constants import SelectionType, selection_type_names, N_COLUMNS, N_ELECTRODES, ROW_LETTERS, ALL_ELECTRODES_KEYWORD
import numpy as np
from typing import Optional

class ElectrodeNameParseError(ValueError):
    """
    Represents an electrode name parsing error.
    """

class ElectrodeNames():
    """
    Collection of functions for converting electrode names back and forth between battleship notation (A1-H12) and electrode ids (0-95). This class contains only class methods, so it never needs to be instantiated.
    """

    @classmethod
    def __id_to_row_col(cls, electrode_id: int) -> tuple[int, int]:
        """
        Given an electrode id, such as `0` or `95`, return a tuple indicating the corresponding row and column of the electrode, such as (0, 0) or (7, 11).
        """
        row = electrode_id // N_COLUMNS
        col = electrode_id %  N_COLUMNS
        return row, col

    @classmethod
    def __select_range(cls, input: str) -> list[int]:
        """
        Given a string representing two electrodes separated by a `-`, for example `A1-B5`, return a list of the electrodes that fall within that range using the appropriate selection method. The order of the electrodes doesn't matter, as they are sorted before being used. In addition to a range, a ':' may be used to denote a selection type, such as `A1-B5:excel`.

        For `ROW_WISE` selection, start at the start cell and move rightward until the end cell is reached, wrapping right-to-left as necessary. For `A1-B2`, return the electrode ids corresponding to [A1, A2, ... A12, B1, B2].

        For `COLUMN_WISE` selection, start at the start cell and move downward until the end cell is reached, wrapping bottom-to-top as necessary. For `A1-B2`, return the electrode ids corresponding to [A1, B1, C1, ... H1, A2, B2].

        For `EXCEL_LIKE` selection, select cells in a box, with the start cell as the top-left corner and the end cell as the bottom-right corner. For `A1-B2`, return the electrode ids corresponding to [A1, A2, B1, B2].

        Default selection type is `EXCEL_LIKE`. A selection type is specified with a ':' and any prefix of a selection type name, such as `A1-B5:c`, `A1-B5:col`, or `A1-B5:column_wise`. The selection type may also be placed in front of the range, as in `c:A1-B5`.
        """
        selection_type_parts = input.split(":")
        if len(selection_type_parts) > 1:
            try:
                assert len(selection_type_parts) == 2
                parsed_selection_type = cls.__parse_selection_type(selection_type_parts[0])
                if parsed_selection_type is not None:
                    selection_type = parsed_selection_type
                    battleship_range = selection_type_parts[1]
                else:
                    parsed_selection_type = cls.__parse_selection_type(selection_type_parts[1])
                    assert parsed_selection_type is not None
                    selection_type = parsed_selection_type
                    battleship_range = selection_type_parts[0]
            except AssertionError:
                raise ElectrodeNameParseError(f"Could not parse electrode input '{input}'. Reason: range may contain exactly one ':', and first or second argument must be a selection type ('excel_like', 'row_wise', or 'column_wise').")
        else:
            selection_type = SelectionType.EXCEL_LIKE
            battleship_range = input

        try:
            battleships = battleship_range.split("-")
            assert len(battleships) == 2
            start = cls.__from_battleship_notation(battleships[0])
            end = cls.__from_battleship_notation(battleships[1])
        except AssertionError:
            raise ElectrodeNameParseError(f"Could not parse electrode input '{battleship_range}'. Reason: range must contain exactly one '-' character.")

        tmp_start_row, tmp_start_col = cls.__id_to_row_col(start)
        tmp_end_row, tmp_end_col = cls.__id_to_row_col(end)

        # ensure that start_row and start_col are always smaller than end_row and end_col
        start_row = min(tmp_start_row, tmp_end_row)
        end_row   = max(tmp_start_row, tmp_end_row)
        start_col = min(tmp_start_col, tmp_end_col)
        end_col   = max(tmp_start_col, tmp_end_col)

        def is_electrode_in_range(electrode_id: int) -> bool:
            row, col = cls.__id_to_row_col(electrode_id)

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

        return list(filter(is_electrode_in_range, range(N_ELECTRODES)))

    @classmethod
    def __from_battleship_notation(cls, battleship: str) -> int:
        """
        Given a 2 or 3 character string containing a single battleship notation, such as `A1` or `B12`, convert it into an integer representing the elecrode id, such as `0` or `23`. Also accept a string representing a raw integer 0-95 and returns that integer. If parsing fails, print an error message to the screen and raise an ElectrodeNameParseError.
        """
        battleship = battleship.lower()

        # first case: a raw number
        if battleship.isdigit():
            electrode_id = int(battleship)
        else:
            try:
                # second case: battleship notation
                assert battleship[0] in ROW_LETTERS.lower()
                row_num = ROW_LETTERS.lower().index(battleship[0])
                assert battleship[1:].isdigit()
                col_num = int(battleship[1:])
                electrode_id = row_num * N_COLUMNS + col_num - 1
            except AssertionError:
                raise ElectrodeNameParseError(f"Could not parse electrode input '{battleship}'")
        if electrode_id >= 0 and electrode_id < N_ELECTRODES:
            return electrode_id
        raise ElectrodeNameParseError(f"Parsed an electrode input '{battleship} that was out of bounds (evaluated to {electrode_id}).")

    @classmethod
    def parse_electrode_input(cls, input: str) -> list[int]:
        """
        Given a string containing one or more comma-separated ranges, such as `'A1-B5,H4-H9'`, return a list of the electrode ids contained withing the range, where each electrode id is an integer between 0 and 95. Do not accept any additional characters other than `-` and `,`. Electrode range is case-insensitve. Print an error message if parsing is not successful.
        """

        if input == ALL_ELECTRODES_KEYWORD:
            return list(range(N_ELECTRODES))

        electrode_ids = []
        for battleship in input.split(","):
            if "-" in battleship:
                electrode_ids.extend(cls.__select_range(battleship))
            else:
                electrode_ids.append(cls.__from_battleship_notation(battleship))
        return electrode_ids

    @classmethod
    def __parse_selection_type(cls, input: str) -> Optional[SelectionType]:
        """
        Check whether a given string is a selection type designator. If it is, return the selection type it corresponds to. If it is not, return None. A selection type designator is a prefix for any of the keys in constants.selection_type_names.
        """
        for selection_str in selection_type_names.keys():
            if selection_str.startswith(input):
                return selection_type_names[selection_str]
        return None

    @classmethod
    def to_battleship_notation(cls, electrode_ids: list[int]) -> str:
        """
        Given a list of electrode ids, such as `[0, 1, 2, 3]`, return a string containing a pretty-print of all the electrodes, for example `A1, A2, A3, A4"`.
        """
        output = ""
        for idx, electrode_id in enumerate(electrode_ids):
            if idx != 0:
                output = output + ", "
            row = ROW_LETTERS[electrode_id // N_COLUMNS]
            column = str((electrode_id % N_COLUMNS) + 1)
            output = output + row + column

        return output.upper()

    @classmethod
    def ascii_art_electrode_ids(cls) -> None:
        """
        Draw a diagram of the electrode using ASCII art, where each electrode is labeled with its numerical electrode_id. Print the result to the terminal immediately.
        """
        print(cls.electrode_ascii_art(["~ " + str(x) + " ~" for x in range(N_ELECTRODES)]))

    @classmethod
    def ascii_art_selected(cls, electrode_ids: list[int]) -> None:
        """
        Draw a diagram of the electrode using ASCII art, with each electrode either displaying 'Yes' if it is selected or a placeholder if it is not. As input, take a list of integers representing which electrode ids are selected, such as [0, 1, 2] or [50, 45, 95]. Print the result to the terminal immediately.
        """
        selected = []
        for electrode_id in range(N_ELECTRODES):
            if electrode_id in electrode_ids:
                selected.append("Yes")
            else:
                selected.append(".")
        print(cls.electrode_ascii_art(selected))

    @classmethod
    def electrode_ascii_art(cls, vals: any) -> str:
        """
        Draw a diagram of the electrode using ASCII art, with a certain string being displayed for each electrode. As input, take a list of N_ELECTRODES strings, each of which must be at most 7 characters long. Return a multi-line string containing the ASCII art.
        """
        assert len(vals) == N_ELECTRODES

        max_len = 7
        v = [] # must have a one-character name
        for val in vals:
            if val is None:
                val = "."
            if not isinstance(vals, str):
                vals = str(vals)
            assert len(val) <= max_len
            v.append(" " * int(np.ceil((max_len - len(val)) / 2)) + val + " " * int(np.floor((max_len - len(val)) / 2)))

        return f"""
               1       2      3        4       5       6       7       8       9       10      11      12
          _______________________________________________________________________________________________________
         /                                                                                                       |
        /                                                                                                        |
  A    /    {v[ 0]} {v[ 1]} {v[ 2]} {v[ 3]} {v[ 4]} {v[ 5]} {v[ 6]} {v[ 7]} {v[ 8]} {v[ 9]} {v[10]} {v[11]}      |
      /                                                                                                          |
  B   |     {v[12]} {v[13]} {v[14]} {v[15]} {v[16]} {v[17]} {v[18]} {v[19]} {v[20]} {v[21]} {v[22]} {v[23]}      |
      |                                                                                                          |
  C   |     {v[24]} {v[25]} {v[26]} {v[27]} {v[28]} {v[29]} {v[30]} {v[31]} {v[32]} {v[33]} {v[34]} {v[35]}      |
      |                                                                                                          |
  D   |     {v[36]} {v[37]} {v[38]} {v[39]} {v[40]} {v[41]} {v[42]} {v[43]} {v[44]} {v[45]} {v[46]} {v[47]}      |
      |                                                                                                          |
  E   |     {v[48]} {v[49]} {v[50]} {v[51]} {v[52]} {v[53]} {v[54]} {v[55]} {v[56]} {v[57]} {v[58]} {v[59]}      |
      |                                                                                                          |
  F   |     {v[60]} {v[61]} {v[62]} {v[63]} {v[64]} {v[65]} {v[66]} {v[67]} {v[68]} {v[69]} {v[70]} {v[71]}      |
      |                                                                                                          |
  G   |     {v[72]} {v[73]} {v[74]} {v[75]} {v[76]} {v[77]} {v[78]} {v[79]} {v[80]} {v[81]} {v[82]} {v[83]}      |
      |                                                                                                          |
  H   |     {v[84]} {v[85]} {v[86]} {v[87]} {v[88]} {v[89]} {v[90]} {v[91]} {v[92]} {v[93]} {v[94]} {v[95]}      |
      |                                                                                                          |
      |__________________________________________________________________________________________________________|
"""

    @classmethod
    def run_unit_tests(cls):
        """
        Run a collection of unit tests on the core functionality of the functions in this class.
        """
        print("Starting unit tests for from_battleship_notation()")
        assert cls.__from_battleship_notation("A1") == 0
        assert cls.__from_battleship_notation("A5") == 4
        assert cls.__from_battleship_notation("H12") == 95
        assert cls.__from_battleship_notation("C10") == 2 * 12 + 9

        print("Starting unit tests for to_battleship_notation()")
        assert cls.to_battleship_notation([0]) == "A1"
        assert cls.to_battleship_notation([4]) == "A5"
        assert cls.to_battleship_notation([94, 95]) == "H11, H12"
        assert cls.to_battleship_notation([0, 1, 2 * 12 + 9]) == "A1, A2, C10"

        print("Starting unit tests for select_range()")
        assert sorted(cls.__select_range("A1-B2", SelectionType.ROW_WISE)) == sorted([cls.__from_battleship_notation(x) for x in "A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, A12, B1, B2".split(", ")])
        assert sorted(cls.__select_range("A1-B2", SelectionType.COLUMN_WISE)) == sorted([cls.__from_battleship_notation(x) for x in "A1, A2, B1, B2, C1, D1, E1, F1, G1, H1".split(", ")])
        assert sorted(cls.__select_range("A1-B2", SelectionType.EXCEL_LIKE)) == sorted([cls.__from_battleship_notation(x) for x in "A1, B1, A2, B2".split(", ")])

        print("Starting unit tests for parse_electrode_input()")
        assert sorted(cls.parse_electrode_input("A1-B2,H4-H6", SelectionType.ROW_WISE)) == sorted([cls.__from_battleship_notation(x) for x in "A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, A12, B1, B2, H4, H5, H6".split(", ")])
        assert sorted(cls.parse_electrode_input("A1-B2,C5-E5,D9", SelectionType.COLUMN_WISE)) == sorted([cls.__from_battleship_notation(x) for x in "A1, A2, B1, B2, C1, D1, E1, F1, G1, H1, C5, D5, E5, D9".split(", ")])
        assert sorted(cls.parse_electrode_input("H11,A1-B2,H12", SelectionType.EXCEL_LIKE)) == sorted([cls.__from_battleship_notation(x) for x in "A1, B1, A2, B2, H11, H12".split(", ")])
