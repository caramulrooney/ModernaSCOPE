import argparse
from constants import SelectionType

print("Starting unit tests for from_battleship_notation()")
assert argparse.from_battleship_notation("A1") == 0
assert argparse.from_battleship_notation("A5") == 4
assert argparse.from_battleship_notation("H12") == 95
assert argparse.from_battleship_notation("C10") == 2 * 12 + 9

print("Starting unit tests for to_battleship_notation()")
assert argparse.to_battleship_notation([0]) == "A1"
assert argparse.to_battleship_notation([4]) == "A5"
assert argparse.to_battleship_notation([94, 95]) == "H11, H12"
assert argparse.to_battleship_notation([0, 1, 2 * 12 + 9]) == "A1, A2, C10"

print("Starting unit tests for select_range()")
assert sorted(argparse.select_range("A1-B2", SelectionType.ROW_WISE)) == sorted([argparse.from_battleship_notation(x) for x in "A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, A12, B1, B2".split(", ")])
assert sorted(argparse.select_range("A1-B2", SelectionType.COLUMN_WISE)) == sorted([argparse.from_battleship_notation(x) for x in "A1, A2, B1, B2, C1, D1, E1, F1, G1, H1".split(", ")])
assert sorted(argparse.select_range("A1-B2", SelectionType.EXCEL_LIKE)) == sorted([argparse.from_battleship_notation(x) for x in "A1, B1, A2, B2".split(", ")])

print("Starting unit tests for parse_electrode_input()")
assert sorted(argparse.parse_electrode_input("A1-B2,H4-H6", SelectionType.ROW_WISE)) == sorted([argparse.from_battleship_notation(x) for x in "A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, A12, B1, B2, H4, H5, H6".split(", ")])
assert sorted(argparse.parse_electrode_input("A1-B2,C5-E5,D9", SelectionType.COLUMN_WISE)) == sorted([argparse.from_battleship_notation(x) for x in "A1, A2, B1, B2, C1, D1, E1, F1, G1, H1, C5, D5, E5, D9".split(", ")])
assert sorted(argparse.parse_electrode_input("H11,A1-B2,H12", SelectionType.EXCEL_LIKE)) == sorted([argparse.from_battleship_notation(x) for x in "A1, B1, A2, B2, H11, H12".split(", ")])

print("All tests passed!")
