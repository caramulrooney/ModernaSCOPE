import constants
from constants import SelectionType

class ElectrodeNames():
    @classmethod
    def __id_to_row_col(cls, electrode_id: int) -> tuple[int, int]:
        row = electrode_id // constants.N_COLUMNS
        col = electrode_id %  constants.N_COLUMNS
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

        return list(filter(is_electrode_in_range, range(constants.N_ELECTRODES)))

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
                assert battleship[0] in constants.ROW_LETTERS.lower()
                row_num = constants.ROW_LETTERS.lower().index(battleship[0])
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

    @classmethod
    def parse_electrode_input(cls, input: str, selection_type: SelectionType = SelectionType.ROW_WISE) -> list[int]:
        """
        Given a string containing one or more comma-separated ranges, such as `'A1-B5,H4-H9'`, return a list of the electrode ids contained withing the range, where each electrode id is an integer between 0 and 95. Do not accept any additional characters other than `-` and `,`. Electrode range is case-insensitve. Print an error message if parsing is not successful.
        """

        if input == "all":
            return list(range(constants.N_ELECTRODES))
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
            row = constants.ROW_LETTERS[electrode_id // constants.N_COLUMNS]
            column = str((electrode_id % constants.N_COLUMNS) + 1)
            output = output + row + column

        return output.upper()

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
