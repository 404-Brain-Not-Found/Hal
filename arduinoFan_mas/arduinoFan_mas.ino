#include <VirtualWire.h>
#include <VirtualWire_Config.h>

const int  sender = 1, receive = 0;
const int conPin = 9;
typedef struct conCode{
  int turnOff = 0;
  int turnOn = 1;
  int dim = 2;
  int newMod = 3;
};
struct conCode codes;
typedef struct  masterData{
  int slaveId;
  int fanOn;
  int lightOn;
};
typedef struct slaveRequest{
  int targetId;
};
typedef struct slaveNewData{
  int Id;
  int fanOn;
  int lightOn;
};
typedef struct newSlave{
  int slaveId;
};

void setup() {
  // put your setup code here, to run once:
  vw_setup(2000);
}

void loop() {
  // put your main code here, to run repeatedly:
  switch(dataFromPi()){
    case 1:{ //get update from mods
        senderReceive(sender);
        struct slaveRequest payload;
        payload.targetId = dataFromPi();
        vw_send((uint8_t *) &payload, sizeof(payload));
        vw_wait_tx();
        senderReceive(receive);
        struct masterData newData;
        uint8_t dataSize = sizeof(newData);
        vw_wait_rx();
        if(vw_get_message((uint8_t *) &newData, &dataSize)){
          if(newData.slaveId == payload.targetId) {
            sendDataToPi(newData.fanOn);
            sendDataToPi(newData.lightOn);
          }
        }
      }
      break;
      
    case 2:// add new mod{
        senderReceive(receive);
        vw_wait_rx_max(1000);
        struct slaveRequest newData;
        uint8_t dataSize = sizeof(newData);
        if(vw_have_message()){
          if(vw_get_message((uint8_t *) &newData, &dataSize)){
            if(newData.targetId = 101){
              sendDataToPi(code.newMod);
              struct slaveRequest payload;
              payload.targetId = dataFromPi();
              senderReceive(sender);
              vw_send((uint8_t *) &payload, sizeof(payload));
            }
          }
        }
      }
      break;
    default:
      delay(1);
     break;
  }
  delay(10);
}

int dataFromPi(){
  int bits[6];
  for(int i = 3; 8; i ++){
    pinMode(i, INPUT);
    if(digitalRead(i)) bits[i] = 1;
    else bits[i] = 0;
  }
  pinMode(conPin, OUTPUT);
  digitalWrite(conPin,HIGH);
  return (1 * bits[0] + 2 * bits[1] + 4 * bits[2] + 8 * bits[3] + 16 * bits[4] + 32 * bits[5]);
}

void sendDataToPi(int data){
  for(int i = 3; 8; i ++){
    pinMode(i, OUTPUT);
    digitalWrite(i, bitRead(data, i);
  }
  pinMode(conPin, INPUT);
  while(!digitalRead(conPin);
}

void  senderReceive(int whichOne){
  if(whichOne ==  sender)vw_rx_stop();
  else vw_rx_start();
}
