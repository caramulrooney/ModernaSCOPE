#include <Wire.h>
#include <math.h>
#include <ADS1110.h> // Implement this library!! https://github.com/nadavmatalon/ADS1110/tree/master

// Define the ADS1110 I2C address
// ADS1110_I2C_ADDRESS(0b1001001);
#define ADS1110_I2C_ADDRESS 0b1001001
ADS1110 ads1110(ADS1110_I2C_ADDRESS);
#define ADC_MIN 100
#define ADC_MAX 800

#define D0 16
#define D1 5
#define D2 4
#define D3 0
#define D4 2
#define D5 14
#define D6 12
#define D7 13
#define D8 15

#define MUX_SELECT_1 D0
#define MUX_SELECT_2 D3
#define MUX_SELECT_3 D4
#define MUX_SELECT_4 D5
#define MUX_SELECT_5 D6
#define MUX_SELECT_6 D7
#define MUX_SELECT_7 D8

#define nSelectPins 7
int selectPins[] = {D0, D3, D4, D5, D6, D7, D8};



// typedef enum:byte {
//   GAIN_MASK = 0x03,      // 3 - B00000011
//   GAIN_1    = 0x00,      // 0 - B00000000 (Default)
//   GAIN_2    = 0x01,      // 1 - B00000001
//   GAIN_4    = 0x02,      // 2 - B00000010
//   GAIN_8    = 0x03       // 3 - B00000011
// } gain_t;

// typedef enum:byte {
//   SPS_MASK = 0x0C,       // 12 - B00001100
//   SPS_15   = 0x0C,       // 12 - B00001100 (Default)
//   SPS_30   = 0x08,       //  8 - B00001000
//   SPS_60   = 0x04,       //  4 - B00000100
//   SPS_240  = 0x00        //  0 - B00000000
// } sample_rate_t;

// typedef enum:byte {
//   CONT          = 0x00,  // B00000000 (Defualt)
//   SINGLE        = 0x10   // B00010000
// } con_mode_t;

// typedef enum:byte {
//   MIN_CODE_240 = 0x01,   //  1 - Minimal Data Value for 240_SPS / -2048  (12-BIT)
//   MIN_CODE_60  = 0x04,   //  4 - Minimal Data Value for 60_SPS  / -2048  (14-BIT)
//   MIN_CODE_30  = 0x08,   //  8 - Minimal Data Value for 30_SPS  / -2048  (15-BIT)
//   MIN_CODE_15  = 0x10    // 16 - Minimal Data Value for 15_SPS  / -2048  (16-BIT) (Default)
// } min_code_t;

// typedef enum:byte {
//   RES_12,                // 12-BIT Resolution
//   RES_14,                // 14-BIT Resolution
//   RES_15,                // 15-BIT Resolution
//   RES_16                 // 16-BIT Resolution (Default)
// } res_t;

// typedef enum:int {
//   INT_REF =    0,        // Inernal Reference:  Pin Vin- is connected to GND (Default)
//   EXT_REF = 2048         // External Reference: Pin Vin- is connected to 2.048V source
// } vref_t;

// const byte DEFAULT_CONFIG = 12;      // B00001100 (16-BIT, 15 SPS, GAIN x1, CONTINUOUS)
// byte _config = DEFAULT_CONFIG;
// const byte COM_SUCCESS = 0;      // I2C Communication Success (No Error)
// byte _comBuffer = COM_SUCCESS;

// void setRes(res_t newRes);
// void setGain(gain_t newGain);
// void initCall(byte data);
// void endCall();
// void setConfig(byte newConfig);

void setup() {
  // Initialize the Serial communication for debugging
  Serial.begin(9600);
  Wire.begin();

  // set all mux select pins to output
  for (int pin = 0; pin < nSelectPins; pin++) {
    pinMode(selectPins[pin], OUTPUT);
  }

  // Set gain
  ads1110.setGain(GAIN_1);
  // setGain(GAIN_1);

  Serial.println("ADS1110 Initialized!");

}

void loop() {
  for (int electrode = 0; electrode < 96; electrode++) { // Iterate through all electrodes
    selectElectrode(electrode);

    // Perform calibration
    delay(10);

    // Read ADC and perform necessary operations
    int adcValue = ads1110.getData();
    // int adcValue = readADC();

    // Print the result
    Serial.print("Electrode ");
    Serial.print(electrode);
    Serial.print(": ");
    Serial.println(adcValue);

    // Convert ADC value to pH
    float pHValue = convertToPH(adcValue);

    // Print the result
    Serial.print("pH Value: ");
    Serial.println(pHValue);

    // Wait before moving to the next electrode
    delay(10);

  }
}

void selectElectrode(int electrode){
  Serial.print("Selecting electrode "); Serial.print(electrode); Serial.print(". Select outputs are: ");
  for (int pin = 0; pin < nSelectPins; pin++) {
    bool pinState = (electrode >> pin) % 2; // get the nth bit of the 7-bit binary number
    digitalWrite(selectPins[pin], pinState);
    Serial.print(int(pinState)); Serial.print(" ");
  }
  Serial.print(" ).");
}

// void setGain() {
//   Wire.beginTransmission(ADS1110_I2C_ADDRESS);
//   Wire.write(ADS1110_CONFIG_REG); // Replace, Address the configuration register

//   // Set the gain
//   Wire.write(ADS1110_GAIN_4); // Replace with command for gain 4

//   Wire.endTransmission();
// }

int readADC() {
  // Logic to read ADC value from ADS1110
  Wire.requestFrom(ADS1110_I2C_ADDRESS, 2);
  // Read and combine two bytes into an integer
  int16_t value = (Wire.read() << 8) | Wire.read();
  return value;
}

float convertToPH(int adcValue) {
    // Replace these constants with your actual calibration values
    float pHRef = 7.0;
    float HRefConcentration = 1.0;  // Replace with your actual reference H+ concentration
    float R = 8.314;  // Ideal gas constant
    float T = 298.15;  // Temperature in Kelvin (25 degrees Celsius)
    float F = 96485.33289;  // Faraday's constant

    // Assuming you have a linear relationship between ADC value and hydrogen ion concentration
    float HConcentration = map(adcValue, ADC_MIN, ADC_MAX, 0.0, 14.0);

    // Nernst equation
    float pH = pHRef + (R * T / F) * log10(HConcentration / HRefConcentration);

    return pH;
    // Replace ADC_MIN and ADC_MAX with actual calibration values
}


// /*==============================================================================================================*
//     SET RESOLUTION
//  *==============================================================================================================*/

// void setRes(res_t newRes) {                             // PARAMS: 12_BIT / 14_BIT / 15_BIT / 16_BIT
//     switch (newRes) {
//         case (RES_12): setConfig((_config & ~SPS_MASK) | (SPS_240 & SPS_MASK)); break;
//         case (RES_14): setConfig((_config & ~SPS_MASK) | (SPS_60  & SPS_MASK)); break;
//         case (RES_15): setConfig((_config & ~SPS_MASK) | (SPS_30  & SPS_MASK)); break;
//         case (RES_16): setConfig((_config & ~SPS_MASK) | (SPS_15  & SPS_MASK)); break;
//     }
// }

// /*==============================================================================================================*
//     SET GAIN
//  *==============================================================================================================*/

// void setGain(gain_t newGain) {                          // PARAMS: GAIN_1 / GAIN_2 / GAIN_4 / GAIN_8
//     setConfig((_config & ~GAIN_MASK) | (newGain & GAIN_MASK));
// }

// /*==============================================================================================================*
//     INITIATE I2C COMMUNICATION
//  *==============================================================================================================*/

// void initCall(byte data) {
//     Wire.beginTransmission(ADS1110_I2C_ADDRESS);
//     Wire.write(data);
// }

// /*==============================================================================================================*
//     END I2C COMMUNICATION
//  *==============================================================================================================*/

// void endCall() {
//     _comBuffer = Wire.endTransmission();
// }

// /*==============================================================================================================*
//     SET CONFIGURATION REGISTER
//  *==============================================================================================================*/

// void setConfig(byte newConfig) {
//     initCall(newConfig);
//     endCall();
//     if (_comBuffer == COM_SUCCESS) _config = newConfig;
// }
