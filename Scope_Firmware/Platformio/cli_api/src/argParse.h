#pragma once
#include <Arduino.h>

#include "defines.h"

void selectRange(unsigned int electrode1, unsigned int electrode2, bool electrodes[], rangeSelectionType rangeType);

bool parseBattleshipNotation(String input, unsigned int *returnElectrodeId);

/**
 * Parse electrode identifiers as a string input.
 *
 * Interpret an input string, such as "A1-A8" and populate an array of 96 bools to say which ones are selected. The array to populate is passed in as the second argument. Return true or false based on whether the string parsing succeeded or failed.
 *
 * @param input String representing a range of electrodes, such as "B10-C3". This corresponds to electrodes B10, B11, B12, C1, C2, and C3.
 * @param electrodes Return array to hold boolean values for each electrode to say whether it was included in the range or not.
 *
 * @return True if the input was parsed successfully, false otherwise.
 */
bool parseElectrodeInput(String input, bool electrodes[], rangeSelectionType rangeType);

String toBattleshipNotation(unsigned int electrode);

void printElectrodeRange(bool electrodes[]);
