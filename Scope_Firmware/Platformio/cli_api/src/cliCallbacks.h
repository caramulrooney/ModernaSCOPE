#pragma once
#include <SimpleCLI.h>

void errorCallback(cmd_error *errorPtr);

void calibrateCallback(cmd *cmdPtr);

void measureCallback(cmd *cmdPtr);

void pingCallback(cmd *cmdPtr);

void setupCli();

void loopCli();
