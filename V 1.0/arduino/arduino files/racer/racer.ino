#include <Servo.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

/* Defines ------------------------------------------------------------------ */
#define button_pin      2
#define right_servo_pin 5
#define left_servo_pin  6
#define right_led       7
#define left_led        8
#define left_qti        A0
#define middle_qti      A1
#define right_qti       A2
#define min_pulse       1300
#define max_pulse       1700
#define standstill      1500
#define qti_threshold   ???   /// Input QTI threshold

RF24 radio(9, 10);

byte readQti(byte);
/* Class ------------------------------------------ */
class trackingAPI{
  private:
    const uint64_t timer_aadress = 0x0000000033;
    bool msg_sent = false;
    char robot_name[21];

  public:
    void setBotName(const char* name){
      if(name[0] == '\0' || strcmp(name, "RobotNameHere") == 0){
        Serial.println("Input robot name");
        while(1);
      }
      else if(strlen(name) > 21){
        Serial.println("Robot name too long");
        while(1);
      }
      else{
        strcpy(robot_name, name);
        Serial.print("Robot name: ");
        Serial.println(robot_name);
      }
    }

    void radioSetup(){
      radio.begin();
      radio.openWritingPipe(timer_aadress);
      radio.stopListening();
      if(radio.write(&robot_name, sizeof(robot_name))){
        Serial.println("Connection with timer established");
      }
      else{
        Serial.println(radio.write(&robot_name, sizeof(robot_name)));
        Serial.println("Connection with timer failed");
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
};
 
/* Global variables ------------------------------------------ */
Servo g_left_wheel;
Servo g_right_wheel;
trackingAPI tracking;

/* Private functions ------------------------------------------------- */
byte readQti (byte qti) {                               // Function to read current position on map
  digitalWrite(qti, HIGH);                              // Send an infrared signal
  delayMicroseconds(1000);                               // Wait for 1ms, very important!
  digitalWrite(qti, LOW);                               // Set the pin low again
  return ( analogRead(qti) > qti_threshold ? 1 : 0);    // Return the converted result: if analog value more then 100 return 1, else 0
}

void setWheels(int delay_left = 1500, int delay_right = 1500) {
  g_left_wheel.writeMicroseconds(delay_left);
  g_right_wheel.writeMicroseconds(delay_right);
  delay(20);
}

void setLed(byte value_left = LOW, byte value_right = LOW) {
  digitalWrite(right_led, value_right);
  digitalWrite(left_led, value_left);
}

/* Arduino functions ---------------------------------------------------------------- */
void setup() {
  /* Start serial monitor */
  Serial.begin(9600);

  /* Set the pin mode of LED pins as output */
  pinMode(right_led, OUTPUT);
  pinMode(left_led, OUTPUT);

  /* Attach servos to digital pins defined earlier */
  g_left_wheel.attach(left_servo_pin);
  g_right_wheel.attach(right_servo_pin);

  /* Initiate wheels to standstill */
  setWheels();

  /* Blinking LEDs for test */
  setLed(LOW, LOW);
  delay(500);
  setLed();
  delay(500);

  /*Radio setup*/
  tracking.setBotName("RobotNameHere");  // Input robot name (max 20 characters)
  tracking.radioSetup();
}

void loop() {
  tracking.sendName();
  /*
  Your code here:
  ...
  ...

  */



}
