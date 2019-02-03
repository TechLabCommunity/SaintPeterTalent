#include <Arduino.h>
#include <Wiegand.h>
#include <Wire.h>
#include <MsTimer2.h>
#include <LiquidCrystal_I2C.h>
#define DOOR_PIN 12
#define COLS 20
#define ROWS 4
#define ADDR_I2C 0x27
#define SEPARATOR '|'
#define TIMEOUT_WAIT 5000
#define TIME_RESET_LCD 900000UL //15 Minutes
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
unsigned long code = 0;
String response = "";
LiquidCrystal_I2C lcd(0x27, COLS, ROWS);
volatile bool need_reset_lcd = false;
int freeRam();

InfoMember get_infos(const String response, const char delimiter = SEPARATOR);

void print_rows(const String s1 = "", const String s2 = "", const String s3 = "", const String s4 = "");

void reset_lcd();

void setup()
{
  Serial.begin(9600);
  pinMode(DOOR_PIN, OUTPUT);
  digitalWrite(DOOR_PIN, LOW);
  wg.begin();
  lcd.begin();
  lcd.backlight();
  print_rows("TalentLab CA", "", "In funzione");
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
      print_rows("ACCESSO NEGATO", "ERRORE VINCOLO", "NO PARTNER");
      break;
    case 'b':
      print_rows("CODICE ERRATO", "--RIPROVARE--", member.custom_message);
      break;
    case 's':
      if (member.alarm_status == "2")
      {
        alarm_msg = "ALLARME OFF";
      }
      print_rows("CODICE VALIDO", "--ENTRATA--", member.custom_message, alarm_msg);
      digitalWrite(DOOR_PIN, HIGH);
      break;
    case 'a':
      if (member.alarm_status == "1")
      {
        alarm_msg = "     ALLARME ON";
      }
      print_rows("CODICE VALIDO", "--USCITA--", member.custom_message, alarm_msg);
      break;
    default:
      break;
    }
    response = "";
    code = 0;
    delay(TIMEOUT_WAIT);
    digitalWrite(DOOR_PIN, LOW);
    reset_lcd();
  }
}

InfoMember get_infos(const String response, const char delimiter)
{
  unsigned int i = 0;
  int col = 0;
  InfoMember member;
  member.action = response[0];
  while (i < response.length() && response[i] != '\n')
  {
    if (response[i] == delimiter)
    {
      col++;
    }
    else
    {
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
    }
    i++;
  }
  return member;
}

void print_rows(const String s1, const String s2, const String s3, const String s4)
{
  lcd.clear();
  String rows[ROWS];
  rows[0] = s1;
  rows[1] = s2;
  rows[2] = s3;
  rows[3] = s4;
  for (unsigned int i = 0; i < ROWS; i++)
  {
    lcd.setCursor(0, i);
    if (rows[i].length() > COLS)
    {
      rows[i].substring(0, 19);
    }
    else
    {
      unsigned offset = (COLS - rows[i].length()) / 2;
      for (unsigned int i = 0; i < offset; i++)
      {
        lcd.print(" ");
      }
    }
    lcd.print(rows[i]);
  }
}

void reset_lcd()
{
  if (need_reset_lcd)
    return;
  need_reset_lcd = true;
  Wire.end();
  lcd.begin();
  print_rows("TalentLab CA", "", "In funzione");
  need_reset_lcd = false;
}

int freeRam()
{
  extern int __heap_start, *__brkval;
  int v;
  return (int)&v - (__brkval == 0 ? (int)&__heap_start : (int)__brkval);
}