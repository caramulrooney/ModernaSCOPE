#include <Arduino.h>
#include <ArduinoJson.h>
#include <SPI.h>
#include <Wire.h>

#define NUM_ELECTRODES 96
// #define DEBUG

void setup_ads1110();
void selectElectrode(int electrode_id);
float calculateVoltage(int electrode, bool* status);

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

// configuration bits
typedef struct {
    bool ST_DRDY = 1;         // read value
    bool PLACE_HOLDER_1 = 0;  // empty
    bool PLACE_HOLDER_0 = 0;  // empty
    bool SC_BIT = 0;          // 1: single conversion mode, 0: continuous conversion mode
    bool DR_1 = 0;            // DR_1 DR_0
    bool DR_0 = 0;            // 00: 240 Samples per second (SPS), 01: 60 SPS, 10: 30 SPS, 11: 15 SPS
    bool PGA_1 = 0;           // PGA_1 PGA_0
    bool PGA_0 = 1;           // 00: Gain of 1, 01: Gain of 2, 10: Gain of 4, 11: Gain of 8
} config;

// Declare variables for high byte, low byte, and configuration register
byte highbyte, lowbyte, configRegister;

void setup() {
    Serial.begin(115200);
#ifdef DEBUG
    Serial.println("");
    Serial.println("Hello, World!");
    Serial.println("");
#endif

    // Initialize the wire library for I2C communication
    Wire.begin();
    pinMode(D0, OUTPUT);
    pinMode(D3, OUTPUT);
    pinMode(D4, OUTPUT);
    pinMode(D5, OUTPUT);
    pinMode(D6, OUTPUT);
    pinMode(D7, OUTPUT);
    pinMode(D8, OUTPUT);

    setup_ads1110();
}

void loop() {
    if (Serial.available() > 0) {
        char receivedChar = Serial.read();
        if (receivedChar == 'e') {
            // read voltages from electrodes
            for (int i = 0; i < NUM_ELECTRODES; i++) {
                bool status = false;
                voltages[i] = calculateVoltage(i, &status);
                delay(5);
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

float calculateVoltage(int electrode, bool* status) {
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

    // read the ST/DRDY bit of the config register
    if (configRegister & 0b10000000) {
#ifdef DEBUG
        Serial.println("Data is old data!");
#endif
        *status = false;
    } else {
#ifdef DEBUG
        Serial.println("Data is new data!");
#endif
        *status = true;
    }

#ifdef DEBUG
    bool sc_register = configRegister & 0b00010000;
    Serial.println("sc_register is " + String(sc_register ? "Single Conversion Mode" : "Continuous Conversion Mode"));
#endif

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

void setup_ads1110() {
    config myConfig;

    // Initialize configuration settings
    myConfig.ST_DRDY = 1;
    myConfig.PLACE_HOLDER_1 = 0;
    myConfig.PLACE_HOLDER_0 = 0;
    myConfig.SC_BIT = 0;  // Continuous conversion mode
    myConfig.DR_1 = 0;    // 240 samples per second
    myConfig.DR_0 = 0;
    myConfig.PGA_1 = 0;  // Gain of 1
    myConfig.PGA_0 = 1;

    configRegister =
        (myConfig.ST_DRDY << 7) +           // Bit 7: ST_DRDY
        (myConfig.PLACE_HOLDER_1 << 6) +    // Bit 6: PLACE_HOLDER_1
        (myConfig.PLACE_HOLDER_0 << 5) +    // Bit 5: PLACE_HOLDER_0
        (myConfig.SC_BIT << 4) +            // Bit 4: SC_BIT
        (myConfig.DR_1 << 3) +              // Bit 3: DR_1
        (myConfig.DR_0 << 2) +              // Bit 2: DR_0
        (myConfig.PGA_1 << 1) +             // Bit 1: PGA_1
        (myConfig.PGA_0 << 0);              // Bit 0: PGA_0

#ifdef DEBUG
    Serial.print("Writing config register...   ");
#endif

    Wire.beginTransmission(ads1110);  // Transmit to the ADS1110's I2C address

#ifdef DEBUG
    if (Wire.write(configRegister)) {  // Sends value byte
        Serial.print("Wrote config register: " + String(configRegister) + " = 0b");
        Serial.println(configRegister, BIN);
    } else {
        Serial.println("Failed to write config register.");
    }
#else
    Wire.write(configRegister);
#endif

    Wire.endTransmission();
}
