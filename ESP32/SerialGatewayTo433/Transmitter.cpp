#include "Transmitter.h"
#include "Receiver.h"

Transmitter::Transmitter():
  mItRead( mItWrite )
{
}
void  Transmitter::Setup() {
  mItWrite = 0;
  mItRead = 0;
  pinMode( TRANSMITTER_PIN, OUTPUT );

}

void Transmitter::ReadSerial()
{

  while ( Serial.available() > 0 )
  {
    char c( Serial.read() );
    switch ( c )
    {
      case 'B': // begin message
        Receiver::Instance().EndReceive(3);
        Serial.println("ReadBegin");
        //        startIndex = mItRead;
        endIndex = mItRead;
        break;
      case 'E':
        Serial.println("ReadEnd");
        mMicrosWait = 0;
        mItWrite = endIndex;
        break;
      case 'L':
      case 'H':
        nBuffer = "";
        break;
      case ';':
        mBuffer[ endIndex ] = nBuffer.toInt();
        nBuffer = "";
        endIndex++;
        break;
      case '0':
      case '1':
      case '2':
      case '3':
      case '4':
      case '5':
      case '6':
      case '7':
      case '8':
      case '9':
        nBuffer += c;
        break;
    }
  }

}

void Transmitter::SendSignal()
{
  unsigned long micros_current( micros() );
  if ( micros_current >= mMicrosWait )
  {
    if (mMicrosWait == 0) {
      currentLevel = false;
    } else {
      currentLevel = currentLevel ? false : true;
      mItRead++;
    }
    digitalWrite( TRANSMITTER_PIN, currentLevel );
    mMicrosWait = micros_current + mBuffer[ mItRead ];
  }
  if ( mItRead != mItWrite )
  {
    return;
  }
  else
  {
    digitalWrite( TRANSMITTER_PIN, 0 );
    Serial.println("Sent");
    Receiver::Instance().BeginReceive();
  }
}

void Transmitter::Loop()
{

  if ( mItWrite != mItRead )  // передаем
  {
    SendSignal();
  }
  else  // все передано
  {
    ReadSerial();
  }
}
