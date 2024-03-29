#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanRequests.py
Function: crifanLib's Requests related functions
Version: 20210903
Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/thirdParty/crifanRequests.py
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20210903"
__copyright__ = "Copyright (c) 2021, Crifan Li"
__license__ = "GPL"

import os
import time
import re
import logging
import requests

try:
    from bs4 import BeautifulSoup
except:
    print("! import bs4 failed, please install: `pip install bs4`")

from crifanLib.crifanHtml import extractHtmlTitle

from crifanLib.crifanString import toPureStr
from crifanLib.crifanFile import formatSize, isFileExistAndValid
from crifanLib.crifanDatetime import floatSecondsToDatetimeDict, datetimeDictToStr
from crifanLib.crifanHtml import extractHtmlTitle

################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanRequests"

UserAgent_Mac = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"

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

        input: 'https://appdlc-drcn.hispace.hicloud.com/dl/appdl/application/apk/db/dbd3fbf4bb7c4e199e27169b83054afd/com.zsbf.rxsc.2010151906.rpk?sign=f9001091ej1001042000000000000100000000000500100101010@21BD93C47A224B178DE4FCDEAC296E3F&extendStr=detail%3A1%3B&tabStatKey=A09000&relatedAppId=C100450321&hcrId=21BD93C47A224B178DE4FCDEAC296E3F&maple=0&distOpEntity=HWSW'
        output: 'https://appdl-1-drcn.dbankcdn.com/dl/appdl/application/apk/db/dbd3fbf4bb7c4e199e27169b83054afd/com.zsbf.rxsc.2010151906.rpk?sign=f9001091ej1001042000000000000100000000000500100101010@21BD93C47A224B178DE4FCDEAC296E3F&extendStr=detail%3A1%3B&tabStatKey=A09000&relatedAppId=C100450321&hcrId=21BD93C47A224B178DE4FCDEAC296E3F&maple=0&distOpEntity=HWSW'
    """
    realUrl = ""
    resp = requests.get(originUrl, allow_redirects=False)

    if resp.status_code == 302:
        realUrl = resp.headers['Location']

    return realUrl

def getRespHeadersFromUrl(curUrl, proxies=None):
    """Get response headers from url

    Args:
        curUrl (str): current url
        proxies (dict): requests proxies
    Returns:
        headers(dict) or None
    Raises:
    Examples:
        1
            input: https://gameapktxdl.vivo.com.cn/appstore/developer/soft/20201020/202010201805243ed5v.apk
            output: {'Date': 'Thu, 10 Dec 2020 05:27:10 GMT', 'Content-Type': 'application/vnd.android.package-archive', 'Content-Length': '154551625', 'Connection': 'keep-alive', 'Server': 'NWS_TCloud_static_msoc1_xz', 'Cache-Control': 'max-age=600', 'Expires': 'Thu, 10 Dec 2020 05:37:09 GMT', 'Last-Modified': 'Thu, 09 Jan 2020 11:21:35 GMT', 'X-NWS-UUID-VERIFY': '94db2d14f135898d924fb249b13a0964', 'X-Verify-Code': '2871bd7acf67c7e298e9c8d8c865e27d', 'X-NWS-LOG-UUID': 'a83536f2-ab83-465d-ba09-0e19a15cc706', 'X-Cache-Lookup': 'Hit From Disktank3, Hit From Inner Cluster', 'Accept-Ranges': 'bytes', 'ETag': '"46C50A5CADB6BEE339236477BB6DDC14"', 'X-Daa-Tunnel': 'hop_count=2'}
        2
            output: {'Server': 'Tengine', 'Date': 'Fri, 11 Dec 2020 14:11:00 GMT', 'Content-Type': 'application/pdf', 'Content-Length': '24422168', 'Last-Modified': 'Fri, 18 Sep 2020 09:56:15 GMT', 'Connection': 'keep-alive', 'ETag': '"5f64843f-174a718"', 'Strict-Transport-Security': 'max-age=15768000', 'Accept-Ranges': 'bytes'}
        3
            output: {'Date': 'Thu, 24 Dec 2020 08:57:18 GMT', 'Content-Type': 'application/vnd.android.package-archive', 'Content-Length': '190814345', 'Connection': 'keep-alive', 'Server': 'openresty', 'Last-Modified': 'Mon, 14 Dec 2020 12:32:50 GMT', 'Expires': 'Mon, 14 Dec 2020 12:32:50 GMT', 'Content-Disposition': 'attachment; filename="com.tanwan.yscqlyzf.huawei.2012141704.apk"', 'Via': 'CHN-JSsuqian-CT3-CACHE7[8],CHN-JSsuqian-CT3-CACHE3[0,TCP_HIT,6],CHN-JSwuxi-GLOBAL2-CACHE63[5],CHN-JSwuxi-GLOBAL2-CACHE74[0,TCP_HIT,2],CHN-SH-GLOBAL1-CACHE92[589],CHN-SH-GLOBAL1-CACHE152[555,TCP_MISS,588],CHN-HElangfang-GLOBAL2-CACHE41[493],CHN-HElangfang-GLOBAL2-CACHE24[487,TCP_MISS,491]', 'X-Hcs-Proxy-Type': '1', 'X-Ccdn-Cachettl': '31536000', 'X-Ccdn-Expires': '30684021', 'Nginx-Hit': '1', 'Cache-Control': 'max-age=7200', 'Age': '851993', 'Lct-Pos-Percent': '0.19', 'Lct-Hot-Series': '1056964608', 'Accept-Ranges': 'bytes', 'dl-from': 'hwcdn'}
        4
            {'Server': 'Tengine', 'Date': 'Thu, 25 Mar 2021 14:44:42 GMT', 'Content-Type': 'image/jpeg', 'Content-Length': '49130', 'Last-Modified': 'Thu, 25 Mar 2021 14:08:56 GMT', 'Connection': 'keep-alive', 'ETag': '"605c9978-bfea"', 'Expires': 'Sat, 24 Apr 2021 14:44:42 GMT', 'Cache-Control': 'max-age=2592000', 'Strict-Transport-Security': 'max-age=15768000', 'Accept-Ranges': 'bytes'}
    """
    respHeaderDict = None

    try:
        resp = requests.get(curUrl, stream=True, proxies=proxies)
        respHeaderDict = resp.headers
        # {'Date': 'Thu, 10 Dec 2020 05:27:10 GMT', 'Content-Type': 'application/vnd.android.package-archive', 'Content-Length': '154551625', 'Connection': 'keep-alive', 'Server': 'NWS_TCloud_static_msoc1_xz', 'Cache-Control': 'max-age=600', 'Expires': 'Thu, 10 Dec 2020 05:37:09 GMT', 'Last-Modified': 'Thu, 09 Jan 2020 11:21:35 GMT', 'X-NWS-UUID-VERIFY': '94db2d14f135898d924fb249b13a0964', 'X-Verify-Code': '2871bd7acf67c7e298e9c8d8c865e27d', 'X-NWS-LOG-UUID': 'a83536f2-ab83-465d-ba09-0e19a15cc706', 'X-Cache-Lookup': 'Hit From Disktank3, Hit From Inner Cluster', 'Accept-Ranges': 'bytes', 'ETag': '"46C50A5CADB6BEE339236477BB6DDC14"', 'X-Daa-Tunnel': 'hop_count=2'}
        # {'Server': 'Tengine', 'Date': 'Fri, 11 Dec 2020 14:11:00 GMT', 'Content-Type': 'application/pdf', 'Content-Length': '24422168', 'Last-Modified': 'Fri, 18 Sep 2020 09:56:15 GMT', 'Connection': 'keep-alive', 'ETag': '"5f64843f-174a718"', 'Strict-Transport-Security': 'max-age=15768000', 'Accept-Ranges': 'bytes'}
        # {'Date': 'Thu, 24 Dec 2020 09:19:58 GMT', 'Content-Type': 'application/vnd.android.package-archive', 'Content-Length': '190814345', 'Connection': 'keep-alive', 'Server': 'openresty', 'Age': '859494', 'Cache-Control': 'max-age=7200', 'Content-Disposition': 'attachment; filename="com.tanwan.yscqlyzf.huawei.2012141704.apk"', 'Expires': 'Mon, 14 Dec 2020 12:32:50 GMT', 'Last-Modified': 'Mon, 14 Dec 2020 12:32:50 GMT', 'Lct-Hot-Series': '12582912', 'Lct-Pos-Percent': '0.25', 'Nginx-Hit': '1', 'Via': 'CHN-JSwuxi-AREACT1-CACHE33[4],CHN-JSwuxi-AREACT1-CACHE43[0,TCP_HIT,2],CHN-JSwuxi-GLOBAL2-CACHE110[2],CHN-JSwuxi-GLOBAL2-CACHE74[0,TCP_HIT,0],CHN-SH-GLOBAL1-CACHE92[589],CHN-SH-GLOBAL1-CACHE152[555,TCP_MISS,588],CHN-HElangfang-GLOBAL2-CACHE41[493],CHN-HElangfang-GLOBAL2-CACHE24[487,TCP_MISS,491]', 'X-Ccdn-Cachettl': '31536000', 'X-Ccdn-Expires': '30676539', 'X-Hcs-Proxy-Type': '1', 'Accept-Ranges': 'bytes', 'dl-from': 'hwcdn'}
        # {'Date': 'Thu, 24 Dec 2020 09:22:05 GMT', 'Content-Type': 'application/octet-stream', 'Content-Length': '249455788', 'Connection': 'keep-alive', 'Accept-Ranges': 'bytes', 'ETag': '"2a0205efc29db9ee555d8cd429a5d723"', 'Last-Modified': 'Tue, 22 Dec 2020 13:38:42 GMT', 'Ohc-Cache-HIT': 'czix102 [2]', 'Ohc-File-Size': '249455788', 'Ohc-Upstream-Trace': '58.216.2.102', 'Timing-Allow-Origin': '*', 'dl-from': 'bdcdn', 'x-obs-id-2': '32AAAQAAEAABAAAQAAEAABAAAQAAEAABCSteDob3rAnYCgC3AxdwUWM4S8xxD0WH', 'x-obs-request-id': '000001768AAD97CB980AA58ADE5C652D', 'Age': '122819', 'Via': 'HIT by 61.183.53.37, HIT by 180.97.190.116', 'Server': 'Tengine/2.2.3'}
    except:
        respHeaderDict = None

    return respHeaderDict

def getFileSizeFromHeaders(respHeaderDict):
    """Get file size from url response headers

    Args:
        respHeaderDict (dict): requests response headers
    Returns:
        file size or 0 mean fail to get
    Raises:
    Examples:
        input: {'Date': 'Fri, 25 Dec 2020 01:18:18 GMT', 'Content-Type': 'application/octet-stream', 'Content-Length': '190814345', 'Connection': 'keep-alive', 'Server': 'openresty', 'Age': '915891', 'Last-Modified': 'Mon, 14 Dec 2020 10:32:43 GMT', 'Lct-Hot-Series': '1006632960', 'Lct-Pos-Percent': '0.12', 'Nginx-Hit': '1', 'Via': 'CHN-JSsuqian-CUCC2-CACHE3[21],CHN-JSsuqian-CUCC2-CACHE3[0,TCP_HIT,10],CHN-HElangfang-GLOBAL2-CACHE49[18],CHN-HElangfang-GLOBAL2-CACHE24[0,TCP_HIT,18]', 'X-Ccdn-Cachettl': '31536000', 'X-Ccdn-Expires': '30620162', 'X-Hcs-Proxy-Type': '1', 'X-Obs-Id-2': '32AAAQAAEAABAAAQAAEAABAAAQAAEAABCSiVxBzkAhQ9rf3Mu0HzMB2FV2QN61NS', 'X-Obs-Request-Id': '0000017660D50FAF940B2445365906B1', 'Accept-Ranges': 'bytes', 'dl-from': 'hwcdn'}
        output: 190814345
    """
    totalFileSize = None

    if respHeaderDict:
        contentLengthStr = respHeaderDict['Content-Length'] # '154551625', '24422168', '190814345'
        contentLengthInt = int(contentLengthStr) # 154551625, 24422168, 190814345
        totalFileSize = contentLengthInt

    return totalFileSize

def getFileSizeFromUrl(fileUrl, proxies=None):
    """Get file size from file url

    Args:
        fileUrl (str): file url
        proxies (dict): requests proxies
    Returns:
        file size（int) or None
    Raises:
    Examples:
        input: https://gameapktxdl.vivo.com.cn/appstore/developer/soft/20201020/202010201805243ed5v.apk
        output: 154551625
    """
    respHeaderDict = getRespHeadersFromUrl(fileUrl, proxies=proxies)
    totalFileSize = getFileSizeFromHeaders(respHeaderDict)
    return totalFileSize # 154551625

def getContentTypeFromHeaders(respHeaderDict):
    """Get content type from url response headers

    Args:
        respHeaderDict (dict): requests response headers
    Returns:
        content type(str) or None
    Raises:
    Examples:
        input: {'Date': 'Thu, 10 Dec 2020 05:27:10 GMT', 'Content-Type': 'application/vnd.android.package-archive', 'Content-Length': '154551625', 'Connection': 'keep-alive', 'Server': 'NWS_TCloud_static_msoc1_xz', 'Cache-Control': 'max-age=600', 'Expires': 'Thu, 10 Dec 2020 05:37:09 GMT', 'Last-Modified': 'Thu, 09 Jan 2020 11:21:35 GMT', 'X-NWS-UUID-VERIFY': '94db2d14f135898d924fb249b13a0964', 'X-Verify-Code': '2871bd7acf67c7e298e9c8d8c865e27d', 'X-NWS-LOG-UUID': 'a83536f2-ab83-465d-ba09-0e19a15cc706', 'X-Cache-Lookup': 'Hit From Disktank3, Hit From Inner Cluster', 'Accept-Ranges': 'bytes', 'ETag': '"46C50A5CADB6BEE339236477BB6DDC14"', 'X-Daa-Tunnel': 'hop_count=2'}
        output: 'application/vnd.android.package-archive'

        input: {'Date': 'Fri, 25 Dec 2020 01:47:31 GMT', 'Content-Type': 'text/html; charset=UTF-8', 'Transfer-Encoding': 'chunked', 'Connection': 'keep-alive', 'Cache-Control': 'no-cache', 'Content-Language': 'en-US', 'Expires': 'Thu, 01 Dec 1994 16:00:00 GMT', 'Set-Cookie': 'JSESSIONID=aaaIXrniUxnxU8Rh-8fzx; path=/', 'Content-Encoding': 'gzip'}
        output: 'text/html; charset=UTF-8'
    """
    contentTypeStr = None

    if respHeaderDict:
        if 'Content-Type' in respHeaderDict:
            contentTypeStr = respHeaderDict['Content-Type']
        else:
            contentTypeStr = None
            # http://s.shouji.qihucdn.com/210112/0c24ebd2f1132df071f5db7301c723e6/com.szs.qh360_1.apk?en=curpage%3D%26exp%3D1611816296%26from%3Dopenbox_Iservice_AppDetail%26m2%3D%26ts%3D1611211496%26tok%3D3960c113b5eb6c09508b2ad674e5757b%26v%3D%26f%3Dz.apk
            # -> 
            # {'Server': 'nginx', 'Date': 'Fri, 29 Jan 2021 09:01:18 GMT', 'Content-Length': '0', 'Connection': 'close'}
        # 'Content-Type': 'application/vnd.android.package-archive'
        # 'Content-Type': 'application/pdf'

    # 'application/vnd.android.package-archive'
    # 'application/pdf'
    return contentTypeStr

def getContentTypeFromUrl(curUrl, proxies=None):
    """Get content type from url

    Args:
        curUrl (str): current url
        proxies (dict): requests proxies
    Returns:
        content type(str) or None
    Raises:
    Examples:
        input: https://gameapktxdl.vivo.com.cn/appstore/developer/soft/20201020/202010201805243ed5v.apk
        output: 'application/vnd.android.package-archive'

        output: 'application/pdf'
    """
    respHeaderDict = getRespHeadersFromUrl(curUrl, proxies=proxies)
    contentTypeStr = getContentTypeFromHeaders(respHeaderDict)
    return contentTypeStr

def isValidImageUrl(imageUrl, proxies=None):
    """Check whether is valid image url

    Args:
        imageUrl (str): image url
        proxies (dict): requests proxies
    Returns:
        bool
    Raises:
    Examples:
        https://www.crifan.com/files/pic/uploads/2021/03/f60ea32cf4664b41922431f4ea015621.jpg
    """
    isValid = False
    contentType = getContentTypeFromUrl(imageUrl, proxies=proxies) # 'image/jpeg'
    isImageType = re.match("^image/", contentType)
    isValid = bool(isImageType)
    return isValid

def isAndroidApkUrl(curApkUrl, proxies=None):
    """Check whether is android apk url

    Args:
        curApkUrl (str): current apk url
        proxies (dict): requests proxies
    Returns:
        (bool, int/str)
            True, apk file size
            False, error message
    Raises:
    Examples:
        input: https://gameapktxdl.vivo.com.cn/appstore/developer/soft/20201020/202010201805243ed5v.apk
        output: True, 154551625

        input: 'https://appdlc-drcn.hispace.hicloud.com/dl/appdl/application/apk/47/4795a70deeac4103a8e6182b257ec4a9/com.shenghe.wzcq.huawei.2012221953.apk?sign=f9001091ej1001032000000000000100000000000500100101010@CC0A6D3E117D430483B55B08162FB0F4&extendStr=detail%3A1%3B&tabStatKey=A09000&relatedAppId=C100005003&hcrId=CC0A6D3E117D430483B55B08162FB0F4&maple=0&distOpEntity=HWSW'
        output: True, 249455788

        input: http://appstore.vivo.com.cn/appinfo/downloadApkFile?id=1676650&app_version=100.0
        output: True, 164494719

        input: https://appdlc-drcn.hispace.hicloud.com/dl/appdl/application/apk/db/dbd3fbf4bb7c4e199e27169b83054afd/com.zsbf.rxsc.2010151906.rpk?sign=f9001091ej1001042000000000000100000000000500100101010@21BD93C47A224B178DE4FCDEAC296E3F&extendStr=detail%3A1%3B&tabStatKey=A09000&relatedAppId=C100450321&hcrId=21BD93C47A224B178DE4FCDEAC296E3F&maple=0&distOpEntity=HWSW
        output: False, 'Content Type is octet-stream but no .apk in url https://appdlc-drcn.hispace.hicloud.com/dl/appdl/application/apk/db/dbd3fbf4bb7c4e199e27169b83054afd/com.zsbf.rxsc.2010151906.rpk?sign=f9001091ej1001042000000000000100000000000500100101010@21BD93C47A224B178DE4FCDEAC296E3F&extendStr=detail%3A1%3B&tabStatKey=A09000&relatedAppId=C100450321&hcrId=21BD93C47A224B178DE4FCDEAC296E3F&maple=0&distOpEntity=HWSW'

        case application/zip:
        input: https://api-game.meizu.com/games/public/download/redirect/url?auth_time=43200&package_name=com.popcap.pvz2cthdamz&source=0&timestamp=1611106470321&type=2&sign=e53a406706f7f7074469fd1816ce7209&fname=com.popcap.pvz2cthdamz_1040
        output: True, 409527195

        case octet-stream, but url contain download:
        input: https://api-game.meizu.com/games/public/download/redirect/url?auth_time=43200&package_name=com.hirealgame.hswsw.mz&source=0&timestamp=1611106503304&type=2&sign=fce0aeff829a8b4c4f493f2e86c9e35b&fname=com.hirealgame.hswsw.mz_402
        output: True, 131942209
    """
    isAllValid = False
    errMsg = "Unknown"
    apkFileSize = 0

    isValidApkUrl = False
    respHeaderDict = getRespHeadersFromUrl(curApkUrl, proxies=proxies)

    contentTypeStr = getContentTypeFromHeaders(respHeaderDict)
    if contentTypeStr:
        # contentTypeStr = contentTypeStr.lower()

        # ContentType_Android = 'application/vnd.android.package-archive'
        # isAndroidType = contentTypeStr == ContentType_Android
        # isValidApkUrl = "android" in contentTypeStr
        foundApplicationAndroid = re.search("application/.*android", contentTypeStr, re.I)

        # 'application/zip'
        foundApplicationZip = re.search("application/zip", contentTypeStr, re.I)

        isAndroidType = foundApplicationAndroid or foundApplicationZip

        if isAndroidType:
            isValidApkUrl = True
            errMsg = ""
        else:
            errMsg = "Content type %s is NOT android for url %s" % (contentTypeStr, curApkUrl)
            # 'Content type text/html; charset=UTF-8 is NOT android for url http://app.mi.com/details?id=com.cqzzdlq.mi'

        # continue to check other possibility
        if not isValidApkUrl:
            # "Content-Type": "application/octet-stream",
            isOctetStreamType = "octet-stream" in contentTypeStr # True
            if isOctetStreamType:
                # 'https://appdlc-drcn.hispace.hicloud.com/dl/appdl/application/apk/47/4795a70deeac4103a8e6182b257ec4a9/com.shenghe.wzcq.huawei.2012221953.apk?sign=f9001091ej1001032000000000000100000000000500100101010@CC0A6D3E117D430483B55B08162FB0F4&extendStr=detail%3A1%3B&tabStatKey=A09000&relatedAppId=C100005003&hcrId=CC0A6D3E117D430483B55B08162FB0F4&maple=0&distOpEntity=HWSW'
                foundApkInUrl = re.search("[^/]+\.apk", curApkUrl, re.I) # <re.Match object; span=(101, 142), match='com.tanwan.yscqlyzf.huawei.2012141704.apk'>
                # isApkInUrl = bool(foundApkInUrl) # True
                # 'https://api-game.meizu.com/games/public/download/redirect/url?auth_time=43200&package_name=com.hirealgame.hswsw.mz&source=0&timestamp=1611106503304&type=2&sign=fce0aeff829a8b4c4f493f2e86c9e35b&fname=com.hirealgame.hswsw.mz_402'
                foundDownloadInUrl = re.search("download", curApkUrl, re.I) # <re.Match object; span=(40, 48), match='download'>
                isValidOctetStreamUrl = foundApkInUrl or foundDownloadInUrl
                if isValidOctetStreamUrl:
                    isValidApkUrl = True
                    errMsg = ""
                else:
                    isValidApkUrl = False
                    errMsg = "Content Type is octet-stream but no .apk or download in url %s" % curApkUrl
                    # 'Content Type is octet-stream but no .apk in url https://appdlc-drcn.hispace.hicloud.com/dl/appdl/application/apk/db/dbd3fbf4bb7c4e199e27169b83054afd/com.zsbf.rxsc.2010151906.rpk?sign=f9001091ej1001042000000000000100000000000500100101010@21BD93C47A224B178DE4FCDEAC296E3F&extendStr=detail%3A1%3B&tabStatKey=A09000&relatedAppId=C100450321&hcrId=21BD93C47A224B178DE4FCDEAC296E3F&maple=0&distOpEntity=HWSW'

                    # continue check for get redirected 302 real url
                    redirectedRealUrl = get302RealUrl(curApkUrl)
                    if redirectedRealUrl != curApkUrl:
                        # Special:
                        # 'https://appdlc-drcn.hispace.hicloud.com/dl/appdl/application/apk/db/dbd3fbf4bb7c4e199e27169b83054afd/com.zsbf.rxsc.2010151906.rpk?sign=f9001091ej1001042000000000000100000000000500100101010@21BD93C47A224B178DE4FCDEAC296E3F&extendStr=detail%3A1%3B&tabStatKey=A09000&relatedAppId=C100450321&hcrId=21BD93C47A224B178DE4FCDEAC296E3F&maple=0&distOpEntity=HWSW'
                        # ->
                        # 'https://appdl-1-drcn.dbankcdn.com/dl/appdl/application/apk/db/dbd3fbf4bb7c4e199e27169b83054afd/com.zsbf.rxsc.2010151906.rpk?sign=f9001091ej1001042000000000000100000000000500100101010@21BD93C47A224B178DE4FCDEAC296E3F&extendStr=detail%3A1%3B&tabStatKey=A09000&relatedAppId=C100450321&hcrId=21BD93C47A224B178DE4FCDEAC296E3F&maple=0&distOpEntity=HWSW'
                        # but still invalid

                        # # for debug
                        # AllDebugedList = [
                        #     "dbankcdn.com",
                        #     "vivo.com.cn",
                        #     "xiaomi.com",
                        # ]
                        # isDebugged = False
                        # for eachDebuged in AllDebugedList:
                        #     if eachDebuged in redirectedRealUrl:
                        #         isDebugged = True
                        #         break
                        # isNotDebuged = not isDebugged
                        # if isNotDebuged:
                        #     logging.info("Not debugged: %s", redirectedRealUrl)

                        curApkUrl = redirectedRealUrl
                        # Normal Expected:
                        # (1) http://appstore.vivo.com.cn/appinfo/downloadApkFile?id=1676650&app_version=100.0
                        #     ->
                        #     http://apkgamedefbddl.vivo.com.cn/appstore/developer/soft/201612/201612061417371446252.apk
                        # (2) 'https://app.mi.com/download/610735?id=com.mobileuncle.toolhero&ref=appstore.mobile_download&nonce=-2797954111430111294%3A26814339&appClientId=2882303761517485445&appSignature=oxBvxJhrGBuUBck5cgFqasC7gI5rLez99KZ24VMiRpA'
                        #     ->
                        #     'https://fga1.market.xiaomi.com/download/AppStore/03367f59ffcbc4719185da0d550a3b407f50cfb62/com.mobileuncle.toolhero.apk'
                        foundApkInUrl = re.search("[^/]+\.apk", curApkUrl, re.I) # <re.Match object; span=(101, 142), match='com.tanwan.yscqlyzf.huawei.2012141704.apk'>
                        foundDownloadInUrl = re.search("download", curApkUrl, re.I) # <re.Match object; span=(40, 48), match='download'>
                        isValidOctetStreamUrl = foundApkInUrl or foundDownloadInUrl
                        if isValidOctetStreamUrl:
                            isValidApkUrl = True
                            errMsg = ""
                        else:
                            isValidApkUrl = False
                            errMsg = "Content Type is octet-stream but no .apk or download in redirected url %s" % curApkUrl
                            # 'Content Type is octet-stream but no .apk in redirected url https://appdl-1-drcn.dbankcdn.com/dl/appdl/application/apk/db/dbd3fbf4bb7c4e199e27169b83054afd/com.zsbf.rxsc.2010151906.rpk?sign=f9001091ej1001042000000000000100000000000500100101010@21BD93C47A224B178DE4FCDEAC296E3F&extendStr=detail%3A1%3B&tabStatKey=A09000&relatedAppId=C100450321&hcrId=21BD93C47A224B178DE4FCDEAC296E3F&maple=0&distOpEntity=HWSW'
                            # 
            # else:
            #     # for debug
            #     logging.error("not expected content type: %s", contentTypeStr)
            #     # https://app.mi.com/download/1302518?id=com.bgnb.wgll.mi&ref=appstore.mobile_download&nonce=8850090374002965212%3A26849396&appClientId=2882303761517485445&appSignature=1lKwhUaTOGHTvIPOl-sjmR2YMjkbHWy9TrJeTeJfbjU
            #     # (2)
            #     # https://api-game.meizu.com/games/public/download/redirect/url?auth_time=43200&package_name=com.mjgame.onweb.mz&source=0×tamp=1611279954158&type=2&sign=d2d619f6314a4d342609d8eb33338ac7&fname=com.mjgame.onweb.mz_17
            #     # ->
            #     # application/json
            #     # (3) 已下架的 不存在的：
            #     # http://app.mi.com/details?id=com.game.shangguxiux.mi
            #     # -> 之前的下载地址：
            #     # 'https://app.mi.com/download/1294550?id=com.game.shangguxiux.mi&ref=appstore.mobile_download&nonce=5009463403913763592%3A26865020&appClientId=2882303761517485445&appSignature=N46VkyUq2p0QwUrKym_uqWxSvoFdiTA1GaPvkzRxONg'
            #     # -> 返回的是：'text/html; charset=UTF-8'
    else:
        isValidApkUrl = False
        errMsg = "Failed to get content type for url %s" % curApkUrl
        # 已下架的游戏，之前的下载地址： http://s.shouji.qihucdn.com/210112/0c24ebd2f1132df071f5db7301c723e6/com.szs.qh360_1.apk?en=curpage%3D%26exp%3D1611816296%26from%3Dopenbox_Iservice_AppDetail%26m2%3D%26ts%3D1611211496%26tok%3D3960c113b5eb6c09508b2ad674e5757b%26v%3D%26f%3Dz.apk

    if isValidApkUrl:
        gotApkFileSize = getFileSizeFromHeaders(respHeaderDict) # 190814345
        if gotApkFileSize:
            apkFileSize = gotApkFileSize
            isAllValid = True
        else:
            isAllValid = False
            errMsg = "Failed to get android apk file size from url %s" % curApkUrl
            # 
    else:
        isAllValid = False

    if isAllValid:
        return isAllValid, apkFileSize
    else:
        return isAllValid, errMsg

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


def parseUrl(curUrl, pageLoadTimeout=10):
    """Use requests to parse url, to get final url, title, html

    Args:
        curUrl (str): current url, probabaly short link address
        pageLoadTimeout (int): timeout in seconds for load page. Default is 10 seconds.
    Returns:
        parse result(dict)
    Raises:
    Examples:
    """
    respValue = None

    try:
        curHeader = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
        }
        resp = requests.get(curUrl, headers=curHeader, timeout=pageLoadTimeout)

        if resp.history:
            logging.debug("Found redirected history url:")
            for curIdx, curResp in enumerate(resp.history):
                curNum = curIdx + 1
                logging.debug("  [%d] status_code=%s, url=%s", curNum, curResp.status_code, curResp.url)

        finalUrl = resp.url
        logging.debug("finalUrl=%s", finalUrl) # 
        finalHtml = resp.text
        finalTitle = extractHtmlTitle(finalHtml)
        logging.debug("finalTitle=%s", finalTitle)

        respValue = {
            "isParseOk": True,
            "url": finalUrl,
            "title": finalTitle,
            "html": finalHtml,
        }
    except Exception as err:
        errStr = str(err)
        # "HTTPConnectionPool(host='dmh2.cn', port=80): Max retries exceeded with url: /9jaSp0 (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x1036b7220>: Failed to establish a new connection: [Errno 8] nodename nor servname provided, or not known'))"
        logging.debug("requests get %s exception: %s", curUrl, errStr)

        respValue = {
            "isParseOk": False,
            "errMsg": errStr, 
        }

    return respValue

#-------------------------------------------------------------------------------
# Small Crawler
#-------------------------------------------------------------------------------

def parsePhoneSegmentInfo_ip138(inputPhoneSegment):
    """Parse out phone segment info (location, city, etc.), emulating ip138

    Args:
        inputPhoneSegment (str): phone segment
    Returns:
        dict
    Raises:
    Examples:
        '1300100' -> {'您查询的手机号码段': '1300100', '卡号归属地': '北京', '卡类型': '联通130卡', '区号': '010', '邮编': '100000'}
    """
    Ip138_ParseMobileUrl = "https://www.ip138.com/mobile.asp"

    respKeyValueDict = {}

    qsParaDict = {
        "mobile": inputPhoneSegment,
        "action": "mobile",
    }
    # "https://www.ip138.com/mobile.asp?mobile=1300109&action=mobile"

    """
        GET /mobile.asp?mobile=1300109&action=mobile HTTP/1.1
        Host: www.ip138.com
        Connection: keep-alive
        Pragma: no-cache
        Cache-Control: no-cache
        sec-ch-ua: "Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"
        sec-ch-ua-mobile: ?0
        Upgrade-Insecure-Requests: 1
        User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
        Sec-Fetch-Site: none
        Sec-Fetch-Mode: navigate
        Sec-Fetch-User: ?1
        Sec-Fetch-Dest: document
        Accept-Encoding: gzip, deflate, br
        Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
        Cookie: ASPSESSIONIDQAQTTSDA=NPKPDMNAIDBMJPFALCKDCOON
    """

    gHeaderDict = {
        # "Host": "www.ip138.com",
        # "Connection": "keep-alive",
        # "Pragma": "no-cache",
        # "Cache-Control": "no-cache",
        # "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        # "sec-ch-ua-mobile": "?0",
        # "Upgrade-Insecure-Requests": "1",
        "User-Agent": UserAgent_Mac,
        # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        # "Sec-Fetch-Site": "none",
        # "Sec-Fetch-Mode": "navigate",
        # "Sec-Fetch-User": "?1",
        # "Sec-Fetch-Dest": "document",
        # "Accept-Encoding": "gzip, deflate, br",
        # "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        # "Cookie": "ASPSESSIONIDQAQTTSDA=NPKPDMNAIDBMJPFALCKDCOON",
    }

    logging.info("opening %s", Ip138_ParseMobileUrl)
    resp = requests.get(Ip138_ParseMobileUrl, params=qsParaDict, headers=gHeaderDict)
    logging.info("resp.url=%s", resp.url)
    logging.info("resp=%s", resp)

    logging.debug("resp.encoding=%s", resp.encoding)
    # resp.encoding = "ISO-8859-1"
    resp.encoding = "UTF-8" # to fix zhcn char messy
    # logging.debug("resp.encoding=%s", resp.encoding)

    respHtml = resp.text
    logging.debug("respHtml=%s", respHtml)

    soup = BeautifulSoup(respHtml, "html.parser")
    logging.debug("soup=%s", soup)
    """
            <tbody>
                <tr>
                    <td>您查询的手机号码段</td>
                    <td><span>1300109</span> <a href="  //jx.ip138.com/1300109/" target="_blank">测吉凶(<font color="red">新</font>)</a></td>
                </tr>
                <tr><td>卡号归属地</td><td><span>北京&nbsp;</span></td></tr>
                <tr><td>卡&nbsp;类&nbsp;型</td><td><span>联通130卡</span></td></tr>
                <tr><td>区 号</td><td><span>010</span></td></tr>
                <tr><td>邮 编</td><td><span>100000</span></td></tr>
            </tbody>
        </table>
    """
    tbodySoup = soup.find("tbody")
    logging.debug("tbodySoup=%s", tbodySoup)
    trSoupList = tbodySoup.find_all("tr")
    logging.debug("trSoupList=%s", trSoupList)

    # allItemDictList = []
    for eachTrSoup in trSoupList:
        logging.debug("eachTrSoup=%s", eachTrSoup)
        tdSoupList = eachTrSoup.find_all("td")
        tdSoupListNum = len(tdSoupList)
        TotalTdNum = 2
        if tdSoupListNum != TotalTdNum:
            logging.error("Unexpeced td list: %s", tdSoupList)
        else:
            tdKeySoup = tdSoupList[0]
            tdValueSoup = tdSoupList[1]
            logging.debug("tdKeySoup=%s, tdValueSoup=%s", tdKeySoup, tdValueSoup)
            # tdKeySoup=<td>您查询的手机号码段</td>, tdValueSoup=<td><span>1300109</span> <a href="  //jx.ip138.com/1300109/" target="_blank">测吉凶(<font color="red">新</font>)</a></td>
            keyStr = tdKeySoup.string
            logging.debug("keyStr=%s", keyStr)
            # keyStr=您查询的手机号码段
            # keyStr = keyStr.strip()
            pureKeyStr = toPureStr(keyStr)
            logging.debug("pureKeyStr=%s", pureKeyStr)
            # pureKeyStr=您查询的手机号码段
            spanValueSoup = tdValueSoup.find("span")
            logging.debug("spanValueSoup=%s", spanValueSoup)
            # spanValueSoup=<span>1300109</span>
            valueStr = spanValueSoup.string
            logging.debug("valueStr=%s", valueStr)
            # valueStr=1300109
            pureValueStr = toPureStr(valueStr)
            logging.debug("pureValueStr=%s", pureValueStr)
            # pureValueStr=1300109
            curItemDict = {
                "key": pureKeyStr,
                "value": pureValueStr
            }
            logging.info("curItemDict=%s", curItemDict)
            # curItemDict={'key': '您查询的手机号码段', 'value': '1300109'}
            # allItemDictList.append(curItemDict)
            respKeyValueDict[pureKeyStr] = pureValueStr

    # logging.info("allItemDictList=%s", allItemDictList)
    # allItemDictList=[{'key': '您查询的手机号码段', 'value': '1300100'}, {'key': '卡号归属地', 'value': '北京'}, {'key': '卡类型', 'value': '联通130卡'}, {'key': '区号', 'value': '010'}, {'key': '邮编', 'value': '100000'}]
    logging.info("respKeyValueDict=%s", respKeyValueDict)
    # respKeyValueDict={'您查询的手机号码段': '1300100', '卡号归属地': '北京', '卡类型': '联通130卡', '区号': '010', '邮编': '100000'}
    return respKeyValueDict

################################################################################
# Test
################################################################################

if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))