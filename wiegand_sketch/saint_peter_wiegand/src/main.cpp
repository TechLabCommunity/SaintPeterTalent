#include <Arduino.h>
#include <Wiegand.h>
#include <Wire.h>
#include <MsTimer2.h>
#include <avr/io.h>
#include <avr/wdt.h>
#include <LiquidCrystal_I2C.h>
#define DOOR_PIN 12
#define COLS 20
#define ROWS 4
#define ADDR_I2C 0x27
#define SEPARATOR '|'
#define TIMEOUT_WAIT 5000
#define TIME_RESET_LCD 15 * 60 * 1000
#define Reset_AVR()      \
  wdt_enable(WDTO_30MS); \
  while (1)              \
  {                      \
  }

#ifndef MAGIC_NUMBER
#define MAGIC_NUMBER 0 //define into platformio.ini
#endif
#define STATUS_MEMORY_CODE 999998

#define RESPONSE_BYPASS "s||||||BYPASS|0"

typedef struct
{
  char action;
  String name = "", surname = "", code = "", alarm_status = "", custom_message = "";
  uint8_t type_enter = 0;
} InfoMember;

WIEGAND wg;
unsigned int count_res = 0;
unsigned long code = 0;
String response = "";
LiquidCrystal_I2C lcd(0x27, 20, 4);
volatile bool need_reset_lcd = false;

int freeRam()
{
  extern int __heap_start, *__brkval;
  int v;
  return (int)&v - (__brkval == 0 ? (int)&__heap_start : (int)__brkval);
}

InfoMember get_infos(String response, char delimiter = SEPARATOR);

void print_rows(String s1, String s2, String s3, String s4);

void reset_lcd()
{
  need_reset_lcd = true;
  Wire.end();
  lcd.begin();
  print_rows(String("    TalentLab CA"), String(""), String("    In funzione"), String(""));
  need_reset_lcd = false;
}

void setup()
{
  Serial.begin(9600);
  pinMode(DOOR_PIN, OUTPUT);
  digitalWrite(DOOR_PIN, LOW);
  wg.begin();
  lcd.begin();
  lcd.backlight();
  print_rows(String("    TalentLab CA"), String(""), String("    In funzione"), String(""));
  MsTimer2::set(TIME_RESET_LCD, reset_lcd);
  MsTimer2::start();
}

void loop()
{
  if (wg.available())
  {
    code = wg.getCode();
    if (code > 999 && code != MAGIC_NUMBER && code != STATUS_MEMORY_CODE)
    {
      Serial.println(String(code) + "#");
    }
    Serial.flush();
  }
  else if (Serial.available())
  {
    response = Serial.readString();
    response.trim();
  }
  else if (code == MAGIC_NUMBER)
  {
    response = RESPONSE_BYPASS;
  }
  else if (code == STATUS_MEMORY_CODE)
  {
    response = String("b|||||") + String("|") + String(freeRam()) + String("|") + "0";
  }
  if (response.length() > 0 && !need_reset_lcd)
  {
    InfoMember member = get_infos(response);
    String alarm_msg = "";
    switch (member.action)
    {
    case 'c':
      print_rows(String("ACCESSO NEGATO"), String("   ERRORE VINCOLO"), String("     NO PARTNER"), String(""));
      break;
    case 'b':
      print_rows(String("    CODICE ERRATO"), String("    --RIPROVARE--"), member.custom_message, String(""));
      break;
    case 's':
      if (member.alarm_status == "2")
      {
        alarm_msg = "     ALLARME OFF";
      }
      print_rows(String("   CODICE VALIDO"), String("    --ENTRATA--"), member.custom_message, String(alarm_msg));
      digitalWrite(DOOR_PIN, HIGH);
      break;
    case 'a':
      if (member.alarm_status == "1")
      {
        alarm_msg = "     ALLARME ON";
      }
      print_rows(String("   CODICE VALIDO"), String("     --USCITA--"), member.custom_message, String(alarm_msg));
      break;
    default:
      break;
    }
    response = "";
    code = 0;
    delay(TIMEOUT_WAIT);
    digitalWrite(DOOR_PIN, LOW);
    Wire.end();
    lcd.begin();
    print_rows(String("    TalentLab CA"), String(""), String("    In funzione"), String(""));
  }
}

InfoMember get_infos(String response, char delimiter)
{
  unsigned int i = 0;
  int col = 0;
  InfoMember member;
  member.action = response[0];
  int c = 0;
  while (i < response.length() && response[i] != '\n' && c < 80)
  {
    if (response[i] == delimiter)
    {
      col++;
      i++;
      continue;
    }
    switch (col)
    {
    case 1:
      member.name += response[i];
      break;
    case 2:
      member.surname += response[i];
      break;
    case 3:
      member.type_enter = ((String)response[i]).toInt();
      break;
    case 4:
      member.code += response[i];
      break;
    case 5:
      member.alarm_status += response[i];
      break;
    case 6:
      member.custom_message += response[i];
      break;
    }
    i++;
    c++;
  }
  return member;
}

void print_rows(String s1, String s2, String s3, String s4)
{
  lcd.clear();
  lcd.setCursor(0, 0);
  s1.substring(0, 19);
  lcd.print(s1);
  lcd.setCursor(0, 1);
  s2.substring(0, 19);
  lcd.print(s2);
  lcd.setCursor(0, 2);
  s3.substring(0, 19);
  lcd.print(s3);
  lcd.setCursor(0, 3);
  s4.substring(0, 19);
  lcd.print(s4);
}