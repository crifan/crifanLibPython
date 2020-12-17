#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanSystem.py
Function: crifanLib's python system related functions.
Version: 20201217
Latest: https://github.com/crifan/crifanLibPython/blob/master/crifanLib/crifanSystem.py
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20201217"
__copyright__ = "Copyright (c) 2020, Crifan Li"
__license__ = "GPL"

import os
import sys
import subprocess
import time
import re

################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanSystem"

################################################################################
# Global Variable
################################################################################
gVal = {
}

gConst = {
}

################################################################################
# Internal Function
################################################################################


################################################################################
# Python System Function
################################################################################


def isPython2():
    """check whether is python 2"""
    return sys.version_info[0] == 2

def isPython3():
    """check whether is python 3"""
    return sys.version_info[0] == 3


def runCommand(consoleCommand):
    """run command using subprocess call"""
    isRunCmdOk = False
    errMsg = "Unknown Error"

    try:
        resultCode = subprocess.check_call(consoleCommand, shell=True)
        if resultCode == 0:
            isRunCmdOk = True
            errMsg = ""
        else:
            isRunCmdOk = False
            errMsg = "%s return code %s" % (consoleCommand, resultCode)
    except subprocess.CalledProcessError as callProcessErr:
        isRunCmdOk = False
        errMsg = str(callProcessErr)
        # "Command 'ffmpeg -y -i /Users/crifan/.../debug/extractAudio/show_112233_video.mp4 -ss 00:00:05.359 -to 00:00:06.763 -b:a 128k /.../show_112233_video_000005359_000006763.mp3 2> /dev/null' returned non-zero exit status 1."

    return isRunCmdOk, errMsg


def getCommandOutput(consoleCommand, consoleOutputEncoding="utf-8", timeout=2):
    """get command output from terminal

    Args:
        consoleCommand (str): console/terminal command string
        consoleOutputEncoding (str): console output encoding, default is utf-8
        timeout (int): wait max timeout for run console command
    Returns:
        console output (str)
    Raises:
    """
    # print("getCommandOutput: consoleCommand=%s" % consoleCommand)
    isRunCmdOk = False
    consoleOutput = ""
    try:
        # consoleOutputByte = subprocess.check_output(consoleCommand)

        consoleOutputByte = subprocess.check_output(consoleCommand, shell=True, timeout=timeout)

        # commandPartList = consoleCommand.split(" ")
        # print("commandPartList=%s" % commandPartList)
        # consoleOutputByte = subprocess.check_output(commandPartList)
        # print("type(consoleOutputByte)=%s" % type(consoleOutputByte)) # <class 'bytes'>
        # print("consoleOutputByte=%s" % consoleOutputByte) # b'640x360\n'

        consoleOutput = consoleOutputByte.decode(consoleOutputEncoding) # '640x360\n'
        consoleOutput = consoleOutput.strip() # '640x360'
        isRunCmdOk = True
    except subprocess.CalledProcessError as callProcessErr:
        cmdErrStr = str(callProcessErr)
        print("Error %s for run command %s" % (cmdErrStr, consoleCommand))

    # print("isRunCmdOk=%s, consoleOutput=%s" % (isRunCmdOk, consoleOutput))
    return isRunCmdOk, consoleOutput


def launchTerminalRunShellCommand(shellFile, isForceNewInstance=True, isUseiTerm2=False):
    """in Mac, Launch terminal(Mac Terminal / iTerm2) and execute shell file, which contain command to run

    Args:
        shellFile (str): shell file full path
        isUseiTerm2 (bool): True to use iTerm2, False to use Mac builtin Terminal
        isForceNewInstance (bool): whether pase -n to open, which means: Open a new instance of the application even if one is already running
    Returns:
    Raises:
    """
    # logging.debug("shellFile=%s, isForceNewInstance=%s, isUseiTerm2=%s", shellFile, isForceNewInstance, isUseiTerm2)

    TerminalApp_iTerm2 = '/Applications/iTerm.app'
    TerminalApp_Terminal = 'Terminal'
    if isUseiTerm2:
        terminalApp = TerminalApp_iTerm2
    else:
        terminalApp = TerminalApp_Terminal

    cmdList = [
        "/usr/bin/open",
    ]

    if isForceNewInstance:
        cmdList.append("-n")

    extarArgs = shellFile
    restCmdList = [
        "-a",
        terminalApp,
        '--args',
        extarArgs,
    ]
    cmdList.extend(restCmdList)
    # logging.debug("cmdList=%s" % cmdList)

    curProcess = subprocess.Popen(cmdList, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    # logging.debug("curProcess=%s" % curProcess)

    returnCode = None
    while True:
        returnCode = curProcess.poll()
        # logging.debug("returnCode=%s", returnCode)
        if returnCode is not None:
            # logging.debug("subprocess end: returnCode=%s", returnCode)
            break
        time.sleep(0.5)

    # logging.debug("Final returnCode=%s", returnCode)
    # logging.debug("Complete launch %s and run shell %s", terminalApp, shellFile)

def killProcess(pid):
    """Kill process by pid

    Args:
        pid (id): process ID
    Returns:
    Raises:
    """
    isKillOk, errCode = False, 0
    pidInt = int(pid)
    killCmd = "kill -9 %s" % pidInt
    returnCode = os.system(killCmd)
    # logging.debug("Command: %s -> returnCode=%s", killCmd, returnCode)
    RETURN_CODE_OK = 0
    if returnCode == RETURN_CODE_OK:
        isKillOk = True
    else:
        errCode = returnCode
    return isKillOk, errCode

def grepProcessStatus(processFile, singleLinePattern, psCmd="ps aux"):
    """grep process info status from ps output

    Args:
        processFile (str): process file name
        singleLinePattern (str): single process line search pattern
        psCmd (str): ps command, default: ps aux
    Returns:
    Raises:
    Examples:
        input: "crawlerStart.py", "^\s*(?P<username>\w+)\s+(?P<pid>\d+)\s+.+?python\s+crawlerStart\.py\s+-task\s+(?P<taskFile>\S+)\s+-id\s+(?P<curDevId>\d+)$"
        output: [{'username': 'limao', 'pid': '64320', 'taskFile': '/Users/limao/dev/xxx/crawler/appAutoCrawler/AppCrawler/task/191115_card_DongKaKongJian/191115_card_DongKaKongJian_wexin.txt', 'curDevId': '1'}]
    """
    # logging.debug("processFile=%s, singleLinePattern=%s", processFile, singleLinePattern)
    isCheckCmdRunOk, isRunning, processInfoList = False, False, []

    groupNameList = re.findall("\(\?P<(\w+)>", singleLinePattern)
    # logging.debug("groupNameList=%s", groupNameList)
    # groupNameList=['username', 'pid', 'port', 'scriptFile', 'devId']
    grepProcessCmd = "%s | grep %s" % (psCmd, processFile)
    # logging.debug("grepProcessCmd=%s", grepProcessCmd)
    isCheckCmdRunOk, cmdResult = getCommandOutput(grepProcessCmd)
    # logging.debug("isCheckCmdRunOk=%s, cmdResult=%s", isCheckCmdRunOk, cmdResult)
    if isCheckCmdRunOk:
        # lineSeparator = "\n"
        lineSeparator = os.linesep
        resultList = cmdResult.split(lineSeparator)
        # logging.debug("resultList=%s", resultList)
        # limao            56562   0.0  0.0  4267948    664 s006  R+    5:53下午   0:00.00 grep mitmdump
        # limao            56560   0.0  0.0  4268636   1112 s006  S+    5:53下午   0:00.00 /bin/sh -c ps aux | grep mitmdump
        # limao            55396   0.0  0.1  4381268  11568 s011  S+    5:19下午   0:05.04 /Users/limao/.pyenv/versions/3.8.0/Python.framework/Versions/3.8/Resources/Python.app/Contents/MacOS/Python /Users/limao/.pyenv/versions/3.8.0/bin/mitmdump -p 8081 -s middleware/Save1.py
        if resultList:
            for eachLine in resultList:
                # logging.debug("eachLine=%s", eachLine)
                foundProcess = re.search(singleLinePattern, eachLine)
                # logging.debug("foundProcess=%s", foundProcess)
                if foundProcess:
                    curProcessInfoDict = {}
                    for eachKey in groupNameList:
                        curValue = foundProcess.group(eachKey)
                        curProcessInfoDict[eachKey] = curValue
                    # logging.debug("curProcessInfoDict=%s", curProcessInfoDict)
                    processInfoList.append(curProcessInfoDict)

    isRunning = bool(processInfoList)
    # logging.debug("isRunning=%s, processInfoList=%s", isRunning, processInfoList)
    return isCheckCmdRunOk, isRunning, processInfoList

################################################################################
# Test
################################################################################



if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))