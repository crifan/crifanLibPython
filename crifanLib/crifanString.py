#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanString.py
Function: crifanLib's string related functions.
Version: v1.2 20180615
Note:
1. latest version and more can found here:
https://github.com/crifan/crifanLibPython
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "v1.2"
__copyright__ = "Copyright (c) 2019, Crifan Li"
__license__ = "GPL"


import re
import json
import random
from enum import Enum
import time
import uuid

try:
    import chardet
except ImportError:
    print("crifanString: Can not found lib chardet")

import urllib

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

import codecs

# from . import crifanMath
# from . import crifanHttp
# from . import crifanSystem
import crifanLib.crifanMath
import crifanLib.crifanHttp
import crifanLib.crifanSystem

################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanString"

################################################################################
# Global Variable
################################################################################
gVal = {
}

gConst = {
}

# login to manager app key:
#     有道智云
#     https://ai.youdao.com/fanyi-services.s
Youdao_API_URL = "https://openapi.youdao.com/api"
Youdao_APP_ID = "xxx"
Youdao_SECRET_KEY = "yyy"

# for supported languages can refer:
#     有道智云 -> 帮助与文档 > 产品文档 > 自然语言翻译 > API 文档 > 支持的语言表
#     http://ai.youdao.com/docs/doc-trans-api.s#p05
constYoudaoErrorCode = {
    101: "缺少必填的参数，出现这个情况还可能是et的值和实际加密方式不对应",
    102: "不支持的语言类型",
    103: "翻译文本过长",
    104: "不支持的API类型",
    105: "不支持的签名类型",
    106: "不支持的响应类型",
    107: "不支持的传输加密类型",
    108: "appKey无效，注册账号， 登录后台创建应用和实例并完成绑定， 可获得应用ID和密钥等信息，其中应用ID就是appKey（ 注意不是应用密钥）",
    109: "batchLog格式不正确",
    110: "无相关服务的有效实例",
    111: "开发者账号无效，可能是账号为欠费状态",
    201: "解密失败，可能为DES,BASE64,URLDecode的错误",
    202: "签名检验失败",
    203: "访问IP地址不在可访问IP列表",
    301: "辞典查询失败",
    302: "翻译查询失败",
    303: "服务端的其它异常",
    401: "账户已经欠费停"
}

################################################################################
# Internal Function
################################################################################


################################################################################
# String Function
################################################################################


################################################################################
# String
################################################################################



def strToList(inputStr, separatorChar=","):
    """
        convert string to list by using separator char, and strip each str in list

        example:
            u'Family members,  Sick'
            or 'Family members,  Sick,'
            ->
            [u'Family members', u'Sick']
    :param separatorChar: the separator char
    :return: converted list
    """
    convertedList = []
    stripedList = []

    if inputStr:
        convertedList = inputStr.split(separatorChar) #<type 'list'>: [u'Family members', u'Sick']

        for eachStr in convertedList:
            stripedStr = eachStr.strip()
            if stripedStr:
                stripedList.append(stripedStr)

    return stripedList


def isStringInstance(someVar):
    """check whether is string instance"""
    if crifanLib.crifanSystem.isPython2():
        return isinstance(someVar, unicode)
    else:
        return isinstance(someVar, str)


def formatString(inputStr, paddingChar="=", totalWidth=80):
    """
    format string, to replace for:
    print '{0:=^80}'.format("xxx");

    auto added space before and after input string
    """
    formatting = "{0:" + paddingChar + "^" + str(totalWidth) + "}"
    return formatting.format(" " + inputStr + " ")


def removeNonWordChar(inputString):
    """
        remove non-word char == only retian alphanumeric character (char+number) and underscore
        eg:
            from againinput4@yeah to againinput4yeah
            from green-waste to greenwaste
    :param inputString:
    :return:
    """
    return re.sub(r"[^\w]", "", inputString)  # non [a-zA-Z0-9_]


def removeInvalidCharInFilename(inputFilename, replacedChar=""):
    """
    Remove invalid char in filename
    eg:
    《神魔手下好当差/穿越之傀儡娃娃》全集
    《神魔手下好当差_穿越之傀儡娃娃》全集
    """
    filteredFilename = inputFilename
    invalidCharList = ['^', '~', '<', '>', '*', '?', '/', '\\', '!']
    for eachInvalidChar in invalidCharList:
        filteredFilename = filteredFilename.replace(eachInvalidChar, replacedChar)
    return filteredFilename


def removeCtlChr(inputString):
    """
        remove control character from input string, otherwise will cause wordpress importer import failed
        for wordpress importer, if contains control char, will fail to import wxr
        eg:
        1. http://againinput4.blog.163.com/blog/static/172799491201110111145259/
        content contains some invalid ascii control chars
        2. http://hi.baidu.com/notebookrelated/blog/item/8bd88e351d449789a71e12c2.html
        165th comment contains invalid control char: ETX
        3. http://green-waste.blog.163.com/blog/static/32677678200879111913911/
        title contains control char:DC1, BS, DLE, DLE, DLE, DC1
    :param inputString:
    :return:
    """
    validContent = ''
    for c in inputString:
        asciiVal = ord(c)
        validChrList = [
            9,  # 9=\t=tab
            10,  # 10=\n=LF=Line Feed=换行
            13,  # 13=\r=CR=回车
        ]
        # filter out others ASCII control character, and DEL=delete
        isValidChr = True
        if (asciiVal == 0x7F):
            isValidChr = False
        elif ((asciiVal < 32) and (asciiVal not in validChrList)):
            isValidChr = False

        if (isValidChr):
            validContent += c

    return validContent


def removeAnsiCtrlChar(inputString):
    """remove ANSI control character: 0x80-0xFF"""
    validContent = ''
    for c in inputString:
        asciiVal = ord(c)
        isValidChr = True
        if ((asciiVal >= 0x80) and (asciiVal <= 0xFF)):
            # if ((asciiVal >= 0xB0) and (asciiVal <= 0xFF)) : # test
            isValidChr = False
            # print "asciiVal=0x%x"%asciiVal

        if (isValidChr):
            validContent += c
    return validContent


def convertToTupleVal(equationStr):
    """
        convert the xxx=yyy into tuple('xxx', yyy), then return the tuple value
        [makesure input string]
        (1) is not include whitespace
        (2) include '='
        (3) last is no ';'
        [possible input string]
        blogUserName="againinput4"
        publisherEmail=""
        synchMiniBlog=false
        publishTime=1322129849397
        publisherName=null
        publisherNickname="\u957F\u5927\u662F\u70E6\u607C"
    :param equationStr:
    :return:
    """
    (key, value) = ('', None)

    try:
        # Note:
        # here should not use split with '=', for maybe input string contains string like this:
        # http://img.bimg.126.net/photo/hmZoNQaqzZALvVp0rE7faA==/0.jpg
        # so use find('=') instead
        firstEqualPos = equationStr.find("=")
        key = equationStr[0:firstEqualPos]
        valuePart = equationStr[(firstEqualPos + 1):]

        # string type
        valLen = len(valuePart)
        if valLen >= 2:
            # maybe string
            if valuePart[0] == '"' and valuePart[-1] == '"':
                # is string type
                value = str(valuePart[1:-1])
            elif (valuePart.lower() == 'null'):
                value = None
            elif (valuePart.lower() == 'false'):
                value = False
            elif (valuePart.lower() == 'true'):
                value = True
            else:
                # must int value
                value = int(valuePart)
        else:
            # len=1 -> must be value
            value = int(valuePart)

        # print "Convert %s to [%s]=%s"%(equationStr, key, value);
    except:
        (key, value) = ('', None)
        print("Fail of convert the equal string %s to value" % (equationStr))

    return key, value


def filterNonAsciiStr(originalUnicodeStr):
    """
        remove (special) non-ascii (special unicode char)
        -> avoid save to ascii occur error:
        UnicodeEncodeError: 'ascii' codec can't encode character u'\u2028' in position 318: ordinal not in range(128)

        eg:
        remove \u2028 from
        Peapack, NJ. \u2028\u2028Mrs. Onassis bought
        in
        http://autoexplosion.com/cars/buy/150631.php

        remove \u201d from
        OC Choppers Super Stretch 124\u201d Softail
        in
        http://autoexplosion.com/bikes/buy/11722.php
    """
    filteredAscii = originalUnicodeStr.encode("ascii", 'ignore')
    filteredUni = filteredAscii.decode("ascii", 'ignore')
    return filteredUni

#----------------------------------------
# JSON
#----------------------------------------


def jsonToStr(jsonDict, indent=2):
    return json.dumps(jsonDict, indent=2, ensure_ascii=False)


def strToJson(jsonStr):
    jsonDict = json.loads(jsonStr, encoding="utf-8")
    return jsonDict


def jsonToPrettyStr(jsonDictOrStr, indent=4, sortKeys=False):
    """
    convert json dictionary un-formatted json string to prettify string

    '{"outputFolder":"output","isResetOutput":true,"waitTimeout":10,"msStore":{"productList":[{"productUrl":"","buyNum":2}]}}'
    ->
    {
        "msStore": {
            "productList": [
                {
                    "productUrl": "",
                    "buyNum": 2
                }
            ]
        },
        "outputFolder": "output",
        "isResetOutput": true,
        "waitTimeout": 10
    }

    :param jsonDictOrStr: json dict or json str
    :param indent: indent space number
    :param sortKeys: output is sort by key or not
    :return: formatted/prettified json string with indent
    """

    prettifiedStr = ""
    jsonDict = jsonDictOrStr
    if type(jsonDictOrStr) is str:
        jsonDict = json.loads(jsonDictOrStr)

    prettifiedStr = json.dumps(jsonDict, indent=indent, sort_keys=sortKeys)
    return prettifiedStr

#----------------------------------------
# String related using chardet
#----------------------------------------


def strIsAscii(strToDect) :
    """
    check whether the strToDect is ASCII string
    Note: should install chardet before use this

    :param strToDect:
    :return:
    """
    isAscii = False
    encInfo = chardet.detect(strToDect)
    if (encInfo['confidence'] > 0.9) and (encInfo['encoding'] == 'ascii'):
        isAscii = True
    return isAscii


def getStrPossibleCharset(inputStr):
    """
    get the possible(possiblility > 0.5) charset of input string

    :param inputStr: input string
    :return: the most possible charset
    """

    possibleCharset = "ascii"
    #possibleCharset = "UTF-8"
    encInfo = chardet.detect(inputStr)
    #print "encInfo=",encInfo
    if (encInfo['confidence'] > 0.5):
        possibleCharset = encInfo['encoding']
    return possibleCharset
    #return encInfo['encoding']


#----------------------------------------
# String related using http
#----------------------------------------

def translateString(strToTrans, fromLanguage="zh-CHS", toLanguage="EN"):
    """
    translate string from source language to destination language

    :param strToTrans: string to translate
    :param fromLanguage: from language
    :param toLanguage: to language
    :return: translated unicode string
    """
    # logging.debug("strToTrans=%s, from=%s, to=%s", strToTrans, fromLanguage, toLanguage)
    transOK, respInfo = False, None

    curTimeFloat = time.time() # 1584168160.8058722
    curTimeInt = int(curTimeFloat) # 1584168160
    curTimeStr = str(curTimeInt) # '1584168160'
    appId = Youdao_APP_ID
    # saltStr = str(random.randint(1, 65536))
    curUuid = uuid.uuid1() # UUID('bd9ef086-65c1-11ea-93e4-acbc327f0101')
    saltStr = str(curUuid) # 'bd9ef086-65c1-11ea-93e4-acbc327f0101'
    secretKey = Youdao_SECRET_KEY
    inputLen = len(strToTrans)
    if inputLen > 20:
        first10 = strToTrans[:10]
        last10 = strToTrans[-10:]
        lenStr = str(inputLen)
        inputPart = first10 + lenStr + last10
    else:
        inputPart = strToTrans
    strToMd5 = appId + inputPart + saltStr + curTimeStr + secretKey
    # '15xxx26Mac中给pip更换源以加速下载eae1e774-65c1-11ea-b769-acbc327f01011584169409olj4xxxV'
    sha256Sign = crifanLib.crifanMath.calcSha256(strToMd5) # 

    curHeaders = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    # query string
    qsDict = {
        "q": strToTrans,
        "from": fromLanguage,
        "to": toLanguage,
        "appKey": appId,
        "salt": saltStr,
        "sign": sha256Sign,
        "signType": "v3",
        "curtime": curTimeStr,
    }
    resp = requests.post(Youdao_API_URL, headers=curHeaders, data=qsDict)
    logging.info("resp=%s", resp)

    respJson = resp.json()
    logging.info("respJson=%s", respJson)
    # {'tSpeakUrl': 'http://openapi.youdao.com/ttsapi?q=Give+the+PIP+replacement+source+to+the+Mac+to+speed+up+the+download&langType=en&sign=45D395166167C153EA9D8C1567002419&salt=1584171072079&voice=4&format=mp3&appKey=152xxx26', 'query': 'Mac中给pip更换源以加速下载', 'translation': ['Give the PIP replacement source to the Mac to speed up the download'], 'errorCode': '0', 'dict': {'url': 'yddict://m.youdao.com/dict?le=eng&q=Mac%E4%B8%AD%E7%BB%99pip%E6%9B%B4%E6%8D%A2%E6%BA%90%E4%BB%A5%E5%8A%A0%E9%80%9F%E4%B8%8B%E8%BD%BD'}, 'webdict': {'url': 'http://m.youdao.com/dict?le=eng&q=Mac%E4%B8%AD%E7%BB%99pip%E6%9B%B4%E6%8D%A2%E6%BA%90%E4%BB%A5%E5%8A%A0%E9%80%9F%E4%B8%8B%E8%BD%BD'}, 'l': 'zh-CHS2en', 'speakUrl': 'http://openapi.youdao.com/ttsapi?q=Mac%E4%B8%AD%E7%BB%99pip%E6%9B%B4%E6%8D%A2%E6%BA%90%E4%BB%A5%E5%8A%A0%E9%80%9F%E4%B8%8B%E8%BD%BD&langType=zh-CHS&sign=E789E4FCDB1321503332112FA1058BFC&salt=1584171072079&voice=4&format=mp3&appKey=15xxx26'}

    if resp.ok:
        # {'errorCode': '101', 'l': 'null2null'}
        errorCode = int(respJson["errorCode"])
        if errorCode != 0:
            transOK = False
            errMsg = "未知错误"
            if errorCode in constYoudaoErrorCode.keys():
                errMsg = constYoudaoErrorCode[errorCode]

            respInfo = {
                "errCode": errorCode,
                "errMsg": errMsg
            }
        else:
            queryUnicode = respJson["query"]
            translatedEnStr = respJson["translation"][0]

            transOK = True
            respInfo = translatedEnStr
    else:
        transOK = False
        respInfo = {
            "errCode": resp.status_code,
            "errMsg": resp.text
        }

    logging.info("%s -> [%s, %s]", strToTrans, transOK, respInfo)
    return transOK, respInfo


def transZhcnToEn(strToTrans):
    """translate the Chinese(zh-CHS) string to English(EN)"""
    translatedStr = strToTrans
    transOK = False
    transErr = ''

    if strIsAscii(strToTrans):
        transOK = True
        translatedStr = strToTrans
    else:
        # (transOK, translatedStr) = translateString(strToTrans, "zh-CN", "en")
        (transOK, translatedStr) = translateString(strToTrans, "zh-CHS", "EN")

    return transOK, translatedStr


#----------------------------------------
# String Language
#----------------------------------------

class LanguageType(Enum):
    UNKNOWN = '未知语言'
    ZHCN = '中文'
    EN = '英文'
    JP = '日文'

def detectLanguageType(inputString, possibilityRatioThreshold = 0.7):
    """
        input: a string
        output: the possible language type and possiblity

        * 测试中文
          * 输入：`testInputStr1 = "测试Python代码的编程逻辑和基本语法"`
          * 输出：中文，0.7
        * 测试英文
          * 输入：`testInputStr2 = "test python basic programming logic and grammar"`
          * 输出：英文，1.0
        * 测试未超过比例
          * 输入：`testInputStr3 = "test python basic 代码逻辑和基本语法"`
          * 输出：未知，0.0
            * 提示，此时：
              * 0.375部分是中文
              * 0.625部分是英文
                * 都没有超过0.7，所以输出 未知语言
        * 测试日文
          * 输入：`testInputStr4 = "Pythonコードプログラミングのロジックと基本スキルをテストする"`
          * 输出：日文，0.76
    """
    lanType = LanguageType.UNKNOWN
    lanPossibilityRatio = 0.0
    inputStrNoSpace = re.sub("\s", "", inputString)
    totalCharNumLen = len(inputStrNoSpace)
    if totalCharNumLen <= 0:
        return lanType, lanPossibilityRatio

    languagePatternList = [
        {
            "lanType" : LanguageType.ZHCN,
            "lanPattern" : "[\\u4e00-\\u9fa5]"
        },
        {
            "lanType" : LanguageType.EN,
            "lanPattern" : "[a-zA-Z]"
        },
        {
            "lanType" : LanguageType.JP,
            "lanPattern" : "[\\u3040-\\u309F\\u30A0-\\u30FF]"
        }
    ]
    for curPatternDict in languagePatternList:
        # curCharNumList = re.compile(curPatternDict['lanPattern']).findall(inputStrNoSpace)
        curCharNumList = re.findall(curPatternDict['lanPattern'], inputStrNoSpace)
        curCharNumLen = len(curCharNumList)
        curLanCharRatio = float(curCharNumLen)/float(totalCharNumLen)
        if curLanCharRatio >= possibilityRatioThreshold:
            lanType = curPatternDict['lanType']
            lanPossibilityRatio = curLanCharRatio
            break

    return lanType, lanPossibilityRatio

################################################################################
# Test
################################################################################



if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))