#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanRequests.py
Function: crifanLib's Requests related functions
Version: 20201212
Latest: https://github.com/crifan/crifanLibPython/blob/master/crifanLib/crifanRequests.py
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20201211"
__copyright__ = "Copyright (c) 2020, Crifan Li"
__license__ = "GPL"

import os
import time
import requests

from crifanLib.crifanFile import formatSize
from crifanLib.crifanDatetime import floatSecondsToDatetimeDict, datetimeDictToStr

################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanRequests"

################################################################################
# Global Variable
################################################################################

################################################################################
# Internal Function
################################################################################

def get302RealUrl(originUrl):
    """get real url address after 302 move

    Args:
        originUrl (str): original url
    Returns:
        real url(str)
    Raises:
    Examples:
        input: 'http://dl.gamecenter.vivo.com.cn/clientRequest/gameDownload?id=57587&pkgName=com.jiuzun.mxsg.vivo&sourword=%E4%B8%89%E5%9B%BD&page_index=4&dlpos=1&channel=h5'
        output: 'https://gameapktxdl.vivo.com.cn/appstore/developer/soft/20180206/201802061851104837232.apk'
    """
    realUrl = ""
    resp = requests.get(originUrl, allow_redirects=False)
    if resp.status_code == 302:
        realUrl = resp.headers['Location']
    return realUrl


def streamingDownloadFile(
        url,
        fileToSave=None,
        proxies=None,
        isShowSpeed=True,
        chunkSize=1024*512,
        resumeSize=0,
        totalSize=0,
    ):
    """Download file using stream mode, support showing process with current speed, percent, size

    Args:
        url (str): file online url
        fileToSave (str): filename or full file path
        proxies (dict): requests proxies
        isShowSpeed (bool): show downloading speed or not
        chunkSize (int): when showing download speed, need use stream downloading, need set chunck size
        resumeSize (bool): the size to start download, normally is the local already downloaded size
        totalSize (int): total file size, only used for calculate downloaded percent
    Returns:
        download ok or not (bool)
    Raises:
    Examples:
    """
    isDownloadOk = False

    if isShowSpeed:
        if totalSize == 0:
            gotTotalSize = getFileSizeFromUrl(url, proxies) # 154551625
            if gotTotalSize:
                totalSize = gotTotalSize

    headers = {
        'Range': 'bytes=%d-' % resumeSize,
        # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36",
    }
    resp = requests.get(url, proxies=proxies, headers=headers, stream=True)
    curDownloadedSize = 0
    with open(fileToSave, "ab") as f:
        startTime = time.time()
        prevTime = startTime
        for curChunkBytes in resp.iter_content(chunk_size=chunkSize):
            if curChunkBytes:
                curTime = time.time() # 1606456020.0718982
                f.write(curChunkBytes)
                f.flush()

                curChunkSize = len(curChunkBytes) # 524288
                curDownloadedSize += curChunkSize # 524288
                totalDownloadedSize = curDownloadedSize + resumeSize # 12058624
                totalDownloadedSizeStr = formatSize(totalDownloadedSize) # '11.5MB'

                curDownloadTime = curTime - prevTime # 15.63818907737732
                curSpeed = curChunkSize / curDownloadTime # 670522.651191692
                curSpeedStr = formatSize(curSpeed) # '231.3KB'

                totalDownloadTime = curTime - startTime # 15.63818907737732
                averageSpeed = curDownloadedSize / totalDownloadTime # 670522.651191692
                averageSpeedStr = formatSize(averageSpeed) # '231.3KB'

                totalDownloadTimeDict = floatSecondsToDatetimeDict(totalDownloadTime)
                totalDownloadTimeStr = datetimeDictToStr(totalDownloadTimeDict, isShowMilliSecPart=False)

                if isShowSpeed:
                    showStr = "downloading speed: cur=%s/s, avg=%s/s, time: total=%s, size: %s" % (curSpeedStr, averageSpeedStr, totalDownloadTimeStr, totalDownloadedSizeStr)

                    if totalSize > 0:
                        downloadedPercent100 = round(100 * totalDownloadedSize / totalSize, 2) # 47.23
                        downloadedPercent100Str = str(downloadedPercent100) # '47.23'
                        percentStr = ", percent: %s%%" % downloadedPercent100Str # ', percent: 47.23%'
                    else:
                        percentStr = ""

                    showStr += percentStr
                    # 'downloading speed: cur=231.3KB/s, avg=231.3KB/s, time: total=00:00:02, size: 11.5MB, percent: 49.38%'
                    print(showStr)

                prevTime = curTime

    return isDownloadOk

def downloadFile(url,
        fileToSave=None,
        proxies=None,
        isStreamMode=True,
        isResume=True,
    ):
    """Download file from url then save to file

    Args:
        url (str): file online url
        fileToSave (str): filename or full file path
        proxies (dict): requests proxies
        isStreamMode (bool): use stream mode or not
    Returns:
        download ok or not (bool)
    Raises:
    Examples:
        input: 
            'https://book.crifan.com/books/5g_message_rcs_tech_summary/pdf/5g_message_rcs_tech_summary.pdf'
            'downloaded/pdf/5g_message_rcs_tech_summary.pdf'
        output:
            True
    """
    isDownloadOk = False

    if not fileToSave:
        urlPartList = url.split("/")
        fileToSave = urlPartList[-1] # 5g_message_rcs_tech_summary.pdf

    try:
        if isStreamMode:
            totalFileSize = getFileSizeFromUrl(url, proxies) # 154551625
            if not totalFileSize:
                print("Failed to get total file size from %s" % url)
                return isDownloadOk
            
            totalSizeStr = formatSize(totalFileSize)
            print("Get total file size %s from %s" % (totalSizeStr, url))

            isDownloadedAndValid = isFileExistAndValid(fileToSave, fullFileSize=totalFileSize)
            if isDownloadedAndValid:
                print("%s is already download" % fileToSave)
                isDownloadOk = True
                return isDownloadOk

            curDownloadedSize = 0
            isExistFile = os.path.isfile(fileToSave)
            if isExistFile:
                curDownloadedSize = os.path.getsize(fileToSave)
                curDownloadedSizeStr = formatSize(curDownloadedSize)
                print("Already downloaded %s for %s" % (curDownloadedSizeStr, fileToSave))

                if curDownloadedSize > totalFileSize:
                    # possible is local is new version, so consider as downloaded
                    print("Downloaded=%s > online=%s, consider as downloaded" % (curDownloadedSizeStr, totalSizeStr))
                    isDownloadOk = True
                    return isDownloadOk

            if not isResume:
                curDownloadedSize = 0

            isDownloadOk = streamingDownloadFile(
                url,
                fileToSave=fileToSave,
                proxies=proxies,
                isShowSpeed=True,
                resumeSize=curDownloadedSize,
                totalSize=totalFileSize,
            )
        else:
            resp = requests.get(url, proxies=proxies)
            with open(fileToSave, 'wb') as saveFp:
                saveFp.write(resp.content)
                isDownloadOk = True
    except BaseException as curException:
        print("Exception %s when download %s to %s" % (curException, url, fileToSave))

    return isDownloadOk

def getFileSizeFromUrl(fileUrl, proxies=None):
    """Get file size from file url

    Args:
        fileUrl (str): file url
        proxies (dict): requests proxies
    Returns:
        file size or 0 mean fail to get
    Raises:
    Examples:
        input: https://gameapktxdl.vivo.com.cn/appstore/developer/soft/20201020/202010201805243ed5v.apk
        output: 154551625
    """
    totalFileSize = None

    try:
        resp = requests.get(fileUrl, stream=True, proxies=proxies)
        respHeaders = resp.headers
        # {'Date': 'Thu, 10 Dec 2020 05:27:10 GMT', 'Content-Type': 'application/vnd.android.package-archive', 'Content-Length': '154551625', 'Connection': 'keep-alive', 'Server': 'NWS_TCloud_static_msoc1_xz', 'Cache-Control': 'max-age=600', 'Expires': 'Thu, 10 Dec 2020 05:37:09 GMT', 'Last-Modified': 'Thu, 09 Jan 2020 11:21:35 GMT', 'X-NWS-UUID-VERIFY': '94db2d14f135898d924fb249b13a0964', 'X-Verify-Code': '2871bd7acf67c7e298e9c8d8c865e27d', 'X-NWS-LOG-UUID': 'a83536f2-ab83-465d-ba09-0e19a15cc706', 'X-Cache-Lookup': 'Hit From Disktank3, Hit From Inner Cluster', 'Accept-Ranges': 'bytes', 'ETag': '"46C50A5CADB6BEE339236477BB6DDC14"', 'X-Daa-Tunnel': 'hop_count=2'}
        # {'Server': 'Tengine', 'Date': 'Fri, 11 Dec 2020 14:11:00 GMT', 'Content-Type': 'application/pdf', 'Content-Length': '24422168', 'Last-Modified': 'Fri, 18 Sep 2020 09:56:15 GMT', 'Connection': 'keep-alive', 'ETag': '"5f64843f-174a718"', 'Strict-Transport-Security': 'max-age=15768000', 'Accept-Ranges': 'bytes'}
        contentLengthStr = respHeaders['Content-Length'] # '154551625', '24422168'
        contentLengthInt = int(contentLengthStr) # 154551625, 24422168
        totalFileSize = contentLengthInt
    except:
        totalFileSize = None

    return totalFileSize # 154551625

def isFileExistAndValid(filePath, fullFileSize=None):
    """Check file exist and valid or not


    Args:
        filePath (str): file path
        fullFileSize (int): full file size
    Returns:
        existed and valid (bool)
    Raises:
    Examples:
    """
    isExistFile = os.path.isfile(filePath)
    isValidFile = False
    if isExistFile:
        curFileSize = os.path.getsize(filePath) # 260900226
        if fullFileSize:
            isValidFile = curFileSize == fullFileSize
        else:
            isValidFile = curFileSize > 0
    isExistAndValid = isExistFile and isValidFile
    return isExistAndValid

################################################################################
# Test
################################################################################

if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))