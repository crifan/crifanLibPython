#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanAndroid.py
Function: crifanLib's Android related functions
Version: 20201218
Latest: https://github.com/crifan/crifanLibPython/blob/master/crifanLib/crifanAndroid.py
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20201218"
__copyright__ = "Copyright (c) 2020, Crifan Li"
__license__ = "GPL"

import re
import logging

from crifanLib.crifanFile import getCommandOutput

################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanAndroid"

################################################################################
# Global Variable
################################################################################

################################################################################
# Internal Function
################################################################################


################################################################################
# Local Function
################################################################################

def getAndroidDeviceList(self, isGetDetail=False):
    """Get android device list

    Args:
        isGetDetail (bool): True to use `adb devices -l`, False to use `adb devices`
    Returns:
        device list(list)
    Raises:
    Examples:
        output: 
            False -> ["2e2a0cb1", "orga4pmzee4ts47t", "192.168.31.84:5555"]
            True -> [{'2e2a0cb1': {'usb': '338952192X', 'product': 'PD2065', 'model': 'V2065A', 'device': 'PD2065', 'transport_id': '4'}}, {'orga4pmzee4ts47t': {'usb': '338886656X', 'product': 'atom', 'model': 'M2004J7AC', 'device': 'atom', 'transport_id': '24'}}, {'192.168.31.84:5555': {'product': 'PD2065', 'model': 'V2065A', 'device': 'PD2065', 'transport_id': '5'}}]
    """
    deviceList = []

    getDevicesCmd = 'adb devices'
    if isGetDetail:
        getDevicesCmd += " -l"
    logging.info("getDevicesCmd=%s", getDevicesCmd)

    isRunCmdOk, cmdOutput = getCommandOutput(getDevicesCmd)
    logging.info("isRunCmdOk=%s, cmdOutput=%s", cmdOutput, cmdOutput)
    if not isRunCmdOk:
        return deviceList

    deviceLines = cmdOutput.splitlines()

    """
    adb devices :
        List of devices attached
        2e2a0cb1	device
        orga4pmzee4ts47t	device
        192.168.31.84:5555	device
    """

    """
    adb devices -l:
        List of devices attached
        2e2a0cb1               device usb:338952192X product:PD2065 model:V2065A device:PD2065 transport_id:4
        orga4pmzee4ts47t       device usb:338886656X product:atom model:M2004J7AC device:atom transport_id:24
        192.168.31.84:5555     device product:PD2065 model:V2065A device:PD2065 transport_id:5
    """

    for eachLine in deviceLines:
        if not eachLine:
            continue

        if "devices attached" in eachLine:
            continue

        foundDevice = re.search("(?P<devSerial>[\w\.\:]+)\s+device\s*(?P<devDetail>[\w\: ]+)", eachLine)
        logging.info("foundDevice=%s", foundDevice)
        # foundDevice=<re.Match object; span=(0, 101), match='2e2a0cb1               device usb:338952192X prod>
        if foundDevice:
            devSerial = foundDevice.group("devSerial")
            logging.info("devSerial=%s", devSerial)
            # devSerial=2e2a0cb1
            if isGetDetail:
                devDetail = foundDevice.group("devDetail")
                logging.info("devDetail=%s", devDetail)
                # devDetail=usb:338952192X product:PD2065 model:V2065A device:PD2065 transport_id:4
                keyValueIter = re.finditer("(?P<key>\w+):(?P<value>\w+)", devDetail) # <callable_iterator object at 0x10baa3a60>
                keyValueMatchList = list(keyValueIter)
                logging.info("keyValueMatchList=%s", keyValueMatchList)
                # keyValueMatchList=[<re.Match object; span=(0, 14), match='usb:338952192X'>, <re.Match object; span=(15, 29), match='product:PD2065'>, <re.Match object; span=(30, 42), match='model:V2065A'>, <re.Match object; span=(43, 56), match='device:PD2065'>, <re.Match object; span=(57, 71), match='transport_id:4'>]
                detailInfoDict = {}
                for eachMatch in keyValueMatchList:
                    eachKey = eachMatch.group("key")
                    eachValue = eachMatch.group("value")
                    detailInfoDict[eachKey] = eachValue
                logging.info("detailInfoDict=%s", detailInfoDict)
                # detailInfoDict={'usb': '338952192X', 'product': 'PD2065', 'model': 'V2065A', 'device': 'PD2065', 'transport_id': '4'}
                curDevDetailDict = {
                    devSerial: detailInfoDict
                }
                logging.info("curDevDetailDict=%s", curDevDetailDict)
                # curDevDetailDict={'2e2a0cb1': {'usb': '338952192X', 'product': 'PD2065', 'model': 'V2065A', 'device': 'PD2065', 'transport_id': '4'}}
                deviceList.append(curDevDetailDict)
            else:
                deviceList.append(devSerial)

    logging.info("deviceList=%s", deviceList)
    # deviceList=[{'2e2a0cb1': {'usb': '338952192X', 'product': 'PD2065', 'model': 'V2065A', 'device': 'PD2065', 'transport_id': '4'}}, {'orga4pmzee4ts47t': {'usb': '338886656X', 'product': 'atom', 'model': 'M2004J7AC', 'device': 'atom', 'transport_id': '24'}}, {'192.168.31.84:5555': {'product': 'PD2065', 'model': 'V2065A', 'device': 'PD2065', 'transport_id': '5'}}]
    return deviceList

def isAndroidUsbConnected(self, deviceSerialId):
    """Check whether android device is currently USB wired connected or not

    Args:
        deviceSerialId (str): android devivce serial id
    Returns:
        connected or not (bool)
    Raises:
    Examples:
        input: "orga4pmzee4ts47t"
        output: True
    """
    isUsbConnected = False
    isRealSerialId = re.search("\w+", deviceSerialId)
    if not isRealSerialId:
        # makesure is not wifi, such as: 192.168.31.84:5555
        logging.error("Invalid android USB wired connected device serial id %s", deviceSerialId)
        return isUsbConnected

    deviceDetailList = self.getAndroidDeviceList(isGetDetail=True)
    for eachDevDetailDict in deviceDetailList:
        curDevSerialStr, curDevDetailDict = list(eachDevDetailDict.items())[0]
        if deviceSerialId == curDevSerialStr:
            detailInfoKeyList = list(curDevDetailDict.keys())
            # ['usb', 'product', 'model', 'device', 'transport_id']
            if "usb" in detailInfoKeyList:
                isUsbConnected = True
            break

    return isUsbConnected

def androidConnectWiFiDevice(self, wifiSerial):
    """Use Android `adb connect` to connect WiFi wireless devive

    Args:
        wifiSerial (str): android devivce WiFi serial, eg: 192.168.31.84:5555
    Returns:
        connect ok or not (bool)
    Raises:
    Examples:
        input: "192.168.31.84:5555"
        output: True
    """
    isConnectOk = False

    adbConnectCmd = "adb connect %s" % wifiSerial
    logging.info("Try connect Android device: %s", adbConnectCmd)
    # os.system(adbConnectCmd) # when failed, will wait too long time: ~ 1 minutes
    isRunOk, cmdOutputStr = getCommandOutput(adbConnectCmd, timeout=1)
    logging.info("isRunOk=%s, console output: %s", isRunOk, cmdOutputStr)
    # connected to 192.168.31.84:5555
    # already connected to 192.168.31.84:5555
    # failed to connect to '192.168.31.84:5555': Operation timed out
    # "failed to connect to '192.168.31.84:5555': Connection refused\n"
    # err=Command 'adb connect 192.168.31.84:5555' timed out after 1 seconds when run cmd=adb connect 192.168.31.84:5555
    if cmdOutputStr:
        if "connected" in cmdOutputStr:
            isConnectOk = True
        elif ("failed" in cmdOutputStr) or ("timed out" in cmdOutputStr):
            isConnectOk = False
    else:
        isConnectOk = False

    return isConnectOk

################################################################################
# Test
################################################################################

if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))
