#include "radio.h"

#define left_qti        A0
#define middle_qti      A1
#define right_qti       A2

RF24 radio(9, 10);  // Assign radio pins

/* Global variables ------------------------------------------ */
const uint64_t timer_aadress = 0x0000000033;
bool msg_sent = false;
extern char robot_name[15];


void radioSetup(){
    radio.begin();
    radio.openWritingPipe(timer_aadress);
    radio.stopListening();
}

void radioTest(){
  if(robot_name[0] == '\0'){
    Serial.println("Input robot name ");
  }
  else{
    if(radio.write(&robot_name, sizeof(robot_name))){
      Serial.println("Connection with timer established");
      Serial.print("Robot name: ");
      Serial.println(robot_name);
    }
    else{
      Serial.println("Connection with timer failed");
    }
  }
}

void sendName(){
  if(readQti(left_qti) && readQti(middle_qti) && readQti(right_qti)){
    if(!msg_sent && radio.write(&robot_name, sizeof(robot_name))){ 
      msg_sent = true;
    }
  }
  else{
    msg_sent = false;
  }
}
