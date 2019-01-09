#include <Utility.h> // Utility library is required, can be downloaded from http://playground.arduino.cc/Code/Utility

const int team1Buttons = {3,4,5,6}; // buttons for scoring methods that credit team 1
const int team2Buttons = {7,8,9,10}; // buttons for scoring methods that credit team 2
//The methods are the same between the 2 team button sets, just FYI
const String methods = {"rubberband","pingpong","shove","disable"}; // the scoring methods, number of methods must match number of buttons per team
#define NUM_OF_METHODS 4

const int specialButtons = {11,12}; // buttons for special buttons (start match, request next match)
#define NUM_OF_SPEC 2

//pin 13 is status LED
#define statusLED 13



void setup() {
  Serial.begin(9600); // Begin Serial Communications
  foreach(team1Buttons,NUM_OF_METHODS,pinMode,INPUT_PULLUP); // init the team 1 buttons
  foreach(team2Buttons,NUM_OF_METHODS,pinMode,INPUT_PULLUP); // init the team 2 buttons
  foreach(specialButtons,NUM_OF_SPEC,pinMode,INPUT_PULLUP); // init the special buttons
  pinMode(statusLED,OUTPUT) // init the status LED
  digitalWrite(statusLED, LOW); // status is off to begin

  //python code uses readline() for reaching the COM port connection, serial.println should be used so it is properly detected
  

}

void loop() {
  for(int i = 0; i < NUM_OF_METHODS; i++) {
    if(digitalRead(team1Buttons[i]) == false) {
      Serial.println( (methods[i] + "1") );
    }
  }

}
