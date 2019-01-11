/*
 * These arrays specify the digital pin each button is connected to, and the method/event to send if that
 * button is pushed. The number of methods must match the number of buttons for each category, so if
 * there are 4 buttons per team for scoring methods, there must be 4 scoring methods in the methods
 * array.
 * 
 * On an Arduino UNO board the maximum amount of buttons that can be used is 11, as pins 0 and 1 do not
 * get anything hooked up to them due to being TX and RX pins for serial connections and pin 13 is used as a status LED
 */
const int team1Buttons[] = {3,4,5,6}; // buttons for scoring methods that credit team 1
const int team2Buttons[] = {7,8,9,10}; // buttons for scoring methods that credit team 2
const String methods[] = {"rubberband","pingpong","shove","disable"}; // the scoring methods, number of methods must match number of buttons per team
#define NUM_OF_METHODS 4

const int specialButtons[] = {11,12}; // buttons for special buttons (start match, request next match)
const String specialEvents[] = {"n","s"}; // events to send for the special buttons, n is request next match, s is start match
#define NUM_OF_SPEC 2

//pin 13 is status LED
#define statusLED 13



void setup() {
  Serial.begin(9600); // Begin Serial Communications
  for(int i = 0; i < NUM_OF_METHODS; i++) {
    pinMode(team1Buttons[i],INPUT_PULLUP);
    pinMode(team2Buttons[i],INPUT_PULLUP);
  }
  for(int i = 0; i < NUM_OF_SPEC; i++) {
    pinMode(specialButtons[i], INPUT_PULLUP);
  }
  pinMode(statusLED,OUTPUT); // init the status LED
  digitalWrite(statusLED, LOW); // status is off to begin

  //python code uses readline() for reaching the COM port connection, serial.println should be used so it is properly detected
  Serial.println("Ready.");

}

void loop() {
  //Check the special buttons
  for(int i = 0; i < NUM_OF_SPEC; i++) {
    if(digitalRead(specialButtons[i]) == false) {
      delay(50); // debounce delay
      if(digitalRead(specialButtons[i]) == false) {
        digitalWrite(statusLED,HIGH);
        Serial.println(specialEvents[i]);
        delay(350);
        digitalWrite(statusLED,LOW);
      }
    }
    
  }
  //Check the Team 1 score buttons
  for(int i = 0; i < NUM_OF_METHODS; i++) {
    if(digitalRead(team1Buttons[i]) == false) {
      delay(50); // debouncing delay
      if(digitalRead(team1Buttons[i]) == false) { // state verification after debounce
        digitalWrite(statusLED,HIGH);
        Serial.println( (methods[i] + "1") );
        delay(350);
        digitalWrite(statusLED,LOW);
      }
    }
  }
  
  //Check the team 2 score buttons
  for(int i = 0; i < NUM_OF_METHODS; i++) {
    if(digitalRead(team2Buttons[i]) == false) {
      delay(50); // debouncing delay
      if(digitalRead(team2Buttons[i]) == false) { // state verification after debounce
        digitalWrite(statusLED,HIGH);
        Serial.println( (methods[i] + "2") );
        delay(100);
        digitalWrite(statusLED,LOW);
      }
    }
  }
  delay(20);
}
