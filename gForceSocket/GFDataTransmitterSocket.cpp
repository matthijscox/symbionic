#include <WinSock2.h>
#include <iostream>
#include "stdafx.h"
#include "GFDataTransmitterSocket.h"

#define DEFAULT_PORT 12345
#define ORIENTATION_DATA       1
#define GESTURE_DATA           2
#define EXTENDED_DEVICE_DATA   3

GFDataTransmitterSocket::GFDataTransmitterSocket():
	mRunning(false),
	mConnected(false),
	mServerSocket(INVALID_SOCKET),
	mClientSocket(INVALID_SOCKET)
{
}


GFDataTransmitterSocket::~GFDataTransmitterSocket()
{
	Stop();
}

bool GFDataTransmitterSocket::Start()
{
	bool success = true;
	WSADATA wsaData;
	int iResult;
	SOCKADDR_IN serverAddr = { 0 };

	// Initialize Winsock
	iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
	if (iResult != 0) {
		std::cout << "WSAStartup failed with error: " << iResult << std::endl;
		success = false;
	}

	if (success)
	{
		mServerSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

		serverAddr.sin_addr.s_addr = INADDR_ANY;
		serverAddr.sin_family = AF_INET;
		serverAddr.sin_port = htons(DEFAULT_PORT);

		iResult = bind(mServerSocket, (SOCKADDR *)&serverAddr, sizeof(serverAddr));
		if (iResult != 0)
		{
			std::cout << "Bind failed with error:  " << iResult << std::endl;
			success = false;
		}
	}

	if (success)
	{
		iResult = listen(mServerSocket, 1);

		if (iResult != 0)
		{
			std::cout << "Listen failed with error:  " << iResult << std::endl;
			success = false;
		}
	}


	if (success)
	{
		mRunning = true;

		void (GFDataTransmitterSocket::*memfunc)() = &GFDataTransmitterSocket::HandleCommunication;

		mpThread = new std::thread(memfunc, this);

		std::cout << "Listening for incoming socket connections..." << std::endl;
	}
	else
	{
		mRunning = false;
	}

	return success;
}

void GFDataTransmitterSocket::Stop()
{
	mRunning = false;

	closesocket(mServerSocket);

	mpThread->join();
}

void GFDataTransmitterSocket::SendOrientationData(const Quaternion& rotation)
{
	float f;
	QueueEntry* queueEntry = new QueueEntry();

	queueEntry->dataLength = (2 + 4 * sizeof f);
	queueEntry->dataPtr = (char*)malloc(queueEntry->dataLength);

	queueEntry->dataPtr[0] = queueEntry->dataLength;
	queueEntry->dataPtr[1] = ORIENTATION_DATA;

	f = rotation.w();
	memcpy(&queueEntry->dataPtr[2], &f, sizeof f);

	f = rotation.x();
	memcpy(&queueEntry->dataPtr[2+sizeof f], &f, sizeof f);

	f = rotation.y();
	memcpy(&queueEntry->dataPtr[2+2* sizeof f], &f, sizeof f);

	f = rotation.z();
	memcpy(&queueEntry->dataPtr[2+3* sizeof f], &f, sizeof f);

	AddToQueue(queueEntry);
}

void GFDataTransmitterSocket::SendGestureData(Gesture& gest)
{
	QueueEntry* queueEntry = new QueueEntry();

	queueEntry->dataLength = 3;
	queueEntry->dataPtr = (char*)malloc(queueEntry->dataLength);

	queueEntry->dataPtr[0] = queueEntry->dataLength;
	queueEntry->dataPtr[1] = GESTURE_DATA;
	queueEntry->dataPtr[2] = static_cast<char>(gest);

	AddToQueue(queueEntry);
}

void GFDataTransmitterSocket::SendExtendedDeviceData(DeviceDataType dataType, gfsPtr<const std::vector<GF_UINT8>> data)
{
	QueueEntry* queueEntry = new QueueEntry();

	queueEntry->dataLength = (data->size() + 3);
	queueEntry->dataPtr = (char*)malloc(queueEntry->dataLength);

	queueEntry->dataPtr[0] = queueEntry->dataLength;
	queueEntry->dataPtr[1] = EXTENDED_DEVICE_DATA;
	queueEntry->dataPtr[2] = static_cast<int>(dataType);

	for (int i = 0; i < data->size(); i++)
	{
		queueEntry->dataPtr[3 + i] = data->at(i);
	}

	AddToQueue(queueEntry);
}

void GFDataTransmitterSocket::SetConnected(bool connected)
{
	if (connected != mConnected)
	{
		if (connected)
		{
			std::cout << "Socket client connected!" << std::endl;
		}
		else
		{
			if (mConnected)
			{
				std::cout << "Socket client disconnected!" << std::endl;
			}
			std::cout << "Listening for incoming socket connections..." << std::endl;
		}
		mConnected = connected;
	}
}

void GFDataTransmitterSocket::AddToQueue(QueueEntry* queueEntry)
{
	std::lock_guard<std::mutex> lock(mMutex);
	mQueue.push(queueEntry);
}

QueueEntry* GFDataTransmitterSocket::GetNextQueueEntry()
{
	QueueEntry* retEntry = NULL;

	std::lock_guard<std::mutex> lock(mMutex);

	if (!mQueue.empty())
	{
		retEntry = mQueue.front();
		mQueue.pop();
	}

	return retEntry;
}

void GFDataTransmitterSocket::HandleCommunication()
{
	SOCKADDR_IN clientAddr;
	char heartbeat = 0;
	QueueEntry* queueEntry = NULL;

	while (mRunning)
	{
		if (mConnected)
		{
			queueEntry = GetNextQueueEntry();

			if (queueEntry != NULL)
			{
				if (send(mClientSocket, queueEntry->dataPtr, queueEntry->dataLength, 0) != queueEntry->dataLength)
				{
					SetConnected(false);
				}

				free((void*)queueEntry->dataPtr);
				free((void*)queueEntry);
			}
			else
			{
				if (send(mClientSocket, &heartbeat, 1, 0) != 1)
				{
					SetConnected(false);
				}
			}
		}
		else
		{
			int clientAddrSize = sizeof(clientAddr);
			if ((mClientSocket = accept(mServerSocket, (SOCKADDR *)&clientAddr, &clientAddrSize)) != INVALID_SOCKET)
			{
				SetConnected(true);
			}
		}

		Sleep(10);
	}
}
