#include <Arduino.h>
#include <StringSplitter.h>

#include "argParse.h"
#include "defines.h"

void selectRange(unsigned int electrode1, unsigned int electrode2, bool electrodes[], rangeSelectionType rangeType) {
    unsigned int row1 = electrode1 % N_COLUMNS;
    unsigned int col1 = electrode1 / N_COLUMNS;
    unsigned int row2 = electrode1 % N_COLUMNS;
    unsigned int col2 = electrode1 / N_COLUMNS;
    for (unsigned int row = 0; row < N_ROWS; row++) {
        for (unsigned int col = 0; col < N_COLUMNS; col++) {
            if ((rangeType == HORIZONTAL && ((row == row1 && col >= col1) || (row > row1 && row <= row2) || (row == row2 && col <= col2))) ||
                (rangeType == VERTICAL && ((col == col1 && row >= row1) || (col > col1 && col <= col2) || (col == col2 && row <= row2))) ||
                (rangeType == EXCEL && ((col >= col1 && row >= row1 && col <= col2 && row <= row2)))) {
                electrodes[row * N_COLUMNS + col] = true;
            }
        }
    }
}

bool parseBattleshipNotation(String input, unsigned int *returnElectrodeId) {
    // if the electrode id is a number from 0 to 95, use that number.
    if (numeric.indexOf(input.charAt(0)) >= 0) {
        int electrodeId = input.toInt();
        if (electrodeId >= 0 && electrodeId < N_ELECTRODES) {
            *returnElectrodeId = electrodeId;
            return true;
        }
    }
    // otherwise, try to parse it in battleship notation.
    int letterId = rowLetters.indexOf(input[0]);
    if (letterId < 0) {
        Serial.println("Electrode notation not recognized.");
        return false;
    }
    input.remove(0, 1);  // remove the first character in place
    int numberId = input.toInt();
    if (numberId <= 0 || numberId > N_COLUMNS) {
        Serial.println("Electrode notation not recognized.");
        return false;
    }
    int electrodeId = letterId * N_COLUMNS + numberId - 1;
    if (electrodeId < 0 || electrodeId >= N_ELECTRODES) {
        Serial.println("Error parsing electrode notation. Please use either a number 0-95, or battleship notation A1-H12.");
        return false;
    }
    *returnElectrodeId = electrodeId;
    return true;
}

bool parseElectrodeInput(String input, bool electrodes[], rangeSelectionType rangeType) {
    input.toLowerCase();  // convert the string in place
    if (input.equals("all")) {
        for (unsigned int i = 0; i < N_ELECTRODES; i++) {
            electrodes[i] = true;
        }
        return true;
    } else {  // set all electrodes to unselected
        for (unsigned int i = 0; i < N_ELECTRODES; i++) {
            electrodes[i] = false;
        }
    }
    StringSplitter *commaSplitter = new StringSplitter(input, ',', N_ELECTRODES);
    // for each comma-separated value
    for (int i = 0; i < commaSplitter->getItemCount(); i++) {
        StringSplitter *hyphenSplitter = new StringSplitter(commaSplitter->getItemAtIndex(i), '-', 2);
        if (hyphenSplitter->getItemCount() == 0) {
            // pass
        } else if (hyphenSplitter->getItemCount() == 1) {
            unsigned int electrodeId;
            if (parseBattleshipNotation(hyphenSplitter->getItemAtIndex(0), &electrodeId)) {
                electrodes[electrodeId] = true;
                Serial.print(electrodeId);
                Serial.print(" ");
                return true;
            } else {
                return false;
            }
        } else if (hyphenSplitter->getItemCount() == 2) {
            unsigned int electrode1;
            if (!parseBattleshipNotation(hyphenSplitter->getItemAtIndex(0), &electrode1)) {
                return false;
            }
            unsigned int electrode2;
            if (!parseBattleshipNotation(hyphenSplitter->getItemAtIndex(0), &electrode2)) {
                return false;
            }
            selectRange(electrode1, electrode2, electrodes, rangeType);
        } else {
            Serial.println("When specifiying electrode ranges, please use no more than 2 elements.");
        }
        delete hyphenSplitter;
    }
    delete commaSplitter;

    return true;
}
