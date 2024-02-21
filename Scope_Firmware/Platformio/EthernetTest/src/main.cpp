#include <Arduino.h>

// put function declarations here:
/*
  ModbusTCP for W5x00 Ethernet library
  Basic Server code example

  (c)2020 Alexander Emelianov (a.m.emelianov@gmail.com)
  https://github.com/emelianov/modbus-esp8266

  This code is licensed under the BSD New License. See LICENSE.txt for more info.
*/

#include <Ethernet.h>  // Ethernet library v2 is required
#include <ModbusEthernet.h>
#include <SPI.h>

#define CALLBACK_COIL 100

uint16_t onCoilChange(TRegister* reg, uint16_t val) {
    Serial.println("Coil was changed!");
    return val;
}

bool onClientConnect(IPAddress ip) {
    Serial.print("Client connected at IP: ");
    Serial.println(ip);
    return true;
}

// Enter a MAC address and IP address for your controller below.
byte mac[] = {
    0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED};
IPAddress ip(192, 168, 0, 210);  // The IP address will be dependent on your local network:
ModbusEthernet mb;               // Declare ModbusTCP instance

void setup() {
    Serial.begin(115200);  // Open serial communications and wait for port to open
    Serial.println();
    Serial.println("Hello, World!");
    Serial.println();

    Ethernet.init(5);         // SS pin
    Ethernet.begin(mac, ip);  // start the Ethernet connection
    delay(1000);              // give the Ethernet shield a second to initialize
    mb.server();              // Act as Modbus TCP server
    // mb.addReg(HREG(100));     // Add Holding register #100
    mb.addCoil(CALLBACK_COIL);                  // Add Coil. The same as mb.addCoil(COIL_BASE, false, LEN)
    mb.onSetCoil(CALLBACK_COIL, onCoilChange);  // Add callback on Coil LED_COIL value set
}

void loop() {
    mb.task();  // Server Modbus TCP queries
    delay(50);
}
