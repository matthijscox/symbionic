#pragma once
#include <thread>
#include <mutex>
#include <queue>
#include <iostream>
#include "gforce.h"

using namespace gf;

typedef struct QueueEntry
{
	char* dataPtr;
	int dataLength;
};

class GFDataTransmitterSocket
{
public:
	GFDataTransmitterSocket();
	~GFDataTransmitterSocket();

	bool Start();
	void Stop();

	void SendOrientationData(const Quaternion& rotation);
	void SendGestureData(Gesture& gest);
	void SendExtendedDeviceData(DeviceDataType dataType, gfsPtr<const std::vector<GF_UINT8>> data);

private:
	void HandleCommunication();
	void SetConnected(bool connected);
	void AddToQueue(QueueEntry* queueEntry);
	QueueEntry* GetNextQueueEntry();

private:
	bool mRunning;
	bool mConnected;
	std::queue<QueueEntry*> mQueue;
	std::thread* mpThread;
	std::mutex mMutex;
	SOCKET mServerSocket;
	SOCKET mClientSocket;
};

