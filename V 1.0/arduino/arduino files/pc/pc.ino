#include <RF24.h>
#include <SPI.h>
#include <nRF24L01.h>

RF24 radio(9, 10);

/* Global variables ------------------------------------------ */
const uint64_t timer_address[2] = {0x0000000022, 0xFFFFFFFF11};
char buf_in[21];
char buf_out[21];
char letter;
int i = 0;

/* Functions ------------------------------------------ */
void sendmsg(){
  radio.stopListening();
  radio.write(buf_out, sizeof(buf_out));
  radio.startListening();
  buf_out[0] = '\0';

}

void readSP(){
  letter = Serial.read();
  if(letter != '\n' && letter > 0){
    buf_out[i] = letter;
    i++;
  }
  else if(letter == '\n'){
    buf_out[i] = '\0';
    i = 0;
    sendmsg();
  }
}

 void listenRadio(){
  radio.read(&buf_in, sizeof(buf_in));
  if(buf_in[0] >= 48 && buf_in[0] <= 57){
    Serial.print("lap_time:");
    Serial.println(buf_in);
  }
  else{
    Serial.print("bot_name:");
    Serial.println(buf_in);
  }
  buf_in[0] = '\0';
 }

/* Arduino functions ---------------------------------------------------------------- */
void setup() {
  /* Start serial monitor */
  Serial.begin(9600);

  /* Radio setup */
  radio.begin();
  radio.openWritingPipe(timer_address[0]);
  radio.openReadingPipe(1, timer_address[1]);
  radio.setPALevel(RF24_PA_MIN);
  radio.startListening();
}

void loop(){
  if(Serial.available()){
    readSP();
  }
  if(radio.available()){
    listenRadio();
  }
}