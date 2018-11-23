#include "stdafx.h"
#include "GFDataTransmitterStubGestureData.h"


GFDataTransmitterStubGestureData::GFDataTransmitterStubGestureData(std::string filename, int delay, GFDataTransmitterSocket& transmitterSocket):
	GFDataTransmitterStubXxxBase(filename, delay, transmitterSocket)
{
}


GFDataTransmitterStubGestureData::~GFDataTransmitterStubGestureData()
{
}

void GFDataTransmitterStubGestureData::SendData(std::string dataLine)
{
	Gesture gest = (Gesture)atoi(dataLine.c_str());

	mTransmitterSocket.SendGestureData(gest);
}
