#include "Arduino.h"

class Transmitter
{
  public:
    static Transmitter& Instance() { static Transmitter instance; return instance; };
    void Setup();
    void Loop();

  private:
    Transmitter();
    Transmitter( const Transmitter& );

    void ReadSerial();
    void SendSignal();
    static const int TRANSMITTER_PIN = 25;
    static const int BUFFER_SIZE = 255;
    unsigned long mBuffer[ BUFFER_SIZE ];
    byte mItWrite;
    byte mItRead;
    bool currentLevel;
    unsigned long mMicrosWait;
    String nBuffer;
    byte startIndex;
    byte endIndex;
};
