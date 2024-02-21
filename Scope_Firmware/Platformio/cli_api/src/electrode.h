#pragma once
#include <Arduino.h>

#include "defines.h"

/**
 * Calibrate electrodes with a standard pH buffer.
 *
 * Assume a standard buffer solution has already been applied to the specified electrodes. Store the current voltage for the specified electrodes in memory and use it as a comparison to calculate the pH of those electrodes in the future.
 *
 * @param electrodes Bool array of length 96, saying which electrodes to calibrate. Such an array can be generated by parseElectrodeInput().
 * @param pH pH of the buffer currently residing on the electrodes being calibrated.
 */
void calibrate(bool electrodes[], float pH);

/**
 * Measure electrode pH.
 *
 * Read the voltage at all electrodes and convert to a pH value using the calibration data stored in memory. Store the calculated pH values in the return array. Return a flag saying whether or not the voltage has settled.
 *
 * @param phValues Return array to hold the pH measurements. `pHValues` must have 96 elements, as all electrodes will be read.
 *
 * @return True if the pH measurement has settled and is ready to be reported; false otherwise.
 */
bool measurePh(float phValues[]);

/**
 * Measure electrode voltage as received by the ADC.
 *
 * Read the voltage at all electrodes but don't convert to a pH value. Store the raw voltages in the return array. Return a flag saying whether or not the voltage has settled.
 *
 * @param voltages Return array to hold the voltage readings. `voltages` must have 96 elements, as all electrodes will be read.
 */
bool measureVoltage(float voltages[]);

typedef struct {
    long epoch;                // epoch timestamp
    float calibrationPh;       // applied to the electrode
    float calibrationVoltage;  // measured in response
    float temperature;         // measured
    int calibrationId;         // round(10 * calibrationPh)
    bool isValid;              // whether it has been assigned or deleted
} calibrationDatum;

class Calibration {
   private:
    calibrationDatum datums[MAX_CALIBRATION_DATUMS];

   public:
    unsigned int id;

    Calibration();

    bool addDatum(calibrationDatum* datum);

    bool getDatum(int calibrationId, calibrationDatum* returnDatum);
};

class CalibrationHistory {
   public:
    Calibration calibrations[N_ELECTRODES];
    Calibration oldCalibrations[N_ELECTRODES];

    CalibrationHistory();

    bool addDatum(unsigned int electrode, float pH, float voltage, float temperature);
};