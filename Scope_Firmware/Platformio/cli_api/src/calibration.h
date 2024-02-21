
#pragma once
#include "defines.h"

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
