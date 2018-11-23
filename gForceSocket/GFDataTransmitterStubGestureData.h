#pragma once
#include "GFDataTransmitterStubXxxBase.h"

class GFDataTransmitterStubGestureData: public GFDataTransmitterStubXxxBase
{
public:
	GFDataTransmitterStubGestureData(std::string filename, int delay, GFDataTransmitterSocket& transmitterSocket);
	~GFDataTransmitterStubGestureData();

	void SendData(std::string dataLine);
};

