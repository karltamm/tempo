#ifndef RADIO_H
#define RADIO_H

#include <Arduino.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

void radioSetup(void);
void radioTest(void);
void sendName(void);
byte readQti(byte);

#endif
