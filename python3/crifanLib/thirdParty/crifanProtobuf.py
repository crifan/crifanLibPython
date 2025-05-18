#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanProtobuf.py
Function: crifanLib's Protobuf(Protocol Buffer) related functions.
Version: 20250428
Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/thirdParty/crifanProtobuf.py
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20250428"
__copyright__ = "Copyright (c) 2025, Crifan Li"
__license__ = "GPL"

import os
import tempfile

from crifanLib.crifanFile import loadTextFromFile, loadBytesFromFile

################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanProtobuf"

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
# Protobuf Function
################################################################################

def decodeProtobuf_bytes(protobufBytes):
    """
    Decode protobuf bytes to json string
    """
    protoInputFile = tempfile.NamedTemporaryFile()
    protoInputFileName = protoInputFile.name
    protoOutputFile = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8")
    protoOutputFileName = protoOutputFile.name

    # saveBytesToFile(protobufBytes, protoInputFile)
    protoInputFile.write(protobufBytes)

    # cmd = f"/opt/homebrew/bin/protoc --decode_raw < ./{protoInputFileName} > {protoOutputFileName}"
    cmd = f"protoc --decode_raw < {protoInputFileName} > {protoOutputFileName}"
    os.system(cmd)

    protoParseResult = loadTextFromFile(protoOutputFileName)

    protoInputFile.close()
    protoOutputFile.close()

    return protoParseResult

def decodeProtobuf_hexStr(protobufBytesHexStr):
    """
    Decode protobuf bytes from hex string to json string
    """
    protobufBytes = bytes.fromhex(protobufBytesHexStr)
    return decodeProtobuf_bytes(protobufBytes)

def decodeProtobuf_file(protobufFilePath):
    """
    Decode protobuf bytes from binary file to json string
    """
    protobufBytes = loadBytesFromFile(protobufFilePath)
    return decodeProtobuf_bytes(protobufBytes)

################################################################################
# Test
################################################################################

if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))
