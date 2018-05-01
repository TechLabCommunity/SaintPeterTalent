#include <MsTimer2.h>
#include <Wiegand.h>
#define N_PINS 3
#define DOOR_PIN 12


const unsigned PINS[N_PINS] = {4,5,6};
WIEGAND wg;
long code = -1;
volatile unsigned int count_res = 0;

void turn_off(){
  for (int i=0; i<N_PINS; i++){
    digitalWrite(PINS[i], HIGH);
  }
  digitalWrite(DOOR_PIN, LOW);
  MsTimer2::stop();
}



void setup() {
  Serial.begin(9600);
  for (int i=0; i<N_PINS; i++){
    pinMode(PINS[i], OUTPUT);
    digitalWrite(PINS[i], HIGH);
  }
  pinMode(DOOR_PIN, OUTPUT);
  digitalWrite(DOOR_PIN, LOW);
  wg.begin();
  MsTimer2::set(3000, turn_off);
}

void loop() {
  if (wg.available())
  {
    long code = wg.getCode();
    if (code > 0) {
      Serial.println(String(code) + "#");
    }

  }
  if (Serial.available()){
    char c = (char)Serial.read();
    switch(c){
      case 'c':
        digitalWrite(PINS[0], LOW);
        count_res++;
      case 'b':
        digitalWrite(PINS[1], LOW);
        count_res++;
      case 'a':
        digitalWrite(PINS[2], LOW);
        count_res++;
        if (count_res == 1){
          digitalWrite(DOOR_PIN, HIGH);
        }
        count_res = 0;
        MsTimer2::start();
        break;
    }
  }
  code = -1;
}
