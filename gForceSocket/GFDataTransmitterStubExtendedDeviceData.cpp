#include "stdafx.h"
#include "GFDataTransmitterStubExtendedDeviceData.h"
#include "StringUtils.h"

GFDataTransmitterStubExtendedDeviceData::GFDataTransmitterStubExtendedDeviceData(std::string filename, int delay, GFDataTransmitterSocket& transmitterSocket) :
	GFDataTransmitterStubXxxBase(filename, delay, transmitterSocket),
	pv(&myVector)
{
}


GFDataTransmitterStubExtendedDeviceData::~GFDataTransmitterStubExtendedDeviceData()
{
}

void GFDataTransmitterStubExtendedDeviceData::SendData(std::string dataLine)
{
	myVector.clear();

	std::vector<std::string> stringParts = StringUtils::split(dataLine, ',');

	for (int i = 1; i < stringParts.size(); i++)
	{
		myVector.push_back(atoi(stringParts[i].c_str()));
	}

	mTransmitterSocket.SendExtendedDeviceData((DeviceDataType)(atoi(stringParts[0].c_str())), pv);
}
