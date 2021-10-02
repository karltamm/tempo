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
const uint64_t addresses[3] = {0xFFFFFFFF11, 0x0000000022, 0x0000000033}; //addresses(timer>PC, PC>timer, BOT>timer)
byte pipeNum=0;

float g_distance_in_cm = 0;
unsigned long start_time = 0;
unsigned long finish_time = 0;

char buf[21];
char lap_time[21], bot_name[21];

bool track = false;
bool correct_bot = false;
bool name_sent = false;


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

void resetLapTime(bool all = false){ //  resets lap time
  start_time = 0;
  lap_time[0] = '\0';
  correct_bot = false;
  recordingLap(false);
  if(all){
    bot_name[0] = '\0';
    name_sent = false;
  }
}

void recieveMsg(){
  if(radio.available(&pipeNum)){
    radio.read(&buf, sizeof(buf));
    if(pipeNum == 1){  // from pc
      if(strcmp(buf, "start_tr") == 0){  
        track = true;
      }
      else if(strcmp(buf, "stop_tr") == 0){
        track = false;
        resetLapTime(true);
      }
      else if(strcmp(buf, "reset_lap") == 0){
        resetLapTime();
      }
    }
    else if(pipeNum == 2 && (millis() - start_time) < 3000){  // from robots
      if(bot_name[0] == '\0'){
        strcpy(bot_name, buf);
        correct_bot = true;
      }
      else if(strcmp(buf, bot_name) == 0){
        correct_bot = true;
      }
    }
    buf[0] = '\0';
  }
}

void sendData(const char* name){
  radio.stopListening();
  radio.write(name, strlen(name)+1);
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
  radio.startListening();
}


void loop(){
  recieveMsg();
  if(track){
    // Lap start
    if (distance() < 10.00 && start_time == 0 && (finish_time == 0 || (millis() - finish_time) > 5000)){
        recordingLap();
        start_time = millis();
        finish_time = 0;
    }
    // Lap finish
    if (distance() < 10.00 && (millis() - start_time) > 10000 && start_time != 0){
      sprintf(lap_time, "%lu", millis() - start_time);
      finish_time = millis();
      sendData(lap_time);
      delay(50);
      if(!name_sent){
        sendData(bot_name);
        name_sent = true;
      }
      resetLapTime();
    }
    // Check if same bot on track
    if((millis() - start_time) > 3000 && start_time != 0 && !correct_bot){
      resetLapTime();
    }
  }
}