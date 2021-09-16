#include <Arduino.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <string.h>

/* Defines ------------------------------------------------------------------ */
#define button_pin      2
#define sonic_echo_pin  3
#define sonic_trig_pin  4
#define right_led       7
#define left_led        8

RF24 radio(9, 10);
const uint64_t addresses[3] = {0xF0F0F0FF11, 0xF0F0F0F022, 0xF0F0F0F033}; //addresses(timer>PC, PC>timer, BOT>ttimer)
byte pipeNum=0;


/* Global variables ------------------------------------------ */
float g_distance_in_cm = 0;
float lap_time;
unsigned long start_time = 0;
unsigned long finish_time = 0;
char buf[15], bot_name[15];


/* Private functions ------------------------------------------------- */
float distance() {
  digitalWrite(sonic_trig_pin, HIGH); // Make sonic_trig_pin HIGH
  delayMicroseconds(10); // Wait for 10us
  digitalWrite(sonic_trig_pin, LOW); // Make the pin low

  return pulseIn(sonic_echo_pin, HIGH) / 58.00; // Return the correct number in cm, you can make the conversion inline with return!
}

void recordingLap(bool recording = true){ //  Turn on LEDs if lap is being recorded
  if(recording){
    digitalWrite(right_led, HIGH);
    digitalWrite(left_led, HIGH);
  }
  else{
    digitalWrite(right_led, LOW);
    digitalWrite(left_led, LOW);
  }
  
}

void resetLapTime(){ //  resets lap time
  start_time = 0;
  bot_name[0] = '\0';
  buf[0] = '\0';
  lap_time = 0;
}

/* Arduino functions ---------------------------------------------------------------- */
void setup() {

  /* Start serial monitor */
  Serial.begin(9600);

  /* Set the LED pins */
  pinMode(right_led, OUTPUT);
  pinMode(left_led, OUTPUT);

  /* Set the ultrasonic sensor pins */
  pinMode(sonic_trig_pin, OUTPUT);
  pinMode(sonic_echo_pin, INPUT);
  distance();

  /* Set up radio */
  radio.begin();
  radio.openWritingPipe(addresses[0]);
  radio.openReadingPipe(1, addresses[1]);
  radio.openReadingPipe(2, addresses[2]);
  radio.setPALevel(RF24_PA_MIN);
  radio.startListening();
}


void loop(){
  if(radio.available(&pipeNum)){
    radio.read(&buf, sizeof(buf));
    if(pipeNum == 1){
      resetLapTime();
      recordingLap(false);
      finish_time = 0;
    }
    else if(pipeNum == 2 && (millis() - start_time) < 5000 && bot_name[0] == '\0'){
      strcpy(bot_name, buf);
    }
    buf[0] = '\0';
  }

  if (distance() < 10.00 && start_time == 0 && (finish_time == 0 || (millis() - finish_time) > 10000)){
    recordingLap();
    start_time = millis();
    finish_time = 0;
  }

  if (distance() < 10.00 && 10000 < (millis() - start_time) && start_time != 0){
    lap_time = (float)(millis() - start_time)/1000;
    finish_time = millis();

    radio.stopListening();
    radio.write(&bot_name, sizeof(bot_name));
    radio.write(&lap_time, sizeof(lap_time));
    radio.startListening();

    recordingLap(false);
    resetLapTime();
  }
}