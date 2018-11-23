#pragma once
#include "stdafx.h"
#include <vector>

class StringUtils
{
public:
	static std::vector<std::string> split(const std::string& s, char seperator);
};

