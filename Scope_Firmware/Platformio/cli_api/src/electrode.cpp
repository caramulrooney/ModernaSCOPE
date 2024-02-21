#include "electrode.h"

#include <Arduino.h>
#include <StringSplitter.h>

#include "argParse.h"
#include "calibration.h"
#include "defines.h"

CalibrationHistory calibrations;

float temperature = 293;  // TODO: actually measure temperature

void calibrate(bool electrodes[], float pH) {
    float voltages[N_ELECTRODES];
    measureVoltage(voltages);
    for (unsigned int i = 0; i < N_ELECTRODES; i++) {
        if (electrodes[i]) {
            calibrations.addDatum(i, pH, voltages[i], temperature);
        }
    }
}

bool measurePh(float phValues[]) {
    float voltages[N_ELECTRODES];
    bool returnVal = measureVoltage(voltages);

    for (unsigned int i = 0; i < N_ELECTRODES; i++) {
        // phValues[i] = (voltages[i] - calibrationVoltage[i])
        phValues[i] = (voltages[i]);
    }
    return returnVal;
}

bool measureVoltage(float* voltages[]) { return true; }
