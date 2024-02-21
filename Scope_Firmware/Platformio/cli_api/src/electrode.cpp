#include "electrode.h"

#include <Arduino.h>
#include <StringSplitter.h>

#include "argParse.h"
#include "defines.h"

CalibrationHistory calibrations;

float temperature = 293;  // room temperature

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

int phToCalibrationId(float pH) {
    return int(pH * 10);
}

float calibrationIdToPh(int calibrationId) {
    return float(calibrationId) / 10;
}

long now = 1708538423;

Calibration::Calibration() {
    for (unsigned int i = 0; i < MAX_CALIBRATION_DATUMS; i++) {
        datums[i].isValid = false;
    }
}

bool Calibration::addDatum(calibrationDatum* datum) {
    for (size_t i = 0; i < MAX_CALIBRATION_DATUMS; i++) {
        if (!datums[i].isValid || datums[i].calibrationId == datum->calibrationId) {
            datums[i] = *datum;
            return true;
        }
    }
    Serial.println("You can only assign a maximum of " + String(MAX_CALIBRATION_DATUMS) + "calibration data points. Use  the # clear_calibration command to remove old calibration datums.");
    return false;
}

bool Calibration::getDatum(int calibrationId, calibrationDatum* returnDatum) {
    for (size_t i = 0; i < MAX_CALIBRATION_DATUMS; i++) {
        if (datums[i].isValid && datums[i].calibrationId == calibrationId) {
            returnDatum = &datums[i];
            return true;
        }
    }
    Serial.println("Datum for ph = " + String(calibrationIdToPh(calibrationId)) + "was not found.");
    return false;
}

CalibrationHistory::CalibrationHistory() {
    for (unsigned int i = 0; i < N_ELECTRODES; i++) {
        calibrations[i].id = i;
        oldCalibrations[i].id = i;
    }
}

bool CalibrationHistory::addDatum(unsigned int electrode, float pH, float voltage, float temperature) {
    int calibrationId = phToCalibrationId(pH);

    // first, save the most recent datum into oldCalibrations
    calibrationDatum oldDatum;
    if (calibrations[electrode].getDatum(calibrationId, &oldDatum)) {
        oldCalibrations[electrode].addDatum(&oldDatum);
    }

    // then, save the incoming datum into calibrations, overwriting the old value
    calibrationDatum newDatum = {
        .epoch = now,  // TODO: Use RTC to determine time of datum
        .calibrationPh = pH,
        .calibrationVoltage = voltage,
        .temperature = temperature,
        .calibrationId = calibrationId,
        .isValid = true};
    return calibrations[electrode].addDatum(&newDatum);
}
