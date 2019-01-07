#include <Arduino.h>
#include <MsTimer2.h>
#include <Wiegand.h>
#include <avr/io.h>
#include <avr/wdt.h>
#include <LiquidCrystal_I2C.h>
#define DOOR_PIN 12
#define MAGIC_NUMBER 2708801 //complete
#define COLS 20
#define ROWS 4
#define ADDR_I2C 0x27

typedef struct
{
  char action;
  String name = "", surname = "", code = "", alarm_status = "", custom_message = "";
  uint8_t type_enter = 0;
} InfoMember;

WIEGAND wg;
volatile bool is_finished = true;
volatile bool yet_print = false;
unsigned int count_res = 0;
unsigned long code = 0;
LiquidCrystal_I2C screen(ADDR_I2C, COLS, ROWS);
String response = "";

void turn_off()
{
  digitalWrite(DOOR_PIN, LOW);
  MsTimer2::stop();
  is_finished = true;
  yet_print = false;
}

InfoMember get_infos(String response, char delimiter = '|');

void screen_print(String *rows, uint8_t length);

void setup()
{
  Serial.begin(9600);
  screen.begin();
  screen.backlight();
  pinMode(DOOR_PIN, OUTPUT);
  digitalWrite(DOOR_PIN, LOW);
  wg.begin();
  MsTimer2::set(6000, turn_off);
  screen.clear();
  delay(2000);
}

void loop()
{
  if (is_finished && !yet_print)
  {
    String rows_composite[] = {"TalentLab CA", "", "In funzione"};
    screen_print(rows_composite, 3);
    yet_print = true;
  }
  if (wg.available())
  {
    code = wg.getCode();
    if (code > 999)
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
  if (response.length() > 0)
  {
    bool is_valid_action = true;
    InfoMember member = get_infos(response);
    String compound_rows[4];
    switch (member.action)
    {
    case 'c':
      compound_rows[0] = "Errore di vincolo";
      compound_rows[1] = "--ACCESSO NEGATO--";
      break;
    case 'b':
      compound_rows[0] = "Codice errato";
      compound_rows[1] = "--RIPROVARE--";
      break;
    case 's':
      digitalWrite(DOOR_PIN, HIGH);
      compound_rows[0] = "Codice valido";
      compound_rows[1] = "--ENTRATA--";
      break;
    case 'a':
      compound_rows[0] = "Codice valido";
      compound_rows[1] = "--USCITA--";
      break;
    default:
      is_valid_action = false;
      break;
    }
    if (is_valid_action)
    {
      if (member.alarm_status == "1")
      {
        compound_rows[2] = "ALLARME ON";
      }
      else if (member.alarm_status == "2")
      {
        compound_rows[2] = "ALLARME OFF";
      }
      else
      {
        compound_rows[2] = "";
      }
      if (member.custom_message.length() > 0)
      {
        compound_rows[3] = member.custom_message;
      }
    }
    else
    {
      String not_valid[] = {"Azione non valida"};
      screen_print(not_valid, 1);
    }
    screen_print(compound_rows, 4);
    is_finished = false;
    MsTimer2::start();
    response = "";
    code = 0;
  }
}

InfoMember get_infos(String response, char delimiter)
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
  }
  return member;
}

void screen_print(String *rows, uint8_t length)
{
  if (length == 0)
    return;
  uint8_t i = 0;
  screen.clear();
  screen.home();
  uint8_t max_rows = min(length, COLS);
  while (i < max_rows)
  {
    screen.setCursor(0, i);
    String row_to_print = rows[i];
    uint8_t n_spaces = (COLS - row_to_print.length()) / 2;
    if (row_to_print.length() < COLS)
    {
      for (uint8_t j = 0; j < n_spaces; j++)
      {
        screen.print(" ");
      }
      screen.print(row_to_print);
    }
    else
    {
      screen.print(row_to_print.substring(COLS - 1));
    }
    i++;
  }
}