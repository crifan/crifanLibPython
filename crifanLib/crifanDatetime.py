#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanDatetime.py
Function: crifanLib's datetime related functions.
Version: 20200918
Note:
1. latest version and more can found here:
https://github.com/crifan/crifanLibPython/blob/master/crifanLib/crifanDatetime.py
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20200918"
__copyright__ = "Copyright (c) 2020, Crifan Li"
__license__ = "GPL"


from datetime import datetime,timedelta
from datetime import time  as datetimeTime
import time

################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanDatetime"

################################################################################
# Global Variable
################################################################################
gVal = {
    'calTimeKeyDict': {}
}

gConst = {
}

################################################################################
# Internal Function
################################################################################


################################################################################
# Datetime Function
################################################################################


def convertLocalToGmt(localTime):
    """
        convert local GMT8 to GMT time
        Note: input should be 'datetime' type, not 'time' type
    :param localTime:
    :return:
    """
    return localTime - timedelta(hours=8)

def datetimeToTimestamp(datetimeVal, withMilliseconds=False) :
    """
        convert datetime value to timestamp
        eg:
            "2006-06-01 00:00:00.123" -> 1149091200
            if with milliseconds -> 1149091200123
    :param datetimeVal:
    :return:
    """
    timetupleValue = datetimeVal.timetuple()
    timestampFloat = time.mktime(timetupleValue) # 1531468736.0 -> 10 digits
    timestamp10DigitInt = int(timestampFloat) # 1531468736
    timestampInt = timestamp10DigitInt

    if withMilliseconds:
        microsecondInt = datetimeVal.microsecond # 817762
        microsecondFloat = float(microsecondInt)/float(1000000) # 0.817762
        timestampFloat = timestampFloat + microsecondFloat # 1531468736.817762
        timestampFloat = timestampFloat * 1000 # 1531468736817.7621 -> 13 digits
        timestamp13DigitInt = int(timestampFloat) # 1531468736817
        timestampInt = timestamp13DigitInt

    return timestampInt

def getCurTimestamp(withMilliseconds=False):
    """
    get current time's timestamp
        (default)not milliseconds -> 10 digits: 1351670162
        with milliseconds -> 13 digits: 1531464292921
    """
    curDatetime = datetime.now()
    return datetimeToTimestamp(curDatetime, withMilliseconds)

def datetimeToStr(inputDatetime, format="%Y%m%d_%H%M%S"):
    """Convert datetime to string

    Args:
        inputDatetime (datetime): datetime value
    Returns:
        str
    Raises:
    Examples:
        datetime.datetime(2020, 4, 21, 15, 44, 13, 2000) -> '20200421_154413'
    """
    datetimeStr = inputDatetime.strftime(format=format)
    # print("inputDatetime=%s -> datetimeStr=%s" % (inputDatetime, datetimeStr)) # 2020-04-21 15:08:59.787623
    return datetimeStr

def getCurDatetimeStr(outputFormat="%Y%m%d_%H%M%S"):
    """
    get current datetime then format to string

    eg:
        20171111_220722

    :param outputFormat: datetime output format
    :return: current datetime formatted string
    """
    curDatetime = datetime.now() # 2017-11-11 22:07:22.705101
    # curDatetimeStr = curDatetime.strftime(format=outputFormat) #'20171111_220722'
    curDatetimeStr = datetimeToStr(curDatetime, format=outputFormat)
    return curDatetimeStr

def timestampToDatetime(timestamp, isMillisecond=False):
    """Convert timestamp to datetime value

    Args:
        timestamp (float/int): int for timestamp value without millisecond, float for timestamp with millisecond
        isMillisecond (bool): True for 13 digit with millisecond, False for 10 digit without millisecond
    Returns:
        datetime
    Raises:
    Examples:
        1587454927964 -> datetime.datetime(2020, 4, 21, 15, 42, 7, 964000)
        1587455053.002 -> datetime.datetime(2020, 4, 21, 15, 44, 13, 2000)
    """
    timestampFloat = float(timestamp)
    if isMillisecond:
        timestampFloat = timestampFloat / 1000
    convertedDatetime = datetime.fromtimestamp(timestampFloat)
    return convertedDatetime

def timestampToDatetimeStr(timestamp, isMillisecond=False, format="%Y%m%d_%H%M%S"):
    """Convert timestamp to datetime string

    Args:
        timestamp (int): timestamp int value with/without millisecond
        isMillisecond (bool): True for 13 digit with millisecond, False for 10 digit without millisecond
        format (str): datetime format
    Returns:
        str
    Raises:
    Examples:
        1587454927964 -> 2020-4-21 15:42:07
    """
    convertedDatetime = timestampToDatetime(timestamp, isMillisecond=isMillisecond)
    datetimeStr = datetimeToStr(convertedDatetime, format=format)
    return datetimeStr


def calcTimeStart(uniqueKey):
    """init for calculate elapsed time"""
    global gVal

    gVal['calTimeKeyDict'][uniqueKey] = time.time()
    return


def calcTimeEnd(uniqueKey):
    """
        to get elapsed time
        Note: before call this, should use calcTimeStart to init
    :param uniqueKey:
    :return:
    """
    global gVal

    return time.time() - gVal['calTimeKeyDict'][uniqueKey]


def floatSecondsToDatetimeTime(floatSeconds):
    """
        convert float seconds(time delta) to datetime.time

        example: 27.83879017829895 -> datetime.time(0, 0, 27, 838790)

        Note: the max hour can NOT excedd 24 hors, otherwise will error: ValueError: hour must be in 0..23
    """
    secondsInt = int(floatSeconds)
    decimalsFloat = floatSeconds - secondsInt
    millisecondsFloat = decimalsFloat * 1000
    millisecondsInt = int(millisecondsFloat)
    microsecondsDecimal = millisecondsFloat - millisecondsInt
    microsecondsInt = int(microsecondsDecimal * 1000)

    minutes, seconds = divmod(secondsInt, 60)
    hours, minutes = divmod(minutes, 60)

    # datetimeTimeValue = datetime.time(
    datetimeTimeValue = datetimeTime(
        hour        =hours,
        minute      =minutes,
        second      =seconds,
        microsecond =(millisecondsInt * 1000) + microsecondsInt
    )

    return datetimeTimeValue


def floatSecondsToDatetimeDict(floatSeconds):
    """
        convert float seconds(time delta) to datetime dict{days, hours, minutes, seconds, millseconds, microseconds}

        example: 96400.3765293 -> {'days': 1, 'hours': 2, 'minutes': 46, 'seconds': 40, 'millseconds': 376, 'microseconds': 529}
    """
    secondsInt = int(floatSeconds)
    decimalsFloat = floatSeconds - secondsInt
    millisecondsFloat = decimalsFloat * 1000
    millisecondsInt = int(millisecondsFloat)
    microsecondsDecimal = millisecondsFloat - millisecondsInt
    microsecondsInt = int(microsecondsDecimal * 1000)

    minutes, seconds = divmod(secondsInt, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    convertedDict = {
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "millseconds": millisecondsInt,
        "microseconds": microsecondsInt,
    }

    return convertedDict


def datetimeDictToStr(datetimeDict, seperatorD=" ", seperatorHms=":", seperatorMilliS="."):
    formattedStr = "%d%s%02d%s%02d%s%02d%s%03d" % (
        datetimeDict["days"], seperatorD,
        datetimeDict["hours"], seperatorHms,
        datetimeDict["minutes"], seperatorHms,
        datetimeDict["seconds"], seperatorMilliS,
        datetimeDict["millseconds"])
    return formattedStr

################################################################################
# Test
################################################################################

def testTimestamp():
    # test timestamp with milliseconds
    timestampNoMilliSec = getCurTimestamp()
    print("timestampNoMilliSec=%s" % timestampNoMilliSec) # 1531468833
    timestampWithMilliSec = getCurTimestamp(withMilliseconds=True)
    print("timestampWithMilliSec=%s" % timestampWithMilliSec) # 1531468833344

if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))

    # testTimestamp()
