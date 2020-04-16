#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanSystem.py
Function: crifanLib's python system related functions.
Version: v1.0 20180605
Note:
1. latest version and more can found here:
https://github.com/crifan/crifanLibPython
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "v1.0"
__copyright__ = "Copyright (c) 2019, Crifan Li"
__license__ = "GPL"

import sys
import subprocess
import time

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


def getCommandOutput(consoleCommand, consoleOutputEncoding="utf-8"):
    """
        get command output from terminal
    """
    # print("getCommandOutput: consoleCommand=%s" % consoleCommand)
    isRunCmdOk = False
    consoleOutput = ""
    try:
        # consoleOutputByte = subprocess.check_output(consoleCommand)

        consoleOutputByte = subprocess.check_output(consoleCommand, shell=True)

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
    # logging.info("shellFile=%s, isForceNewInstance=%s, isUseiTerm2=%s", shellFile, isForceNewInstance, isUseiTerm2)

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
    # logging.info("cmdList=%s" % cmdList)

    curProcess = subprocess.Popen(cmdList, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    # logging.info("curProcess=%s" % curProcess)

    returnCode = None
    while True:
        returnCode = curProcess.poll()
        # logging.info("returnCode=%s", returnCode)
        if returnCode is not None:
            # logging.info("subprocess end: returnCode=%s", returnCode)
            break
        time.sleep(0.5)

    # logging.info("Final returnCode=%s", returnCode)
    # logging.info("Complete launch %s and run shell %s", terminalApp, shellFile)

################################################################################
# Test
################################################################################



if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))