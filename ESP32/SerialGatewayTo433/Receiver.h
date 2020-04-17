#include "Arduino.h"
#include <FunctionalInterrupt.h>

class Receiver
{
  public:
    static Receiver& Instance() {
      static Receiver instance;
      return instance;
    };
    void Setup();
    void Loop();
    void BeginReceive();
    void EndReceive(unsigned int newMsgStatus);

    unsigned long GetPrevious() { return previous; }
    unsigned long SetPrevious(unsigned long newValue) { previous = newValue; }
    unsigned long GetMaxSignal() { return maxSignal; }
    unsigned long GetMsgStatus() { return msgStatus; }
    unsigned long ItsTooSmall() { return msgSizeH < 5 ? true : false; }  // коротки сообщения игнорируем
    void AddBufferH(unsigned int value) { bufferH[msgSizeH++] = value; }    
    void AddBufferL(unsigned int value) { bufferL[msgSizeL++] = value; }    

  private:
    Receiver();
    Receiver( const Receiver& );
    static void InterruptLowToHigh();
    static void InterruptHighToLow();
    void BeginNewSignal(unsigned long mCurrent);
    void PrintBuffer();

    unsigned int bufferH[ 128 ];
    unsigned int bufferL[ 128 ];
    unsigned int msgSizeH;
    unsigned int msgSizeL;
    unsigned int msgStatus;
    unsigned long previous;
    unsigned long msgBegin;
    static const int maxSignal = 8000;
    static const int LHDataPin = 32;
    static const int HLDataPin = 33;
};
