#include "Receiver.h"

Receiver::Receiver() {}

void Receiver::Setup()
{
  pinMode(LHDataPin, INPUT);
  pinMode(HLDataPin, INPUT);
  BeginReceive();
}


void Receiver::BeginReceive() {
  //  Serial.println("BeginReceive...");
  previous = 0;
  msgStatus = 0;
  msgSizeL = 0;
  msgSizeH = 0;
  attachInterrupt(digitalPinToInterrupt(LHDataPin), InterruptLowToHigh, RISING);
  attachInterrupt(digitalPinToInterrupt(HLDataPin), InterruptHighToLow, FALLING);
}

void Receiver::EndReceive(unsigned int newMsgStatus) {
  msgStatus = newMsgStatus;

  detachInterrupt(digitalPinToInterrupt(LHDataPin));
  detachInterrupt(digitalPinToInterrupt(HLDataPin));
}


void Receiver::BeginNewSignal(unsigned long mCurrent)
{
  msgSizeL = 0;
  msgSizeH = 0;
  msgStatus = 1;
  msgBegin = mCurrent;
  AddBufferL(maxSignal);
  //  AddBufferH((unsigned int) (mCurrent - previous));
}


void Receiver::InterruptLowToHigh()
{
  Receiver& receiver( Receiver::Instance() );
  unsigned long mCurrent = micros();
  unsigned long previous = receiver.GetPrevious();
  bool longMsg = (mCurrent - previous) > receiver.GetMaxSignal();
  switch (receiver.GetMsgStatus())
  {
    case 2:
      break;
    case 1:
      if (longMsg) // закончилось сообщение
      {
        if (receiver.ItsTooSmall()) {
          receiver.BeginNewSignal(mCurrent);
          break;
        } else {
          receiver.AddBufferL(0);
          receiver.EndReceive(2);
          break;
        }
      }
      else { // сообщение продолжается
        receiver.AddBufferL((unsigned int) (mCurrent - previous));
      }
      break;
    case 0:
      if (longMsg && previous) {// начинаем новое
        receiver.BeginNewSignal(mCurrent);
      }
      break;
  }
  receiver.SetPrevious(mCurrent);
}


void Receiver::InterruptHighToLow()
{
  Receiver& receiver( Receiver::Instance() );
  unsigned long mCurrent = micros();
  unsigned long previous = receiver.GetPrevious();
  switch (receiver.GetMsgStatus())
  {
    case 1:
      receiver.AddBufferH((unsigned int) (mCurrent - previous));
      break;

  }
  receiver.SetPrevious(mCurrent);
}

void Receiver::PrintBuffer() {
  int i = 0;
  //String mOut = String(msgStatus);
  String mOut = "";
  for (i; i < msgSizeH; i++) {
    mOut += "L";
    mOut += String(bufferL[i]);
    mOut += ";H";
    mOut += String(bufferH[i]);
    mOut += ";";
  }
  Serial.println(mOut);
}


void Receiver::Loop()
{
  switch ( msgStatus )
  {
    case 1:
      if ((micros() - msgBegin) > 100000 || msgSizeH > 127 ) {// сообщение затянулось
        EndReceive(4);
      }
      break;
    case 2:
      PrintBuffer();
      BeginReceive();
      break;
    case 3:
      break;
    case 4:
      PrintBuffer();
      BeginReceive();
      break;

  }
}
