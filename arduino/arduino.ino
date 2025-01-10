// This file is part ot the MicroWind project, a wind tunnel and wind turbine model
// Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
// The MicroWind software is licensed under GPLv3
// Authors: Felix Prigge

//LIBRARIES
#include <Wire.h>
#include <INA219_WE.h>
INA219_WE CurrentSensor = INA219_WE(0x40);
#define I2C_ADDRESS
#include <Servo_Hardware_PWM.h>
Servo PitchServo;

// PIN DEFINITION
const int PIN_SERVO               = 2;
const int PIN_TURBINE_TACHO       = 18;
const int PIN_FAN_TACHO           = 19;
const int PIN_FAN_PWM             = 45;
const int PIN_FORCE_CLK           = 8;
const int PIN_FORCE_DATA          = 9;
const int PIN_TORQUE_1            = 22;
const int PIN_TORQUE_2            = 23;
const int PIN_TORQUE_3            = 24;
const int PIN_TORQUE_4            = 25;
const int PIN_TORQUE_5            = 26;
const int PIN_TORQUE_6            = 27;
const int PIN_TORQUE_START        = 30;
const int PIN_LED                 = 13;
const int PIN_ANEMOMETER          = A0;
const int PIN_POTENTIOMETER       = A1;

// VARIABLES
uint8_t fan_pwm                           = 0;
uint16_t us_servo                         = 1500;
volatile unsigned long time_fan_tick      = micros();
volatile unsigned long time_turbine_tick  = micros();
unsigned long dt_fan_mean                 = 0;
unsigned long dt_turbine_mean             = 0;
volatile bool rotating_fan                = false;
volatile bool rotating_turbine            = false;
uint16_t speed_fan                        = 0;
uint16_t speed_turbine                    = 0;
float currentfloat                        = 0;
uint16_t current                          = 0;
float voltagefloat                        = 0;
uint16_t voltage                          = 0;
uint32_t thrust_force                     = 0;
uint32_t thrust_force_offset              = 0;
uint16_t anemometer                       = 0;
uint16_t potentiometer                    = 0;
uint8_t torque_level                      = 0;
uint8_t * torque_level_pointer            = &torque_level;
int torque_toggle                         = 1;
int * torque_toggle_pointer               = &torque_toggle;
uint8_t led                               = 0;

// ROTARY BUFFERS
volatile unsigned long rot_turbine_tick[8];  // 8 values stored for averaging (1/2 revolution)
uint8_t pos_turbine_tick = 0;
volatile unsigned long rot_fan_tick[2];      // 2 values stored for averaging (1 revolutions)
uint8_t pos_fan_tick = 0;

void setup() {
  // put your setup code here, to run once:
  // attach servo
  PitchServo.attach(PIN_SERVO);
  PitchServo.writeMicroseconds(1500);
  Wire.begin();

  // define pin functions
  pinMode(PIN_TURBINE_TACHO, INPUT);
  pinMode(PIN_FAN_TACHO, INPUT_PULLUP);
  pinMode(PIN_FAN_PWM, OUTPUT);
  analogWrite(PIN_FAN_PWM, 0);
  pinMode(PIN_FORCE_CLK, OUTPUT);
  digitalWrite(PIN_FORCE_CLK, LOW);
  pinMode(PIN_FORCE_DATA, INPUT);
  pinMode(PIN_TORQUE_1, OUTPUT);
  digitalWrite(PIN_TORQUE_1, LOW);
  pinMode(PIN_TORQUE_2, OUTPUT);
  digitalWrite(PIN_TORQUE_2, LOW);
  pinMode(PIN_TORQUE_3, OUTPUT);
  digitalWrite(PIN_TORQUE_3, LOW);
  pinMode(PIN_TORQUE_4, OUTPUT);
  digitalWrite(PIN_TORQUE_4, LOW);
  pinMode(PIN_TORQUE_5, OUTPUT);
  digitalWrite(PIN_TORQUE_5, LOW);
  pinMode(PIN_TORQUE_6, OUTPUT);
  digitalWrite(PIN_TORQUE_6, LOW);
  pinMode(PIN_TORQUE_START, OUTPUT);
  digitalWrite(PIN_TORQUE_START, HIGH);
  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, HIGH);
  pinMode(PIN_ANEMOMETER, INPUT);
  pinMode(PIN_POTENTIOMETER, INPUT);
  
  CurrentSensor.init();
  CurrentSensor.setADCMode(BIT_MODE_12);// 12 Bit Resolution
  CurrentSensor.setMeasureMode(CONTINUOUS); // choose mode and uncomment for change of default
  CurrentSensor.setPGain(PG_40);// max 0.4 A
  CurrentSensor.setBusRange(BRNG_16); // max 16V

  delay(10);
  // set gain for force sensor
  hx711_set_gain();
  delay(500);
  thrust_force_offset = hx711_read_force();

  // change the timer 5 prescaler to increase the PWM frequency for the fan. Leave everyting else as is
  TCCR5B = TCCR5B & 0b11111000 | 0x02; //Timer 5 is a 16-Bit timer. Prescaler set to 8. Resulting frequency ~ 8kHz 
  
  // set timer 4 for the torque level toggle interrupt. Thanks to https://dbuezas.github.io/arduino-web-timers
  TCCR4B = (1<<WGM42) | (1<<CS41); // CTC-mode, prescaler = 8
  TIMSK4 = 1<<OCIE4A;
  OCR4A = 10000; // toggle every 5ms (ORC4A*prescaler/16Mhz)

  // attach pin interrupt functions
  attachInterrupt(digitalPinToInterrupt(PIN_TURBINE_TACHO), turbine_interrupt, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_FAN_TACHO), fan_interrupt, CHANGE);

  // begin serial connection
  Serial.begin(38400);
  delay(100);
  digitalWrite(PIN_LED, LOW);  
}

void loop() {
  // put your main code here, to run repeatedly:

  // wait for data request
  while (Serial.available() == 0) {}
  Serial.read();

  // calculate data
  noInterrupts();
  if (rotating_fan == true) {
    if (micros() - time_fan_tick < 500000ul) {
      dt_fan_mean = rot_fan_tick[0];
      dt_fan_mean += rot_fan_tick[1];
      dt_fan_mean /= 2;
      speed_fan = 60000000 / dt_fan_mean / 2; // two ticks per rotation
    }
    else {
      speed_fan = 0;
      rotating_fan = false;
    }
  }
  if (rotating_turbine == true) {
    if (micros() - time_turbine_tick < 625000ul) {
      dt_turbine_mean = rot_turbine_tick[0];
      dt_turbine_mean += rot_turbine_tick[1];
      dt_turbine_mean += rot_turbine_tick[2];
      dt_turbine_mean += rot_turbine_tick[3];
      dt_turbine_mean += rot_turbine_tick[4];
      dt_turbine_mean += rot_turbine_tick[5];
      dt_turbine_mean += rot_turbine_tick[6];
      dt_turbine_mean += rot_turbine_tick[7];
      dt_turbine_mean /= 8;
      speed_turbine = 60000000 / dt_turbine_mean / 16; // 16 ticks per rotation
    }
    else {
      speed_turbine = 0;
      rotating_turbine = false;
    }
  }
  interrupts();
  
  currentfloat = 0.2 * CurrentSensor.getCurrent_mA() + 0.8 * currentfloat;
  current = (uint16_t)currentfloat;
  voltagefloat = CurrentSensor.getBusVoltage_V() * 1000.0;
  voltage = (uint16_t)voltagefloat;
  
  noInterrupts();
  if (digitalRead(PIN_FORCE_DATA) == LOW) {
    thrust_force = hx711_read_force();
  }
  anemometer = analogRead(PIN_ANEMOMETER);
  potentiometer = analogRead(PIN_POTENTIOMETER);
  interrupts();
  
  //write data
  Serial.write((byte*)(&speed_fan), 2); // 2bytes
  Serial.write((byte*)(&speed_turbine), 2); // 2bytes
  Serial.write((byte*)(&current), 2); // 2bytes
  Serial.write((byte*)(&voltage), 2); // 2bytes
  Serial.write((byte*)(&thrust_force), 4); // 4bytes
  Serial.write((byte*)(&anemometer), 2); // 2bytes
  Serial.write((byte*)(&potentiometer), 2); // 2bytes
  
  //read data
  while (Serial.available() == 0) {}
  analogWrite(PIN_FAN_PWM, Serial.read());
  while (Serial.available() == 0) {}
  us_servo = Serial.read();
  while (Serial.available() == 0) {}
  us_servo |= (Serial.read() << 8); // 2 byte little endian
  PitchServo.writeMicroseconds(us_servo);
  while (Serial.available() == 0) {}
  *torque_level_pointer = Serial.read();
  while (Serial.available() == 0) {}
  led = Serial.read();

  digitalWrite(PIN_LED, led); 
}

// Interrupts
ISR(TIMER4_COMPA_vect) {
  torque_level_set();
}

void fan_interrupt() {
  if (micros() - time_fan_tick > 20000ul) {
    rot_fan_tick[pos_fan_tick % 2] = micros() - time_fan_tick;
    time_fan_tick = micros();
    pos_fan_tick++;
    rotating_fan = true;
  }
}

void turbine_interrupt() {
  if (micros() - time_turbine_tick > 1000ul) {
    rot_turbine_tick[pos_turbine_tick % 8] = micros() - time_turbine_tick;
    time_turbine_tick = micros();
    pos_turbine_tick++;
    rotating_turbine = true;
  }
}

// Functions
uint32_t hx711_read_force() {
  uint32_t value = 0;
  uint32_t mask = 0x00800000; // 1 at the 24th bit

  while (mask > 0) {
    digitalWrite(PIN_FORCE_CLK, HIGH);
    delayMicroseconds(1);   // T2  >= 0.2 us
    if (digitalRead(PIN_FORCE_DATA) == HIGH)
    {
      value |= mask;
    }
    digitalWrite(PIN_FORCE_CLK, LOW);
    delayMicroseconds(1);   // keep duty cycle ~50%
    mask >>= 1;
  }
  hx711_set_gain();
  return value - thrust_force_offset;
}

void hx711_set_gain() {
  for (int i = 0; i < 3; i++) { // set gain
    digitalWrite(PIN_FORCE_CLK, HIGH);
    delayMicroseconds(1);   // T2  >= 0.2 us
    digitalWrite(PIN_FORCE_CLK, LOW);
    delayMicroseconds(1);   // keep duty cycle ~50%
  }
}

void torque_level_set() {
  // switch off all pins
  digitalWrite(PIN_TORQUE_START, HIGH);
  digitalWrite(PIN_TORQUE_1, LOW);
  digitalWrite(PIN_TORQUE_2, LOW);
  digitalWrite(PIN_TORQUE_3, LOW);
  digitalWrite(PIN_TORQUE_4, LOW);
  digitalWrite(PIN_TORQUE_5, LOW);
  digitalWrite(PIN_TORQUE_6, LOW);

  // switch on turbine start transistor if turbine start
  if (torque_level == 255){  // aka -1
    digitalWrite(PIN_TORQUE_START, LOW);
    return;
  }

  // from 13 software levels to 7 physical levels
  int t_l;
  if (torque_level % 2 == 0){
    t_l = torque_level/2;
  }
  else{
    // toggle between two levels
    t_l = (torque_level+torque_toggle)/2;
    *torque_toggle_pointer *= -1;        
  }

  // set physical torque levels
  if (t_l == 0){
    // leave all switches turned off
  }
  else if (t_l == 1){
    digitalWrite(PIN_TORQUE_1, HIGH);
  }
  else if (t_l == 2){
    digitalWrite(PIN_TORQUE_2, HIGH);
  }  
  else if (t_l == 3){
    digitalWrite(PIN_TORQUE_3, HIGH);
  }
  else if (t_l == 4){
    digitalWrite(PIN_TORQUE_4, HIGH);
  }
  else if (t_l == 5){
    digitalWrite(PIN_TORQUE_5, HIGH);
  }
  else if (t_l == 6){
    digitalWrite(PIN_TORQUE_6, HIGH);
  }
}