#pragma once
#include <Arduino.h>

#define N_ELECTRODES 96
#define N_ROWS 8
#define N_COLUMNS 12

String rowLetters = "ABCDEFGH";
String numeric = "0123456789";

enum rangeSelectionType {
    HORIZONTAL,
    VERTICAL,
    EXCEL
};
