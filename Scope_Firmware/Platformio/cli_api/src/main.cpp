#include <Arduino.h>
#include <SimpleCLI.h>

#include "cliCallbacks.h"

void setup() {
    Serial.begin(115200);
    Serial.println();
    Serial.println("Hello World");
    Serial.println();

    setupCli();
}

void loop() {
    loopCli();
}
