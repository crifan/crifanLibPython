#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanFlask.py
Function: crifanLib's Flask related functions.
Version: v20181224
Note:
1. latest version and more can found here:
https://github.com/crifan/crifanLibPython
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "v20190107"
__copyright__ = "Copyright (c) 2019, Crifan Li"
__license__ = "GPL"

import io
import re
from flask import send_file

################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanFlask"

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
# Flask Function
################################################################################



def sendFile(fileBytes, contentType, outputFilename, asAttachment=True, range=None):
    """
        flask return downloadable file or file's binary stream data
            example url: http://127.0.0.1:34800/audio/5c1c631c127588257d568eba/3569.mp3
    :param fileBytes:  file binary bytes
    :param contentType: MIME content type, eg: audio/mpeg
    :param outputFilename: output filename, eg: 3569.mp3
    :param asAttachment: True to return downloadable file with filename, False to return binary stream file data
    :param range: range header to support 206=Partial Content, eg: bytes=1146880-
    :return: Flask response
    """
    """Flask API use this to send out file (to browser, browser can directly download file)"""
    # print("sendFile: len(fileBytes)=%s, contentType=%s, outputFilename=%s" % (len(fileBytes), contentType, outputFilename))
    # return send_file(
    #     io.BytesIO(fileBytes),
    #     mimetype=contentType,
    #     as_attachment=asAttachment,
    #     attachment_filename=outputFilename
    # )
    respBytes = fileBytes
    respStatusCode = 200

    totalLen = len(fileBytes)
    respContentLength = totalLen

    contentRange = None
    # support range header of 206=Partial Content to support api caller to continue download or audio drag to play
    if range:
        # responseFile.status_code = 206 # Partial Content
        # bytes=1146880-
        foundBytes = re.search("bytes=(?P<byteStart>\d+)(-(?P<byteEnd>\d+)?)?", range)
        if foundBytes:
            byteStart = foundBytes.group("byteStart")
            # if byteStart:
            byteStart = int(byteStart)
            # for debug
            # if byteStart >= 0:
            if byteStart > 0:
                respStatusCode = 206

            byteEnd = foundBytes.group("byteEnd")
            if byteEnd:
                byteEnd = int(byteEnd)
                if byteEnd > 0:
                    respStatusCode = 206
            else:
                byteEnd = totalLen - 1

            byteEndIdx = byteEnd + 1
            respBytes = fileBytes[byteStart:byteEndIdx]
            respContentLength = len(respBytes)

            # print("byteStart=%d, byteEnd=%d, respContentLength=%s" % (byteStart, byteEnd, respContentLength))
            # Content-Range: bytes 2162688-4010305/4010306
            contentRange = "bytes %d-%d/%d" % (byteStart, byteEnd, totalLen)

    responseFile = send_file(
        # io.BytesIO(fileBytes),
        io.BytesIO(respBytes),
        mimetype=contentType,
        as_attachment=asAttachment,
        attachment_filename=outputFilename,
        # conditional=True # Note: after test conditional is not work well, so implement 206 by myself
    )

    responseFile.headers["Connection"] = "keep-alive"
    # to support audio miniprogram first seek and drag to play
    # if contentType == "audio/mpeg":
    responseFile.headers["Accept-Ranges"] = "bytes"

    # add Content-Length to support miniprogram iOS background play audio works, not error: 10003
    responseFile.headers["Content-Length"] = respContentLength

    # if respStatusCode != 200:
    responseFile.status_code = respStatusCode
    if contentRange:
        responseFile.headers["Content-Range"] = contentRange

    return responseFile


################################################################################
# Test
################################################################################

def testSendFile():
    # inside flask api
    fileBytes = open("some_image.jpg", "rb")
    contentType = "image/jpeg"
    outputFilename = "output_image.jpg"

    fileBytes = open("some_audio.mp3", "rb")
    contentType = "audio/mpeg"
    outputFilename = "output_audio.mp3"

    return sendFile(fileBytes, contentType, outputFilename)


if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))
    # testSendFile()