#include "Receiver.h"
#include "Transmitter.h"
#include "WiFi.h"

unsigned int _mode;  //0 receivead // 1 transmit 

void setup()
{
  WiFi.mode(WIFI_OFF);
  //  btStop();
  Serial.begin(115200);
  delay (100);
  Serial.println("Setup...");
  pinMode( 25, OUTPUT );
  Receiver::Instance().Setup();
  Transmitter::Instance().Setup();
}
void loop()
{
  Receiver::Instance().Loop();
  Transmitter::Instance().Loop();
}
