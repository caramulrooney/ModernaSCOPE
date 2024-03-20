from config import SelectionType, N_COLUMNS, N_ELECTRODES, ROW_LETTERS
import numpy as np

class ElectrodeNames():
    @classmethod
    def __id_to_row_col(cls, electrode_id: int) -> tuple[int, int]:
        row = electrode_id // N_COLUMNS
        col = electrode_id %  N_COLUMNS
        return row, col

    @classmethod
    def __select_range(cls, battleship_range: str, selection_type: SelectionType) -> list[int]:
        try:
            battleships = battleship_range.split("-")
            assert len(battleships) == 2
            start = cls.__from_battleship_notation(battleships[0])
            end = cls.__from_battleship_notation(battleships[1])
        except AssertionError:
            print(f"Could not parse electrode input '{battleship_range}'. Reason: range must contain exactly one '-' character.")

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
        Given a 2 or 3 character string containing a single battleship notation, such as `A1` or `B12`, convert it into an integer representing the elecrode id, such as `0` or `23`.
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
                print(f"Could not parse electrode input '{battleship}'")
                return 0
        if electrode_id >= 0 and electrode_id < N_ELECTRODES:
            return electrode_id
        # else:
        print(f"Parsed an electrode input '{battleship} that was out of bounds (evaluated to {electrode_id}).")
        return 0

    @classmethod
    def parse_electrode_input(cls, input: str, selection_type: SelectionType = SelectionType.ROW_WISE) -> list[int]:
        """
        Given a string containing one or more comma-separated ranges, such as `'A1-B5,H4-H9'`, return a list of the electrode ids contained withing the range, where each electrode id is an integer between 0 and 95. Do not accept any additional characters other than `-` and `,`. Electrode range is case-insensitve. Print an error message if parsing is not successful.
        """

        if input == "all":
            return list(range(N_ELECTRODES))
        electrode_ids = []
        for battleship in input.split(","):
            if "-" in battleship:
                electrode_ids.extend(cls.__select_range(battleship, selection_type))
            else:
                electrode_ids.append(cls.__from_battleship_notation(battleship))
        return electrode_ids

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
        print(cls.electrode_ascii_art(["~ " + str(x) + " ~" for x in range(N_ELECTRODES)]))

    @classmethod
    def ascii_art_selected(cls, electrode_ids: list[int]) -> None:
        selected = []
        for electrode_id in range(N_ELECTRODES):
            if electrode_id in electrode_ids:
                selected.append("Yes")
            else:
                selected.append(".")
        print(cls.electrode_ascii_art(selected))

    @classmethod
    def electrode_ascii_art(cls, vals: any) -> str:
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
