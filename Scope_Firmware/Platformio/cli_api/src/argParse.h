#pragma once
#include <Arduino.h>

#include "defines.h"

void selectRange(unsigned int electrode1, unsigned int electrode2, bool electrodes[], rangeSelectionType rangeType);

bool parseBattleshipNotation(String input, unsigned int *returnElectrodeId);

bool parseElectrodeInput(String input, bool electrodes[], rangeSelectionType rangeType);
