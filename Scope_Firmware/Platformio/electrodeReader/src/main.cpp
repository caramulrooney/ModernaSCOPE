#include <Arduino.h>
#include <ArduinoJson.h>
#include <SPI.h>
#include <Wire.h>

const int NUM_ELECTRODES = 96;
float voltages[NUM_ELECTRODES];

void setup() {
  Serial.begin(115200);
}

void loop() {
  if (Serial.available() > 0){
    char receivedChar = Serial.read();
    if (receivedChar == 'e') {
      // read voltages from electrodes
      for (int i = 0; i <= NUM_ELECTRODES; i++) {
        voltages[i] = 1;
        //analogRead(i) * (2.048 / 1023.0) // CHANGE
      }
      // format data in JSON
      JsonDocument doc; // create static json document with capacity of 256 bytes
      JsonArray values = doc.to<JsonArray>(); // create json array `values` and initialize it with contents of json doc
      for (int i = 0; i < NUM_ELECTRODES; i++) { // iterate over each element in  `voltages` array and add them to json array
        values.add(voltages[i]);
      }

      // send json back to python script
      serializeJson(values, Serial); // serialize json array into json string and write to serial port
      Serial.println();

    }
  }
  delay(10);
}
