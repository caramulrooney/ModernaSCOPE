#include "cliCallbacks.h"

#include <SimpleCLI.h>

#include "argParse.h"
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

    rangeSelectionType rangeType = HORIZONTAL;
    Argument argSelection = cmd.getArgument("selection");
    String selectionString = argSelection.getValue();
    selectionString.toLowerCase();
    switch (selectionString.charAt(0)) {
        case 'h':
            rangeType = HORIZONTAL;
            break;
        case 'v':
            rangeType = VERTICAL;
            break;
        case 'e':
            rangeType = EXCEL;
            break;
        default:
            Serial.println("For selection type, please enter either h/orizontal, v/ertical, or e/xcel.");
    }

    Argument argElectrode = cmd.getArgument("electrodes");
    String electrodeInput = argElectrode.getValue();
    if (!parseElectrodeInput(electrodeInput, electrodes, rangeType)) {
        Serial.println("Could not parse electrode range.");
    }
    return electrodeInput;  // return the raw string
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
    calibrate(electrodes, pH);
}

void measureCallback(cmd *cmdPtr) {
    Command cmd(cmdPtr);

    bool electrodes[N_ELECTRODES];
    String electrodeInput = parseArgElectrode(cmdPtr, electrodes);

    Argument argNow = cmd.getArgument("now");
    bool now = argNow.isSet();

    printElectrodeRange(electrodes);
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

void setupCli() {
    cmdPing = cli.addCommand("ping", pingCallback);
    cmdPing.addPositionalArgument("str", "pong");
    cmdPing.addArgument("n/um/ber,anzahl", "1");
    cmdPing.addFlagArgument("c");

    cmdCalibrate = cli.addCommand("calibrate", calibrateCallback);
    cmdCalibrate.addPositionalArgument("p/H");
    cmdCalibrate.addArgument("e/lectrode/s", "all");
    cmdCalibrate.addArgument("s/elect/ion", "h");

    cmdClearCalibration = cli.addCommand("calibrate", calibrateCallback);
    cmdClearCalibration.addArgument("p/H", "all");
    cmdClearCalibration.addArgument("e/lectrode/s", "all");
    cmdClearCalibration.addArgument("s/elect/ion", "h");

    cmdShowCalibration = cli.addCommand("calibrate", calibrateCallback);
    cmdShowCalibration.addArgument("p/H", "all");
    cmdShowCalibration.addArgument("e/lectrode/s", "all");
    cmdShowCalibration.addArgument("s/elect/ion", "h");

    cmdMeasure = cli.addCommand("measure", measureCallback);
    cmdMeasure.addArgument("e/lectrode/s", "all");
    cmdMeasure.addArgument("s/elect/ion", "h");
    cmdMeasure.addArgument("t/ime/_steps", "1");
    cmdMeasure.addArgument("max_time", "120");
    cmdMeasure.addFlagArgument("n/ow");
    cmdMeasure.addFlagArgument("v/oltage/_only");

    cli.setOnError(errorCallback);
}

void loopCli() {
    if (Serial.available()) {
        String input = Serial.readStringUntil('\n');
        Serial.println("# " + input);

        cli.parse(input);
    }
}
