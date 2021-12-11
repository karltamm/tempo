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
    void RadioSetup(){
      Radio.begin();
      Radio.openWritingPipe(timer_address[0]);
      Radio.openReadingPipe(1, timer_address[1]);
      Radio.setPALevel(RF24_PA_LOW);  // Set amp level to -12dBm
      Radio.setRetries(5, 15);  // Set 15 retries with a delay of 1.5ms
      Radio.setDataRate(RF24_250KBPS);  // Set speed to 250 kbps to improve range
      Radio.setChannel(108);  // At 2.508 Ghz to limit interference from wifi channels
      Radio.startListening();
    }

    void listenRadio(){
      Radio.read(&buf, sizeof(buf));
      Serial.println(buf);
      buf[0] = '\0';
    }

    void sendmsg(char* msg){
      Radio.stopListening();
      if(Radio.write(msg, strlen(msg)+1)){
        if(strcmp(msg, "start_tr") == 0){
          Serial.println("Success");  // To verify the connection with timer
        }
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
  // Read messages from serial and send them to timer
  if(Serial.available()){
    Rad.sendmsg(Ser.readSP());
  }
  // Get messages from timer and write them to serial
  if(Radio.available()){
    Rad.listenRadio();
  }
}