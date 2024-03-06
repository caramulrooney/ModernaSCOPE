#include <Arduino.h>
#include <ArduinoJson.h>
#include <SPI.h>
#include <Wire.h>

#define NUM_ELECTRODES 96
// #define DEBUG

void selectElectrode(int electrode_id);
float calculateVoltage(int electrode);

// Define the I2C address for the ADS1110
#define ads1110 0x49

// Define ADC select pins
#define D0 16
#define D1 5
#define D2 4
#define D3 0
#define D4 2
#define D5 14
#define D6 12
#define D7 13
#define D8 15

#define nSelectPins 7
int selectPins[] = {D0, D3, D4, D5, D6, D7, D8};
float voltages[NUM_ELECTRODES];

// Declare variables for high byte, low byte, and configuration register
byte highbyte, lowbyte, configRegister;

void setup() {
    Serial.begin(115200);
    // Initialize the wire library for I2C communication
    Wire.begin();
    pinMode(D0, OUTPUT);
    pinMode(D3, OUTPUT);
    pinMode(D4, OUTPUT);
    pinMode(D5, OUTPUT);
    pinMode(D6, OUTPUT);
    pinMode(D7, OUTPUT);
    pinMode(D8, OUTPUT);
}

void loop() {
    if (Serial.available() > 0) {
        char receivedChar = Serial.read();
        if (receivedChar == 'e') {
            // read voltages from electrodes
            for (int i = 0; i < NUM_ELECTRODES; i++) {
                voltages[i] = calculateVoltage(i);
            }

            // format data in JSON
            JsonDocument doc;                           // create static json document with capacity of 256 bytes
            JsonArray values = doc.to<JsonArray>();     // create json array `values` and initialize it with contents of json doc
            for (int i = 0; i < NUM_ELECTRODES; i++) {  // iterate over each element in  `voltages` array and add them to json array
                values.add(voltages[i]);
            }

            // send json back to python script
            serializeJson(values, Serial);  // serialize json array into json string and write to serial port
            Serial.println();
        }
    }
    delay(10);
}

float calculateVoltage(int electrode) {
    selectElectrode(electrode);

    // Request 3 bytes of data from the ADS1110 via I2C
    Wire.requestFrom(ads1110, 3);
    // Wait until all the requested data is available
    while (Wire.available())  // ensure all the data comes in
    {
        // Read the high byte, low byte, and configuration register
        highbyte = Wire.read();  // high byte * B11111111
        lowbyte = Wire.read();   // low byte
        configRegister = Wire.read();
    }

    // Combine the high and low bytes to get the raw data
    float data;
    data = highbyte * 256;
    data = data + lowbyte;

    // Convert the raw data to voltage (assuming 2.048V reference and 15-bit resolution)
    float voltage;
    voltage = data * 2.04;
    voltage = voltage / 32768.0;

    return voltage;
}

void selectElectrode(int electrode) {
#ifdef DEBUG
    Serial.print("Selecting electrode ");
    Serial.print(electrode);
    Serial.print(". Select outputs are: ");
#endif

    for (int pin = 0; pin < nSelectPins; pin++) {
        bool pinState = (electrode >> pin) % 2;  // get the nth bit of the 7-bit binary number
        digitalWrite(selectPins[pin], pinState);
#ifdef DEBUG
        Serial.print(int(pinState));
        Serial.print(" ");
#endif
    }
}
