#include <Arduino.h>
#include <rdm6300.h>
#include <RF24.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <AltSoftSerial.h>

#define RDM6300_RX_PIN 8

RF24 Radio(6, 7);
Rdm6300 rdm6300;
AltSoftSerial alt_soft_serial;

/* Global variables*/
uint32_t buf_time;
uint32_t buf_name;
bool tracking = false;

class RadioConnection{
  private:
    const uint64_t pc_address[2] = {0xFFFFFFFF11, 0x0000000022}; //addresses(timer>PC, PC>timer)
    char buf[21];
  
  public:
    void RadioSetup(){
      Radio.begin();
      Radio.openWritingPipe(pc_address[0]);
      Radio.openReadingPipe(1, pc_address[1]);
      Radio.setPALevel(RF24_PA_LOW);
	  Radio.setRetries(3, 5);
      Radio.startListening();
    }

   	void recieveMsg(){
		Radio.read(&buf, sizeof(buf));
		Serial.println(buf);
		if(strcmp(buf, "start_tr") == 0){
			tracking = true;
		}
		else if(strcmp(buf, "stop_tr") == 0){
			tracking = false;
		}
    	buf[0] = '\0';
  	}

	void sendData(uint32_t name, uint32_t time){
		char msg[21], buf[10];
		sprintf(msg, "%lX", name);
		sprintf(buf, "%lu", time);
		strcat(msg, ":");
		strcat(msg, buf);
		Serial.println(msg);
    	Radio.stopListening();
    	Radio.write(msg, strlen(msg)+1);
    	Radio.startListening();
	}
};

RadioConnection rad;

void setup()
{
	/*Serial setup*/
	Serial.begin(9600);

	/*RFID setup*/
	alt_soft_serial.begin(RDM6300_BAUDRATE);
	rdm6300.begin(&alt_soft_serial);

	/*Radio setup*/
	rad.RadioSetup();
}

void loop(){
	if(Radio.available()){
		rad.recieveMsg();
	}
	if (tracking && rdm6300.update()){
		buf_name = rdm6300.get_tag_id();
		if(millis() - buf_time > 2000 ){
			buf_time = millis();  // Record detection time
			rad.sendData(buf_name, buf_time);
		}
		buf_name = 0;
	}
}