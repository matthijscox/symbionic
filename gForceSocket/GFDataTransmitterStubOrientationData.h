#pragma once
#include "GFDataTransmitterStubXxxBase.h"

class GFDataTransmitterStubOrientationData: public GFDataTransmitterStubXxxBase
{
public:
	GFDataTransmitterStubOrientationData(std::string filename, int delay, GFDataTransmitterSocket& transmitterSocket);
	~GFDataTransmitterStubOrientationData();

	void SendData(std::string dataLine);
};

