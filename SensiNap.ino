#define LED 4        // Pin number for the LED
#define Buzzer 11    // Pin number for the Buzzer

byte signal;        // Variable to store the received signal

void setup() {
  pinMode(LED, OUTPUT);      // Set LED pin as output
  pinMode(Buzzer, OUTPUT);   // Set Buzzer pin as output

  Serial.begin(9600);        // Initialize serial communication
}

void loop() {
  if (Serial.available() > 0) {   // Check if there is data available to read
    signal = Serial.read();       // Read the received signal

    if (signal == 'T') {
      // If the received signal is 'T'
      // Turn on the LED and Buzzer for a short duration
      digitalWrite(LED, HIGH);
      digitalWrite(Buzzer, HIGH);
      delay(200);
      digitalWrite(LED, LOW);
      digitalWrite(Buzzer, LOW);
      delay(150);
    } else if (signal == 'F') {
      // If the received signal is 'F'
      // Turn off the LED and Buzzer
      digitalWrite(LED, LOW);
      digitalWrite(Buzzer, LOW);
    }
  }
}
