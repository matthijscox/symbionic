#pragma once
#include "GFDataTransmitterStubXxxBase.h"

class GFDataTransmitterStubExtendedDeviceData : public GFDataTransmitterStubXxxBase
{
public:
	GFDataTransmitterStubExtendedDeviceData(std::string filename, int delay, GFDataTransmitterSocket& transmitterSocket);
	virtual ~GFDataTransmitterStubExtendedDeviceData();

	void SendData(std::string dataLine);

private:
	std::vector<GF_UINT8> myVector;
	gfsPtr<const std::vector<GF_UINT8>> pv;
};

