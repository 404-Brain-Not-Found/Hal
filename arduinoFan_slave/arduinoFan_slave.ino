#include <VirtualWire.h>
#include <VirtualWire_Config.h>
#include <EEPROM.h>
#include <OneWire.h> 
#include <DallasTemperature.h>
int ID_ADDRESS = 0;
int ID;
const int FIRST_ONE_WIRE_BUS_PIN = 7;
const int SECOND_ONE_WIRE_BUS_PIN = 8;
OneWire firstOneWireBus(FIRST_ONE_WIRE_BUS_PIN);
OneWire secondOneWireBus(SECOND_ONE_WIRE_BUS_PIN);
DallasTemperature bus1(&firstOneWireBus);
DallasTemperature bus2(&secondOneWireBus);
DeviceAddress outsideTemp = {};
DeviceAddress insideTemp = {};
int PIR_PIN = 5;
int HALL_EFFECT_PIN = 2;
float temps[2];
bool emptyRoom = false;
// both
const int  sender = 1, receive = 0;
const int TX_POWER_PIN = 6, RX_POWER_PIN = 7;
typedef struct  masterData{
  int slaveId;
  int fanOn;
};
typedef struct slaveRequest{
  int targetId;
};
typedef struct slaveNewData{
  int Id;
  int fanOn;
  int onLight;
};
typedef struct newSlave{
  int slaveId;
};

void setup() {
  // put your setup code here, to run once:
  pinMode(PIR_PIN, INPUT);
  digitalWrite(PIR_PIN, HIGH);
  pinMode(HALL_EFFECT_PIN, INPUT);
  digitalWrite(HALL_EFFECT_PIN, HIGH);
  attachInterrupt(digitalPinToInterrupt(HALL_EFFECT_PIN), checkMotion, CHANGE);
  vw_setup(2000);
  discoverOneWireDevices();
  bus1.begin();
  bus2.begin();
  ID = EEPROM.read(ID_ADDRESS);
  if (ID == NAN){
    senderReceive(receive);
    while(!vw_have_message()) delay(1);
    senderReceive( sender);
    struct newSlave payload;
    payload.slaveId = 101;
    
    vw_send((uint8_t *) &payload, sizeof(payload));
    vw_wait_tx();
    
    senderReceive(receive);
    struct newSlave newData;
    uint8_t dataSize = sizeof(newData);
    vw_wait_rx();
    vw_get_message((uint8_t *) &newData, &dataSize);
    ID = newData.slaveId;
    EEPROM.write(ID_ADDRESS, ID);
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  senderReceive(receive);
  if(vw_have_message()){
    struct slaveRequest newData;
    uint8_t dataSize = sizeof(newData);
    vw_wait_rx();
    vw_get_message((uint8_t *) &newData, &dataSize);
    if(newData.targetId == ID){
       senderReceive( sender);
      struct slaveNewData payload;
      payload.Id = ID;
      int onOof;
      int lightOn;
      if(tempControl() && !emptyRoom) onOof = 1;
      else onOof = 0;
      if(!emptyRoom) lightOn = 1;
      else lightOn = 0;
      payload.fanOn = onOof;
      payload.onLight = lightOn;
      vw_send((uint8_t *) &payload, sizeof(payload));
      vw_wait_tx();
    }
  }
}

void discoverOneWireDevices() {
  byte i;
  byte addr[8];
  while(firstOneWireBus.search(addr)) for( i = 0; i < 8; i++) insideTemp[i] = addr[i];
  firstOneWireBus.reset_search();
  while(secondOneWireBus.search(addr)) for( i = 0; i < 8; i++) outsideTemp[i] = addr[i];
  secondOneWireBus.reset_search();
}

void checkMotion(){
  int pirVal = digitalRead(PIR_PIN);
  if(pirVal == HIGH) emptyRoom = true;
  else emptyRoom = false;
}

void  senderReceive(int whichOne){
  if(whichOne ==  sender)vw_rx_stop();
  else vw_rx_start();
}

bool tempControl(){
  bus1.requestTemperatures();  
  bus2.requestTemperatures();
  if(bus1.getTempC(insideTemp) > bus2.getTempC(outsideTemp)) return true;
  else return false;
}
