#include "stdafx.h"
#include "StringUtils.h"
#include "GFDataTransmitterStubOrientationData.h"


GFDataTransmitterStubOrientationData::GFDataTransmitterStubOrientationData(std::string filename, int delay, GFDataTransmitterSocket& transmitterSocket) :
	GFDataTransmitterStubXxxBase(filename, delay, transmitterSocket)
{
}


GFDataTransmitterStubOrientationData::~GFDataTransmitterStubOrientationData()
{
}

void GFDataTransmitterStubOrientationData::SendData(std::string dataLine)
{
	std::vector<std::string> stringParts = StringUtils::split(dataLine, ',');

	if (stringParts.size() == 4)
	{
		float f0 = atof(stringParts[0].c_str());
		float f1 = atof(stringParts[1].c_str());
		float f2 = atof(stringParts[2].c_str());
		float f3 = atof(stringParts[3].c_str());

		Quaternion rotation(f0, f1, f2, f3);
		mTransmitterSocket.SendOrientationData(rotation);
	}
}
