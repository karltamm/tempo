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
int bot_nr = 0;
bool tracking = false;
int i;

class RadioCon{
  private:
    const uint64_t pc_address[2] = {0xFFFFFFFF11, 0x0000000022}; //addresses(timer>PC, PC>timer)
    char buf[21];
  
  public:
    void RadioSetup(){
      Radio.begin();
      Radio.openWritingPipe(pc_address[0]);
      Radio.openReadingPipe(1, pc_address[1]);
      Radio.setPALevel(RF24_PA_MIN);
      Radio.startListening();
    }

   	void recieveMsg(){
	   	if(Radio.available()){
    		Radio.read(&buf, sizeof(buf));
			if(strcmp(buf, "start_tr") == 0){  
				tracking = true;
			}
			else if(strcmp(buf, "stop_tr") == 0){
				tracking = false;
			}
			else if(strcmp(buf, "reset_lap: ") == 0){
			}
		}
    	buf[0] = '\0';
  	}

	void sendData(uint32_t name, uint32_t time){
		char msg[21], buf[10];
		sprintf(msg, "%lX", name);
		sprintf(buf, "%lu", time);
		strcat(msg, " ");
		strcat(msg, buf);
		Serial.println(msg);
    	Radio.stopListening();
    	Radio.write(&msg, sizeof(msg));
    	Radio.startListening();
	}
};

class Tracking{
	private:
		uint32_t start_time = 0;
		
	public:
		uint32_t bot_name;

		void start(uint32_t time_buf){
			start_time = time_buf;
		}

		uint32_t finish(uint32_t time_buf){
			return time_buf - start_time;
		}

		int error(uint32_t time_buf){
			if(start_time && 20000 < (millis() - start_time) && (millis() - start_time) < 60000){
				return 0;
			}
			else{
				start(time_buf);
				return 1;
			}
		}

		void resetLapTime(){ //  resets lap time
			start_time = 0;
		}
};
RadioCon rad;
Tracking botsOnTrack[10];

void removeBot(int index){
	for(int i = index;botsOnTrack[i].bot_name && i<bot_nr ;i++){
		botsOnTrack[i] = botsOnTrack[i+1];
	}
}

void setup()
{
	Serial.begin(9600);

	alt_soft_serial.begin(RDM6300_BAUDRATE);
	rdm6300.begin(&alt_soft_serial);

	/* Set up radio */
	rad.RadioSetup();
}

void loop(){	
	if (rdm6300.update() && millis() - buf_time > 3000){
		buf_time = millis();  // Record detection time
		buf_name = rdm6300.get_tag_id();  // Get Tag ID
		for(i = 0; i<bot_nr; i++){
			if(buf_name == botsOnTrack[i].bot_name && !botsOnTrack[i].error(buf_time)){
				rad.sendData(botsOnTrack[i].bot_name, botsOnTrack[i].finish(buf_time));
				removeBot(i);
				bot_nr--;
				break;
			}
		}
		if(i == bot_nr){
			botsOnTrack[bot_nr].bot_name = buf_name;
			botsOnTrack[bot_nr].start(buf_time);
			bot_nr++;
		}
	}
}