#include <Wire.h>
#include <math.h>
#include "ADS1110.h" // Implement this library!! https://github.com/nadavmatalon/ADS1110/tree/master

// Define the ADS1110 I2C address
// ADS1110_I2C_ADDRESS(0b1001001);
#define ADS1110_I2C_ADDRESS 0b1001001

#define MUX_SELECT_1 D0
#define MUX_SELECT_2 D3
#define MUX_SELECT_3 D4
#define MUX_SELECT_4 D5
#define MUX_SELECT_5 D6
#define MUX_SELECT_6 D7
#define MUX_SELECT_7 D8

#define nSelectPins 7
int selectPins[] = {D0, D3, D4, D5, D6, D7, D8};

void setup() {
  // Initialize the Serial communication for debugging
  Serial.begin(9600);
  Wire.begin();

  // set all mux select pins to output
  for (int pin = 0; pin < nSelectPins; pin++) {
    pinMode(selectPins[pin], OUTPUT);
  }

  // Set gain
  setGain(GAIN_1);

  Serial.println("ADS1110 Initialized!");

}

void loop() {
  for (int electrode = 0; electrode < 96; electrode++) { // Iterate through all electrodes
    selectElectrode(electrode);

    // Perform calibration
    delay(10);

    // Read ADC and perform necessary operations
    int adcValue = readADC();

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
