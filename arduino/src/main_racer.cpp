#include <Arduino.h>
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
#define qti_threshold   408

RF24 radio(9, 10);

 
/* Global variables ------------------------------------------ */
Servo g_left_wheel;
Servo g_right_wheel;
char robot_name[15] = "namesafjdspag[ajk[akasvjp]";

/* Private functions ------------------------------------------------- */

byte readQti (byte qti) {                               // Function to read current position on map
  digitalWrite(qti, HIGH);                              // Send an infrared signal
  delayMicroseconds(1000);                               // Wait for 1ms, very important!
  digitalWrite(qti, LOW);                               // Set the pin low again
  return ( analogRead(qti) > qti_threshold ? 1 : 0);    // Return the converted result: if analog value more then 100 return 1, else 0
}

class trackingAPI{
  private:
    const uint64_t timer_aadress = 0x0000000033;
    bool msg_sent = false;

    void radioSetup(){
      radio.begin();
      radio.openWritingPipe(timer_aadress);
      radio.stopListening();
    } 

  public:
    void radioTest(){
      radioSetup();
      if(robot_name[0] == '\0'){
        Serial.println("Input robot name");
      }
      else if(strlen(robot_name)>15){
        Serial.println("Robot name too long");
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
};

trackingAPI test;

void setWheels(int delay_left = 1500, int delay_right = 1500) {
  g_left_wheel.writeMicroseconds(delay_left);
  g_right_wheel.writeMicroseconds(delay_right);
  delay(20);
}

void setLed(byte value_left = LOW, byte value_right = LOW) {
  digitalWrite(right_led, value_right);
  digitalWrite(left_led, value_left);
}

void forward(int t){
  setLed(LOW, LOW);
  setWheels(1600, 1400);
  delay(t);
}

void right(int t){
  setLed(LOW, HIGH);
  setWheels(1600, 1600);
  delay(t);
  setWheels();
  setLed(LOW, LOW);
}

void left (int t){
  setLed(HIGH, LOW);
  setWheels(1400, 1400);
  delay(t);
  setWheels();
  setLed(LOW, LOW);
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

  /* Radio test*/
  test.radioTest();
}

void loop() {
  test.sendName();
  /*if (readQti(left_qti) && readQti(middle_qti) && readQti(right_qti)){ // All sensors on finish line
    setLed(HIGH, HIGH);
  }
  else if (!readQti(left_qti) && !readQti(right_qti)){ // Both sensors on white
    forward(10);
  }
  else if (!readQti(left_qti) && readQti(right_qti)){ // Left sensor on white, right on black
    right(100);
  }
  else if (readQti(left_qti) && !readQti(right_qti)){ // Right sensor on white, Left on black
    left(100);
  }*/
}
