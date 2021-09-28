#include <Arduino.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define button_pin      2
RF24 radio(9, 10);

/* Global variables ------------------------------------------ */
const uint64_t timer_address[2] = {0x0000000022, 0xFFFFFFFF11};
char bot_name[15];
double lap_time;

/* Button setup for testing ---------------------------------------------------------------- */
unsigned long g_last_debounce_time = 0;  // the last time the output pin was toggled
unsigned long g_debounce_delay = 50;    // the debounce time; increase if the output flickers
int g_button_state;             // the current reading from the input pin
int g_last_button_state = LOW;

byte buttonRead() {
  int reading = digitalRead(button_pin);
  if (reading != g_last_button_state){
    g_last_debounce_time = millis();
  }
  if ((millis() - g_last_debounce_time) > g_debounce_delay) {
    if (reading != g_button_state) {
      g_button_state = reading;
      if (g_button_state == HIGH) {
        return 1;
      }
    }
  }
  g_last_button_state = reading;
  return 0;

}
/* Arduino functions ---------------------------------------------------------------- */
void setup() {
  /* Start serial monitor */
  Serial.begin(9600);

  pinMode(button_pin, INPUT);
  
  /* Radio setup */
  radio.begin();
  radio.openWritingPipe(timer_address[0]);
  radio.openReadingPipe(1, timer_address[1]);
  radio.setPALevel(RF24_PA_MIN);
  radio.startListening();

}


void loop() {
  if (buttonRead() == 1){
    radio.stopListening();
    radio.write("reset", 6);
    radio.startListening();
  }

  if(radio.available()){
    if(bot_name[0] == '\0'){
      Serial.print("bot_name:");
      radio.read(&bot_name, sizeof(bot_name));
      Serial.println(bot_name);
    }
    else{
      radio.read(&lap_time, sizeof(lap_time));
      Serial.print("lap_time:");
      Serial.println(lap_time, 3);
      bot_name[0] = '\0';
    }

  }
}