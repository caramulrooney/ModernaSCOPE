// Example 53.1 - ADS1110 single-sided voltmeter (0~2.048VDC)

#include "Wire.h"

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

bool fHasLooped = false;
int electrode = 1; //Looking at one electrode at a time

// Declare variables to store voltage and ads1110 raw data
float voltage, data;

// Declare variables for high byte, low byte, and configuration register
byte highbyte, lowbyte, configRegister;


// Setup function
void setup()
{
   // Start serial communication at 9600 baud
   Serial.begin(9600);
   // Initialize the wire library for I2C communication
   Wire.begin();
}

// Loop function
void loop(){
  //if (fHasLooped == false) {
    if (electrode == 1) { //Looking at one electrode at a time
    //for (int electrode = 0; electrode < 96; electrode++) { //Iterate through all electrodes
      Serial.println("Inside the loop");
      selectElectrode(electrode);
      
       // Request 3 bytes of data from the ADS1110 via I2C
       Wire.requestFrom(ads1110, 3);
       // Wait until all the requested data is available
       while(Wire.available()) // ensure all the data comes in
       {
         // Read the high byte, low byte, and configuration register
         highbyte = Wire.read(); // high byte * B11111111
         lowbyte = Wire.read(); // low byte
         configRegister = Wire.read();
       }
      
       // Combine the high and low bytes to get the raw data
       data = highbyte * 256;
       data = data + lowbyte;
    
       // Print the raw data
       Serial.print("\nADCValue >> ");
       Serial.println(data, DEC);
    
       // Convert the raw data to voltage (assuming 2.048V reference and 15-bit resolution)
       Serial.print("Voltage >> ");
       voltage = data * 2.048 ;
       voltage = voltage / 32768.0;
    
       // Print the voltage
       Serial.print(voltage, DEC);
       Serial.println(" V");
    
       // Delay for 1 second
       delay(1000);

       fHasLooped = true;
     }
  //}
}

void selectElectrode(int electrode){
  Serial.print("Selecting electrode "); 
  Serial.print(electrode); 
  Serial.print(". Select outputs are: ");
  
  for (int pin = 0; pin < nSelectPins; pin++) {
    bool pinState = (electrode >> pin) % 2; // get the nth bit of the 7-bit binary number
    digitalWrite(selectPins[pin], pinState);
    Serial.print(int(pinState)); 
    Serial.print(" ");
  }
}
