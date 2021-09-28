#include <Arduino.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>


/* Defines ------------------------------------------------------------------ */
#define sonic_echo_pin  3
#define sonic_trig_pin  4
#define right_led       7
#define left_led        8

RF24 radio(9, 10);

/* Global variables ------------------------------------------ */
const uint64_t addresses[3] = {0xFFFFFFFF11, 0x0000000022, 0x0000000033}; //addresses(timer>PC, PC>timer, BOT>ttimer)
byte pipeNum=0;

float g_distance_in_cm = 0;
double lap_time;
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
  lap_time = 0;
  bot_name[0] = '\0'; 
}

void recieveMsg(){
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
}

void sendMsg(char name[15], double time){
  radio.stopListening();
  if(name[0] == '\0'){
    radio.write("noName", 7);
  }
  else{
    radio.write(&bot_name, sizeof(bot_name));
  }
  radio.write(&lap_time, sizeof(lap_time));
  radio.startListening();
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
  radio.openWritingPipe(addresses[0]);     // writing pipe to PC
  radio.openReadingPipe(1, addresses[1]);  // reading pipe from PC
  radio.openReadingPipe(2, addresses[2]);  // reading pipe from robots
  radio.setPALevel(RF24_PA_MIN);
  radio.startListening();
}


void loop(){
  recieveMsg();

  // Lap start
  if (distance() < 10.00 && start_time == 0 && (finish_time == 0 || (millis() - finish_time) > 5000)){
    recordingLap();
    start_time = millis();
    finish_time = 0;
  }

  // Lap finish
  if (distance() < 10.00 && (millis() - start_time) > 10000 && start_time != 0){
    lap_time = (double)(millis() - start_time)/1000;
    finish_time = millis();

    sendMsg(bot_name, lap_time);
    recordingLap(false);
    resetLapTime();
  }
}