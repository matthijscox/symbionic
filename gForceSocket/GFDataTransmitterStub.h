#pragma once
#include "GFDataTransmitterSocket.h"
#include "GFDataTransmitterStubXxxBase.h"

class GFDataTransmitterStub
{
public:
	GFDataTransmitterStub();
	~GFDataTransmitterStub();

	int Run(_TCHAR* settingsFile, std::atomic<bool>& exiting);

private:
	std::vector<GFDataTransmitterStubXxxBase*> LoadTransmitters(const std::string& settingsFile, GFDataTransmitterSocket& transmitterSocket);

private:
	GFDataTransmitterSocket mDataTransmitter;
};

