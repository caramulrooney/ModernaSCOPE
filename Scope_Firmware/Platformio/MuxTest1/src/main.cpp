#include <Arduino.h>

#include "Wire.h"

// Define the I2C address for the ADS1110
#define ads1110 0x49  // correct

// // Define pin aliases
// #define D0 16
// #define D1 5
// #define D2 4
// #define D3 0
// #define D4 2
// #define D5 14
// #define D6 12
// #define D7 13
// #define D8 15

#define nSelectPins 7
int selectPins[] = {13, 41, 40, 36, 37, 38, 39};  // these are correct for Teensy 4.1
void selectElectrode(int electrode);
void receiveSerial();
void readADS1110();

// Declare variables to store voltage and ads1110 raw data
float voltage,
    data;

// Declare variables for high byte, low byte, and configuration register
byte highbyte, lowbyte, configRegister;

// Setup function
void setup() {
    Serial.begin(115200);
    Serial.println();
    Serial.println("Hello, World!");
    Serial.println();
    Wire.begin();  // I2C Communication library

    for (int i = 0; i < nSelectPins; i++) {
        pinMode(selectPins[i], OUTPUT);
    }
}
int electrode = 8;  // Looking at one electrode at a time

// Loop function
void loop() {
    selectElectrode(electrode);
    receiveSerial();
    readADS1110();

    // Delay for 1 second
    delay(1000);
}

void readADS1110() {
    // Request 3 bytes of data from the ADS1110 via I2C
    Wire.requestFrom(ads1110, 3);
    // Wait until all the requested data is available
    while (Wire.available())  // ensure all the data comes in
    {
        Serial.println("Wire was available at least once");
        // Read the high byte, low byte, and configuration register
        highbyte = Wire.read();  // high byte * B11111111
        lowbyte = Wire.read();   // low byte
        configRegister = Wire.read();
    }

    // Combine the high and low bytes to get the raw data
    data = highbyte * 256;
    data = data + lowbyte;

    // Print the raw data
    Serial.print("ADCValue >> ");
    Serial.println(data, DEC);

    // Convert the raw data to voltage (assuming 2.048V reference and 15-bit resolution)
    Serial.print("Voltage >> ");
    voltage = data * 2.048;
    voltage = voltage / 32768.0;

    // Print the voltage
    Serial.print(voltage, DEC);
    Serial.println(" V");

    Serial.print("Configuration Byte = ");
    Serial.println(configRegister);
}

void selectElectrode(int electrode) {
    Serial.print("Selecting electrode ");
    Serial.print(electrode);
    Serial.print(". Select outputs are: ");

    for (int pin = 0; pin < nSelectPins; pin++) {
        bool pinState = (electrode >> pin) % 2;  // get the nth bit of the 7-bit binary number
        digitalWrite(selectPins[pin], pinState);
        Serial.print(int(pinState));
        Serial.print(" ");
    }
    Serial.println();
}

const size_t numChars = 3;
char receivedChars[numChars];  // an array to store the received data

// function modified from https://forum.arduino.cc/t/serial-input-basics-updated/382007
void receiveSerial() {
    static byte idx = 0;
    char endMarker = '!';
    char nextChar;

    while (Serial.available() > 0) {
        nextChar = Serial.read();

        if (nextChar != endMarker) {
            receivedChars[idx] = nextChar;
            idx++;
            if (idx >= numChars) {
                idx = numChars - 1;
            }
        } else {
            receivedChars[idx] = '\0';  // terminate the string
            idx = 0;
            electrode = atoi(receivedChars);
        }
    }
}
