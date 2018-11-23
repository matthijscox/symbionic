#include "stdafx.h"
#include "gforce.h"
#include <atomic>
#include <fstream>
#include "StringUtils.h"
#include "GFDataTransmitterStub.h"
#include "GFDataTransmitterSocket.h"
#include "GFDataTransmitterStubOrientationData.h"
#include "GFDataTransmitterStubGestureData.h"
#include "GFDataTransmitterStubExtendedDeviceData.h"

using namespace gf;
using namespace std;

GFDataTransmitterStub::GFDataTransmitterStub()
{
}

GFDataTransmitterStub::~GFDataTransmitterStub()
{
}

int GFDataTransmitterStub::Run(_TCHAR* settingsFile, std::atomic<bool>& exiting)
{
	int ret = 0;

	wstring ws(settingsFile);
	string fileName(ws.begin(), ws.end());

	GFDataTransmitterSocket transmitterSocket;

	if (transmitterSocket.Start() != true)
	{
		cout << "Unable to start data transmitter socket" << endl;
		ret = 1;
	}
	else
	{
		std::vector<GFDataTransmitterStubXxxBase*> transmitters = LoadTransmitters(fileName, transmitterSocket);

		for (int i=0;i<transmitters.size();i++)
		{
			transmitters.at(i)->Start();
		}

		do
		{
			Sleep(100);
		}
		while (!exiting);

		for (int i = 0; i < transmitters.size(); i++)
		{
			transmitters.at(i)->Stop();
		}

		transmitterSocket.Stop();
	}


	return ret;
}

std::vector<GFDataTransmitterStubXxxBase*> GFDataTransmitterStub::LoadTransmitters(const std::string& settingsFile, GFDataTransmitterSocket& transmitterSocket)
{
	std::vector<GFDataTransmitterStubXxxBase*> output;

	std::ifstream infile(settingsFile);

	if (!infile.good())
	{
		cout << "ERROR: Unable to read file '" << settingsFile << "'" << endl;
	}
	else
	{
		cout << "Reading settings file '" << settingsFile << "'" << endl;

		std::string line;
		while (std::getline(infile, line))
		{
			std::vector<std::string> stringParts = StringUtils::split(line, ',');
			if (stringParts.size() != 3)
			{
				cout << "ERROR: Ignoring incorrectly formatted line '" << line << "' in file '" << settingsFile << "'" << endl;
			}
			else
			{
				std::string dataType = stringParts[0];
				std::string filename = stringParts[1];
				int delay = atoi(stringParts[2].c_str());

				if (dataType.compare("OrientationData") == 0)
				{
					cout << "OrientationData" << endl;
					output.push_back(new GFDataTransmitterStubOrientationData(filename, delay, transmitterSocket));
				}
				else if (dataType.compare("GestureData") == 0)
				{
					cout << "GestureData" << endl;
					output.push_back(new GFDataTransmitterStubGestureData(filename, delay, transmitterSocket));
				}
				else if (dataType.compare("ExtendedDeviceData") == 0)
				{
					cout << "ExtendedDeviceData" << endl;
					output.push_back(new GFDataTransmitterStubExtendedDeviceData(filename, delay, transmitterSocket));
				}
				else
				{
					cout << "ERROR: Ignoring unknown data type '" << dataType << "'" << endl;
				}
			}
		}
		infile.close();
	}

	return output;
}
