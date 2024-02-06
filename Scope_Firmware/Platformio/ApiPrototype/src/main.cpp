/*********
  Rui Santos
  Complete project details at https://randomnerdtutorials.com/esp8266-nodemcu-access-point-ap-web-server/

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files.
  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.
*********/

// Import required libraries
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESPAsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <FS.h>
#include <LittleFS.h>

const char *ssid = "ESP8266-Access-Point";
const char *password = "123456789";

// Create AsyncWebServer object on port 80
AsyncWebServer server(80);
void writeFile(const char *, const char *);

void checkFiles()
{
  if (LittleFS.exists("/index.html"))
  {
    Serial.println("/index.html exists.");
  }
  else
  {
    Serial.println("/index.html does not exist.");
  }
  if (LittleFS.exists("/style.css"))
  {
    Serial.println("/style.css exists.");
  }
  else
  {
    Serial.println("/style.css does not exist.");
  }
  if (LittleFS.exists("/result.txt"))
  {
    Serial.println("/result.txt exists.");
  }
  else
  {
    Serial.println("/result.txt does not exist.");
  }
}

void setup()
{
  // Serial port for debugging purposes
  Serial.begin(115200);
  Serial.println();
  Serial.println("Hello World!");
  Serial.println();
  writeFile("/result.txt", "a, b, c\n100, 200, 300\n300, 400, 100\n150, 300, 200");
  checkFiles();

  Serial.print("Setting AP (Access Point)…");
  // Remove the password parameter, if you want the AP (Access Point) to be open
  WiFi.softAP(ssid, password);

  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);

  // Print ESP8266 Local IP Address
  Serial.println(WiFi.localIP());

  // Route for root / web page
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request)
            { request->send(LittleFS, "text/html", "/index.html"); });
  // Route to load style.css file
  server.on("/style.css", HTTP_GET, [](AsyncWebServerRequest *request)
            { request->send(LittleFS, "text/css", "/style.css"); });
  server.on("/temperature", HTTP_GET, [](AsyncWebServerRequest *request)
            { request->send_P(200, "text/plain", "This is your ~~ Temperature ~~"); });
  server.on("/humidity", HTTP_GET, [](AsyncWebServerRequest *request)
            { request->send_P(200, "text/plain", "This is your ~~~~ Humidity ~~~~"); });
  server.on("/csv", HTTP_GET, [](AsyncWebServerRequest *request)
            { request->send_P(200, "text/plain", "/result.txt"); });

  // Start server
  server.begin();
}

void loop()
{
}

void writeFile(const char *path, const char *message)
{
  Serial.printf("Writing file: %s\r\n", path);

  File file = LittleFS.open(path, "w+");
  if (!file)
  {
    Serial.println("- failed to open file for writing");
    return;
  }
  if (file.print(message))
  {
    Serial.println("- file written");
  }
  else
  {
    Serial.println("- write failed");
  }
  file.close();
}
