#include <Arduino.h>
#include <RF24.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <string.h>


RF24 Radio(6, 7);

class RadioConnection{
  private:
    const uint64_t timer_address[2] = {0x0000000022, 0xFFFFFFFF11};
    char buf[21];
    char* ptr;
  
  public:
    void RadioSetup(){  // Radio connection setup
      Radio.begin();
      Radio.openWritingPipe(timer_address[0]);
      Radio.openReadingPipe(1, timer_address[1]);
      Radio.setPALevel(RF24_PA_MIN);
      Radio.startListening();
    }

    void listenRadio(){  
      Radio.read(&buf, sizeof(buf));
      ptr = strtok(buf, " ");
      Serial.print("bot_name:");
      Serial.println(ptr);
      
      ptr = strtok(NULL, " ");
      Serial.print("time:");
      Serial.println(ptr);
      buf[0] = '\0';
    }

     void sendmsg(char* msg){
      Radio.stopListening();
      if(Radio.write(msg, strlen(msg)+1)){
        Serial.println("Success");  //delivery confirmation
      }
      Radio.startListening();
    }
};

class SerialConnection{
  private:
    int i = 0;
    char character;
    
  public:
    char buf[21];
    
    char* readSP(){
      while(1){
        character = Serial.read();
        if(character != '\n' && character > 0){
          buf[i] = character;
          i++;
        }
        else if(character == '\n'){
          buf[i] = '\0';
          i = 0;
          return buf;
        }
      }
      return 0;
    }
};

RadioConnection Rad;
SerialConnection Ser;

void setup() {
  Serial.begin(9600);

  Rad.RadioSetup();
}

void loop(){
  if(Serial.available()){
    Rad.sendmsg(Ser.readSP());
  }
  if(Radio.available()){
    Rad.listenRadio();
  }
}