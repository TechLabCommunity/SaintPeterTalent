#include <MsTimer2.h>
#include <Wiegand.h>
#define N_PINS 3


const unsigned PINS[N_PINS] = {4,5,6};
WIEGAND wg;
long code = -1;
volatile bool are_on = false;

void turn_off(){
  for (int i=0; i<N_PINS; i++){
    digitalWrite(PINS[i], HIGH);
  }
  are_on = false;
}


void setup() {
  Serial.begin(9600);
  for (int i=0; i<N_PINS; i++){
    pinMode(PINS[i], OUTPUT);
    digitalWrite(PINS[i], HIGH);a
  }
  wg.begin();
  MsTimer2::set(3000, turn_off);
}

void loop() {
  if (wg.available())
  {
    long code = wg.getCode();
    if (code > 0) {
      Serial.println(String(code) + "#");
      Serial.flush();
    }

  }
  if (Serial.available()){
    char c = (char)Serial.read();
    switch(c){
      case 'c':
        digitalWrite(PINS[0], LOW);
      case 'b':
        digitalWrite(PINS[1], LOW);
      case 'a':
        digitalWrite(PINS[2], LOW);
        are_on = true;
        MsTimer2::start();
        break;
    }
  }
  if (!are_on){
    MsTimer2::stop();
  }
  code = -1;
}
