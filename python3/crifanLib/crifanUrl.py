#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanUrl.py
Function: crifanLib's url related functions.
Update: 20210709
Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/crifanUrl.py
"""

import re

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20210709"
__copyright__ = "Copyright (c) 2021, Crifan Li"
__license__ = "GPL"


################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanUrl"

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
# URL Function
################################################################################


################################################################################
# URL
################################################################################


def genFullUrl(mainUrl, paraDict):
    """
    generate the full url, which include the main url plus the parameter list
    Note:
        normally just use urllib.urlencode is OK.
        only use this if you do NOT want urllib.urlencode convert some special chars($,:,{,},...) into %XX
    :param mainUrl:
    :param paraDict:
    :return:
    """
    fullUrl = mainUrl
    fullUrl += '?'
    for i, para in enumerate(paraDict.keys()):
        if(i == 0):
            # first para no '&'
            fullUrl += str(para) + '=' + str(paraDict[para])
        else:
            fullUrl += '&' + str(para) + '=' + str(paraDict[para])
    return fullUrl


def urlIsSimilar(url1, url2):
    """
    check whether two url is similar
        Note: input two url both should be str type
    """
    isSim = False

    url1 = str(url1)
    url2 = str(url2)

    slashList1 = url1.split('/')
    slashList2 = url2.split('/')
    lenS1 = len(slashList1)
    lenS2 = len(slashList2)

    # all should have same structure
    if lenS1 != lenS2:
        # not same sturcture -> must not similar
        isSim = False
    else:
        sufPos1 = url1.rfind('.')
        sufPos2 = url2.rfind('.')
        suf1 = url1[(sufPos1 + 1) : ]
        suf2 = url2[(sufPos2 + 1) : ]
        # at least, suffix should same
        if (suf1 == suf2):
            lastSlashPos1 = url1.rfind('/')
            lastSlashPos2 = url2.rfind('/')
            exceptName1 = url1[:lastSlashPos1]
            exceptName2 = url2[:lastSlashPos2]
            # except name, all other part should same
            if (exceptName1 == exceptName2):
                isSim = True
            else :
                # except name, other part is not same -> not similar
                isSim = False
        else:
            # suffix not same -> must not similar
            isSim = False

    return isSim

def findSimilarUrl(url, urlList):
    """
        found whether the url is similar in urlList
        if found, return True, similarSrcUrl
        if not found, return False, ''
    :param url:
    :param urlList:
    :return:
    """
    (isSimilar, similarSrcUrl) = (False, '')
    for srcUrl in urlList:
        if urlIsSimilar(url, srcUrl):
            isSimilar = True
            similarSrcUrl = srcUrl
            break
    return (isSimilar, similarSrcUrl)


def isIpUrl(curUrl):
    """Check whether url is IP or not

    Args:
        curUrl (str): current url
    Returns:
        bool
    Raises:
    Examples:
        is IP:
            http://127.0.0.1:7912/info/wifi
            http://192.168.31.1/
            http://119.29.29.29/d?dn=wup.imtt.qq.com
            https://111.231.108.161:888/notice/notice?platform=aligames

            http://2408:80f1:31:10::3d:8080/monitor/monitor.jsp?t=1625540141127
        not IP:
            http://37.com.cn/useragreement/shell/xxx
    """
    isIpV4 = re.match('https?://\d+\.\d+\.\d+\.\d+', curUrl)
    isIpV6 = re.match("https?://[\da-z]+:[\da-z]+:[\da-z]+:[\da-z]+::[\da-z]+", curUrl, re.I)
    isIp = isIpV4 or isIpV6
    return isIp

################################################################################
# Test
################################################################################



if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))