from global_enums import SelectionType, Constants

def select_range(battleship_range: str, selection_type: SelectionType) -> list[int]:
    try:
        battleships = battleship_range.split("-")
        assert len(battleships) == 2
        start = from_battleship_notation(battleships[0])
        end = from_battleship_notation(battleships[1])
    except AssertionError:
        print(f"Could not parse electrode input '{battleship_range}'. Reason: range must contain exactly one '-' character.")

    tmp_start_row = start // Constants.N_COLUMNS
    tmp_end_row   = end   // Constants.N_COLUMNS
    tmp_start_col = start %  Constants.N_COLUMNS
    tmp_end_col   = end   %  Constants.N_COLUMNS

    # ensure that start_row and start_col are always smaller than end_row and end_col
    start_row = min(tmp_start_row, tmp_end_row)
    end_row   = max(tmp_start_row, tmp_end_row)
    start_col = min(tmp_start_col, tmp_end_col)
    end_col   = max(tmp_start_col, tmp_end_col)

    def is_electrode_in_range(row: int, col: int) -> bool:
        if selection_type == SelectionType.ROW_WISE:
            if start_row == end_row:
                return start_col <= col <= end_col
            return (start_row < row < end_row) or (row == start_row and col >= start_col) or (row == end_row and col <= end_col)
        elif selection_type == SelectionType.COLUMN_WISE:
            if start_col == end_col:
                return start_row <= row <= end_row
            return (start_col < col < end_col) or (col == start_col and row >= start_row) or (col == end_col and row <= end_row)
        elif selection_type == SelectionType.EXCEL_LIKE:
            return row >= start_row and row <= end_row and col >= start_col and col <= end_col

    return list(is_electrode_in_range, filter(range(Constants.N_ELECTRODES)))

def from_battleship_notation(battleship: str) -> int:
    # first case: a raw number
    if battleship.isdigit():
        electrode_id = int(battleship)
    else:
        try:
            # second case: battleship notation
            assert battleship[0] in Constants.ROW_LETTTERS
            row_num = Constants.ROW_LETTTERS.index(battleship[0])
            assert battleship[1:].isdigit()
            col_num = int(battleship[1:])
            electrode_id = row_num * Constants.N_COLUMNS + col_num - 1
        except AssertionError:
            print(f"Could not parse electrode input '{battleship}'")
            return 0
    if electrode_id >= 0 and electrode_id < Constants.N_ELECTRODES:
        return electrode_id
    # else:
    print(f"Parsed an electrode input '{battleship} that was out of bounds (evaluated to {electrode_id}).")
    return 0

def parse_electrode_input(input: str) -> list[int]:
    electrode_ids = []
    for battleship in input.split(","):
        if "-" in battleship:
            electrode_ids.extend(select_range(battleship))
        else:
            electrode_ids.append(from_battleship_notation(battleship))
    return electrode_ids

def to_battleship_notation(electrode_ids: list[int]) -> str:
      output = ""
      for idx, electrode_id in enumerate(electrode_ids):
        if idx != 0:
             output = output + ", "
        row = Constants.ROW_LETTTERS[electrode_id // Constants.N_COLUMNS]
        column = str((electrode_id % Constants.N_COLUMNS) + 1)
        output = output + row + column

      return output


# String rowLetters = "abcdefgh";
# String numeric = "0123456789";

# // TODO: Make this work for upper right and lower left for excel selection method
# void selectRange(unsigned int electrode1, unsigned int electrode2, bool electrodes[], rangeSelectionType rangeType) {
#     Serial.println("Electrode 1: " + String(electrode1) + ", Electrode 2: " + String(electrode2));
#     unsigned int row1 = min(electrode1, electrode2) / N_COLUMNS;
#     unsigned int col1 = min(electrode1, electrode2) % N_COLUMNS;
#     unsigned int row2 = max(electrode1, electrode2) / N_COLUMNS;
#     unsigned int col2 = max(electrode1, electrode2) % N_COLUMNS;
#     for (unsigned int row = 0; row < N_ROWS; row++) {
#         for (unsigned int col = 0; col < N_COLUMNS; col++) {
#             if ((rangeType == HORIZONTAL && ((row1 == row2 && row == row1 && col >= col1 && col <= col2) || (row1 != row2 && ((row == row1 && col >= col1) || (row > row1 && row < row2) || (row == row2 && col <= col2))))) ||
#                 (rangeType == VERTICAL && ((col1 == col2 && col == col1 && row >= row1 && row <= row2) || (col1 != col2 && ((col == col1 && row >= row1) || (col > col1 && col < col2) || (col == col2 && row <= row2))))) ||
#                 (rangeType == EXCEL && ((col1 <= col2 && (col >= col1 && row >= row1 && col <= col2 && row <= row2)) || ((col1 > col2 && (col <= col1 && row >= row1 && col >= col2 && row <= row2)))))) {
#                 Serial.println("Row = " + String(row) + ", Col = " + String(col));
#                 electrodes[row * N_COLUMNS + col] = true;
#             }
#         }
#     }
# }

# bool parseBattleshipNotation(String input, unsigned int *returnElectrodeId) {
#     // if the electrode id is a number from 0 to 95, use that number.
#     if (numeric.indexOf(input.charAt(0)) >= 0) {
#         int electrodeId = input.toInt();
#         if (electrodeId >= 0 && electrodeId < N_ELECTRODES) {
#             *returnElectrodeId = electrodeId;
#             return true;
#         }
#     }
#     // otherwise, try to parse it in battleship notation.
#     int letterId = rowLetters.indexOf(input[0]);
#     if (letterId < 0) {
#         Serial.println("Electrode notation not recognized (1).");
#         return false;
#     }
#     input.remove(0, 1);  // remove the first character in place
#     int numberId = input.toInt();
#     if (numberId <= 0 || numberId > N_COLUMNS) {
#         Serial.println("Electrode notation not recognized (2).");
#         return false;
#     }
#     int electrodeId = letterId * N_COLUMNS + numberId - 1;
#     if (electrodeId < 0 || electrodeId >= N_ELECTRODES) {
#         Serial.println("Error parsing electrode notation. Please use either a number 0-95, or battleship notation A1-H12.");
#         return false;
#     }
#     *returnElectrodeId = electrodeId;
#     return true;
# }

# bool parseElectrodeInput(String input, bool electrodes[], rangeSelectionType rangeType) {
#     input.toLowerCase();  // convert the string in place
#     if (input.equals("all")) {
#         for (unsigned int i = 0; i < N_ELECTRODES; i++) {
#             electrodes[i] = true;
#         }
#         return true;
#     } else {  // set all electrodes to unselected
#         for (unsigned int i = 0; i < N_ELECTRODES; i++) {
#             electrodes[i] = false;
#         }
#     }
#     StringSplitter *commaSplitter = new StringSplitter(input, ',', N_ELECTRODES);
#     // for each comma-separated value
#     for (int i = 0; i < commaSplitter->getItemCount(); i++) {
#         StringSplitter *hyphenSplitter = new StringSplitter(commaSplitter->getItemAtIndex(i), '-', 2);
#         if (hyphenSplitter->getItemCount() == 0) {
#             // pass
#         } else if (hyphenSplitter->getItemCount() == 1) {
#             unsigned int electrodeId;
#             if (parseBattleshipNotation(hyphenSplitter->getItemAtIndex(0), &electrodeId)) {
#                 electrodes[electrodeId] = true;
#             } else {
#                 return false;
#             }
#         } else if (hyphenSplitter->getItemCount() == 2) {
#             unsigned int electrode1;
#             if (!parseBattleshipNotation(hyphenSplitter->getItemAtIndex(0), &electrode1)) {
#                 return false;
#             }
#             unsigned int electrode2;
#             if (!parseBattleshipNotation(hyphenSplitter->getItemAtIndex(1), &electrode2)) {
#                 return false;
#             }
#             selectRange(electrode1, electrode2, electrodes, rangeType);
#         } else {
#             Serial.println("When specifiying electrode ranges, please use no more than 2 elements.");
#         }
#         delete hyphenSplitter;
#     }
#     delete commaSplitter;

#     return true;
# }

# String toBattleshipNotation(unsigned int electrode) {
#     String battleship = rowLetters.charAt(electrode / N_COLUMNS) + String(electrode % N_COLUMNS + 1);
#     battleship.toUpperCase();
#     return battleship;
# }

# void printElectrodeRange(bool electrodes[]) {
#     Serial.print("Selected electrodes: ");
#     for (unsigned int i = 0; i < N_ELECTRODES; i++) {
#         if (electrodes[i]) {
#             Serial.print(toBattleshipNotation(i));
#             Serial.print(", ");
#         }
#     }
#     Serial.println();
# }
