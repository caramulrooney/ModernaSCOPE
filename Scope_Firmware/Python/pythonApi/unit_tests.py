import argparse

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

print(argparse.select_range("A1-B2"), argparse.SelectionType.ROW_WISE)

print("All tests passed!")
