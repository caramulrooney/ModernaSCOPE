#include <Arduino.h>
#include <StringSplitter.h>

#include "argParse.h"
#include "defines.h"
#include "electrode.h"

void calibrate(bool electrodes[], float pH) {}

bool measurePh(float phValues[]) {
    float voltages[N_ELECTRODES];
    bool returnVal = measureVoltage(voltages);

    for (unsigned int i = 0; i < N_ELECTRODES; i++) {
        // phValues[i] = (voltages[i] - calibrationVoltage[i])
        phValues[i] = (voltages[i] - 0);
    }
    return returnVal;
}

bool measureVoltage(float voltages[]) { return true; }
