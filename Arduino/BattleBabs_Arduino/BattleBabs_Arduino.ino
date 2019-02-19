/*******************************************************
 * BATTLEBABS CLIENT SCOREKEEPING REMOTE ARDUINO PROGRAM
 * VERSION: 2
 * VERSION AUTHOR: TekCastPork
 ******************************************************/

/*
 * These arrays specify the digital pin each button is connected to, and the method/event to send if that
 * button is pushed. The number of methods must match the number of buttons for each category, so if
 * there are 4 buttons per team for scoring methods, there must be 4 scoring methods in the methods
 * array.
 * 
 * On an Arduino UNO board the maximum amount of buttons that can be used is 11, as 3 pins are not able to be used as inputs,
 * these unusable pins are pins 0, 1, and 13.
 * Pins 0 and 1 are not used as they are hooked into the TX and RX lines for serial communication, using these pins could corrupt Serial Communications
 * with the client python program.
 * 
 * Pin 13 is used as the Busy/Status LED on the controller, so it is an output instead of an inputs
 * 
 * This program should be compatible with other arduino flavors (mini, Mega, 101, ETC) So if more buttons are required an arduino with more
 * ports should be usable.
 */
#define NUM_OF_METHODS 4
const int team1Buttons[NUM_OF_METHODS] = {3,4,5,6}; // buttons for scoring methods that credit team 1
const int team2Buttons[NUM_OF_METHODS] = {7,8,9,10}; // buttons for scoring methods that credit team 2
const String methods[NUM_OF_METHODS] = {"rubberband","pingpong","shove","disable"}; // the scoring methods, number of methods must match number of buttons per team

//These methods are name sensitive but not CASE sensitive with the client program, 
//so "rubberband" and "RuBbErBaNd" would do the same thing, but "rubberband" and "rubber_band" are not considered the same


#define NUM_OF_SPEC 2
const int specialButtons[NUM_OF_SPEC] = {11,12}; // buttons for special buttons (start match, request next match)
const String specialEvents[NUM_OF_SPEC] = {"n","s"}; // events to send for the special buttons, n is request next match, s is start match


//pin 13 is the status LED
#define statusLED 13



void setup() {
  Serial.begin(9600); // Begin Serial Communications to python client program, 9600 baud

  for(int i = 0; i < NUM_OF_METHODS; i++) { // Setup the pins used as button inputs. They are setup using internal pullup resistors to prevent floating input issues
	pinMode(team1Buttons[i],INPUT_PULLUP);
	pinMode(team2Buttons[i],INPUT_PULLUP);
  }
  for(int i = 0; i < NUM_OF_SPEC; i++) { // Setup the pins used as special button inputs. These too are setup using internal pullup resistors to prevent floating inputs
	pinMode(specialButtons[i], INPUT_PULLUP);
  }
  //NOTE: Since the inputs are on pullup resistors, when the button is pushed the pin will be pulled to logic low (in this case ground), so to check for a button press,
  // a digitalRead() returning false should be tested for, not a return of true

  pinMode(statusLED,OUTPUT); // Setup the Status/Busy LED
  digitalWrite(statusLED, LOW); // status LED is off to begin

  //PySerial uses readline to complete a serial read, meaning any Serial communication in this arduino program must be done using the println method

  Serial.println("Ready."); // Sending this over serial is actually fine, as it wont be parsed by the client due to being an incorrect format

}

void loop() {
  //Check the special buttons for potential input
  for(int i = 0; i < NUM_OF_SPEC; i++) {

	if(digitalRead(specialButtons[i]) == false) { // Check to see if the button is pushed

	  delay(50); // debounce delay, since on the microsecond scale switched turn on and off very quickly for a few microseconds, a microprocessor CAN and WILL detect this bouncing, this prevents it

	  if(digitalRead(specialButtons[i]) == false) { // after the debouncing delay, verify the input state

		digitalWrite(statusLED,HIGH); // IF it was pushed we go into busy state as the command is sent and a user delay occurs, prevent very quick command sending
		Serial.println(specialEvents[i]); // send the command based on the button

		while(1) { // User input delay, wait for the button to be released before checking for new inputs
			if(digitalRead(specialButtons[i]) == true) {
				delay(50); //debounce delay
	  			if(digitalRead(specialButtons[i]) == false) { // after the debouncing delay, verify the input state
				  break; // break the while loop
				}
			}
		}

		digitalWrite(statusLED,LOW); // Busy state over, turn off Status LED
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
			while(1) { // User input delay, wait for the button to be released before checking for new inputs
				if(digitalRead(specialButtons[i]) == true) {
					delay(50); //debounce delay
						if(digitalRead(specialButtons[i]) == false) { // after the debouncing delay, verify the input state
						break; // break the while loop
					}
				}
			}
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
			while(1) { // User input delay, wait for the button to be released before checking for new inputs
				if(digitalRead(specialButtons[i]) == true) {
					delay(50); //debounce delay
						if(digitalRead(specialButtons[i]) == false) { // after the debouncing delay, verify the input state
						break; // break the while loop
					}
				}
			}
			digitalWrite(statusLED,LOW);
			}
		}
  }
  delay(20); // Speed limiting delay, 20ms
}
