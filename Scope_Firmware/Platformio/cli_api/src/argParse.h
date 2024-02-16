#pragma once
#include <Arduino.h>

#include "defines.h"

/**
 * Populate selected electrode array for a single range of cells.
 *
 * Given a starting cell, an ending cell, and a boolean array to populate, set those values in the array to true which correspond to cells in the specified range. Three selection methods are implemented.
 *
 * `HORIZONTAL` selection starts at the starting cell and advances horizontally to the right, wrapping row-wise until it reaches the ending cell.
 *
 * `VERTICAL` selection starts at the starting cell and advances vertically downwards, wrapping column-wise until it reaches the ending cell.
 *
 * `EXCEL` selection includes only those cells with a row number between the row number of the starting cell and the row number of the ending cell, as well as a column number between the column number of the starting cell and the column number of th ending cell. Essentially, it includes all cells within a box where the starting cell is the top left corner and the ending cell is the bottom right corner. This selection method should be familiar to users of Excel or Google Sheets.
 *
 * @param electrode1 Starting cell (integer 0-95).
 * @param electrode2 Ending cell (integer 0-95).
 * @param electrodes Return array to hold boolean values for each electrode to say whether it was included in the range or not.
 * @param rangeType One of `HORIZONTAL`, `VERTICAL`, or `EXCEL` (see `selectRange` function).
 */
void selectRange(unsigned int electrode1, unsigned int electrode2, bool electrodes[], rangeSelectionType rangeType);

/**
 * Convert battleship notation (A1-H12) to electrode id (0-95).
 *
 * Given an input string representing a cell in battleship notation, place the electrode id in the returnElectrodeId variable, then return true or false based on whether the input string could be parsed or not.
 *
 * @param input String representing a cell in battleship notation (A1-H12)
 * @param returnElectrodeId Return address to store the converted electrode id (0-95)
 * @return True if the input string was properly parsed as battleship notation, false otherwise.
 */
bool parseBattleshipNotation(String input, unsigned int *returnElectrodeId);

/**
 * Parse electrode identifiers as a string input.
 *
 * Interpret an input string, such as "A1-A8,B1-B4,C1" and populate an array of 96 bools to say which ones are selected. The array to populate is passed in as the second argument. `HORIZONTAL`, `VERTICAL`, or `EXCEL` selection methods are allowed (see `selectRange` function). Return true or false based on whether the string parsing succeeded or failed.
 *
 * @param input String representing a range of electrodes, such as "B10-C3,H10-H12,D9". `-` designates a range of cells, and `,` separates distinct ranges. Spaces are not allowed.
 * @param electrodes Return array to hold boolean values for each electrode to say whether it was included in the range or not.
 * @param rangeType One of `HORIZONTAL`, `VERTICAL`, or `EXCEL` (see `selectRange` function).
 *
 * @return True if the input was parsed successfully, false otherwise.
 */
bool parseElectrodeInput(String input, bool electrodes[], rangeSelectionType rangeType);

/**
 * Convert electrode id 0-95 to position A1-H12 in 96-well plate format.
 *
 * Electrode ids start at 0=A1 and increment rightwards 1=A2, 2=A3, then downwards 12=B1, 13=B2.
 *
 * @param electrode Electrode id from 0-95.
 *
 * @return String representing the electrode id in battleship notation from A1-H12.
 */
String toBattleshipNotation(unsigned int electrode);

/**
 * Print which electrodes are selected.
 *
 * Given an array of 96 bools representing which electrodes are selected or unselected, print the id of every electrode that is selected in battleship notation.
 *
 * @param electrodes Array of of 96 bools representing which electrodes are selected.
 */
void printElectrodeRange(bool electrodes[]);
