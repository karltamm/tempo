#include <Arduino.h>
#include <RF24.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <string.h>


RF24 Radio(9, 10);

class RadioCon{
  private:
    const uint64_t timer_address[2] = {0x0000000022, 0xFFFFFFFF11};
    char buf[21];
    char* ptr;
  
  public:
    void RadioSetup(){
      Radio.begin();
      Radio.openWritingPipe(timer_address[0]);
      Radio.openReadingPipe(1, timer_address[1]);
      Radio.setPALevel(RF24_PA_MIN);
      Radio.startListening();
    }

    void listenRadio(){
      Radio.read(&buf, sizeof(buf));
      ptr = strtok(buf, " ");
      Serial.print("Bot_name:");
      Serial.println(ptr);
      
      ptr = strtok(NULL, " ");
      Serial.print("Lap_time:");
      Serial.println(ptr);
    }

     void sendmsg(char* msg){
      Radio.stopListening();
      Radio.write(msg, strlen(msg)+1);
      Radio.startListening();
      buf[0] = '\0';
    }
};

class SerialCon{
  private:
    int i = 0;
    char letter;
    char ser_buf[21];

  public:
    char* readSP(){
      while(1){
        letter = Serial.read();
        if(letter != '\n' && letter > 0){
          ser_buf[i] = letter;
          i++;
        }
        else if(letter == '\n'){
          ser_buf[i] = '\0';
          i = 0;
          return ser_buf;
        }
      }
      return 0;
    }
};

RadioCon Rad;
SerialCon Ser;

void setup() {

  Serial.begin(9600);


  Rad.RadioSetup();
}

void loop(){
  if(Serial.available()){
    //Serial.println(Ser.readSP());
    //Rad.sendmsg(Ser.readSP());
  }
  if(Radio.available()){
    Rad.listenRadio();
  }
}