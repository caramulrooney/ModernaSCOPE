#include <Arduino.h>
#include <SimpleCLI.h>

#include "defines.h"
#include "electrode.h"

SimpleCLI cli;

Command cmdPing;
Command cmdCalibrate;
Command cmdClearCalibration;
Command cmdShowCalibration;
Command cmdMeasure;

void errorCallback(cmd_error *errorPtr) {
    CommandError e(errorPtr);

    Serial.println("ERROR: " + e.toString());

    if (e.hasCommand()) {
        Serial.println("Did you mean? " + e.getCommand().toString());
    } else {
        Serial.println(cli.toString());
    }
}

String parseArgElectrode(cmd *cmdPtr, bool electrodes[]) {
    Command cmd(cmdPtr);

    Argument argElectrode = cmd.getArgument("electrodes");
    String electrodeInput = argElectrode.getValue();
    if (!parseElectrodeInput(electrodeInput, electrodes)) {
        Serial.println("Could not parse electrode range.");
    }
    return electrodeInput;
}

float parseArgPh(cmd *cmdPtr) {
    Command cmd(cmdPtr);

    Argument argPh = cmd.getArgument("pH");
    float pH = argPh.getValue().toFloat();
    if (pH <= 0 || pH >= 14) {
        Serial.println("Please enter a pH value between 0 and 14, exclusive.");
    }
    return pH;
}

void calibrateCallback(cmd *cmdPtr) {
    Command cmd(cmdPtr);

    float pH = parseArgPh(cmdPtr);

    bool electrodes[N_ELECTRODES];
    String electrodeInput = parseArgElectrode(cmdPtr, electrodes);

    Serial.println("Calibrating electrodes " + electrodeInput);
}

void measureCallback(cmd *cmdPtr) {
    Command cmd(cmdPtr);

    bool electrodes[N_ELECTRODES];
    String electrodeInput = parseArgElectrode(cmdPtr, electrodes);

    Argument argNow = cmd.getArgument("now");
    bool now = argNow.isSet();

    Serial.println("Measuring electrodes " + electrodeInput);
}

void pingCallback(cmd *cmdPtr) {
    Command cmd(cmdPtr);

    Argument argN = cmd.getArgument("num");
    String argVal = argN.getValue();
    int n = argVal.toInt();

    Argument argStr = cmd.getArgument("str");
    String strVal = argStr.getValue();

    Argument argC = cmd.getArgument("c");
    bool c = argC.isSet();

    if (c)
        strVal.toUpperCase();

    for (int i = 0; i < n; i++) {
        Serial.println(strVal);
    }
}

void setup() {
    Serial.begin(115200);
    Serial.println();
    Serial.println("Hello World");
    Serial.println();

    cmdPing = cli.addCommand("ping", pingCallback);
    cmdPing.addPositionalArgument("str", "pong");
    cmdPing.addArgument("n/um/ber,anzahl", "1");
    cmdPing.addFlagArgument("c");

    cmdCalibrate = cli.addCommand("calibrate", calibrateCallback);
    cmdCalibrate.addPositionalArgument("p/H");
    cmdCalibrate.addArgument("e/lectrode/s", "all");

    cmdClearCalibration = cli.addCommand("calibrate", calibrateCallback);
    cmdClearCalibration.addArgument("p/H", "all");
    cmdClearCalibration.addArgument("e/lectrode/s", "all");

    cmdShowCalibration = cli.addCommand("calibrate", calibrateCallback);
    cmdShowCalibration.addArgument("p/H", "all");
    cmdShowCalibration.addArgument("e/lectrode/s", "all");

    cmdMeasure = cli.addCommand("measure", measureCallback);
    cmdMeasure.addArgument("e/lectrode/s", "all");
    cmdMeasure.addArgument("t/ime/_steps", "1");
    cmdMeasure.addArgument("max_time", "120");
    cmdMeasure.addFlagArgument("n/ow");
    cmdMeasure.addFlagArgument("v/oltage/_only");

    cli.setOnError(errorCallback);
}

void loop() {
    if (Serial.available()) {
        String input = Serial.readStringUntil('\n');
        Serial.println("# " + input);

        cli.parse(input);
    }
}
