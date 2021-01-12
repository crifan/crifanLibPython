#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanMultimedia.py
Function: crifanLib's python multimedia (audio) related functions
Version: 20210112
Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/crifanMultimedia.py
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20210112"
__copyright__ = "Copyright (c) 2021, Crifan Li"
__license__ = "GPL"

import os
import io
import re
import base64
import logging

try:
    import audioread
except:
    print("need audioread if use crifanMultimedia audio functions")

################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanMultimedia"

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
# Python Multimedia Function
################################################################################

def detectAudioMetaInfo(audioFullPath):
    """
        detect audio meta info: duration, channels, sampleRate
    """
    isOk = False
    errMsg = ""
    audioMetaInfo = {
        "duration": 0,
        "channels": 0,
        "sampleRate": 0,
    }

    try:
        with audioread.audio_open(audioFullPath) as audioFp:
            audioMetaInfo["duration"] = audioFp.duration
            audioMetaInfo["channels"] = audioFp.channels
            audioMetaInfo["sampleRate"] = audioFp.samplerate

            isOk = True
    except OSError as osErr:
        errMsg = "detect audio info error: %s" % str(osErr)
    except EOFError as eofErr:
        errMsg = "detect audio info error: %s" % str(eofErr)
    except audioread.DecodeError as decodeErr:
        errMsg = "detect audio info error: %s" % str(decodeErr)
    
    if isOk:
        return isOk, audioMetaInfo
    else:
        return isOk, errMsg

################################################################################
# Test
################################################################################


if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))