#pragma once
#include <Arduino.h>

#define N_ELECTRODES 96
#define N_ROWS 8
#define N_COLUMNS 12
#define MAX_CALIBRATION_DATUMS 5

enum rangeSelectionType {
    HORIZONTAL,
    VERTICAL,
    EXCEL
};
