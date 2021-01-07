#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanString.py
Function: crifanLib's string related functions
Version: 20210107
Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/crifanString.py
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20210107"
__copyright__ = "Copyright (c) 2021, Crifan Li"
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
# Program Language Detection
################################################################################

def isHtmlXmlLanguage(codeStr):
    """Detect code str is html/xml programming language or not

    Args:
        codeStr (str): input string of code
    Returns:
        is html/xml language (bool), the language name: 'html'/'xml'(str)
    Raises:
    """
    ValidHtmlMinTagNum = 2

    # HTML Tags Ordered Alphabetically
    # https://www.w3schools.com/TAGS/default.asp
    HtmlTagList = [
        "a",
        "abbr",
        "acronym",
        "address",
        "applet",
        "area",
        "article",
        "aside",
        "audio",
        "b",
        "base",
        "basefont",
        "bdi",
        "bdo",
        "big",
        "blockquote",
        "body",
        "br",
        "button",
        "canvas",
        "caption",
        "center",
        "cite",
        "code",
        "col",
        "colgroup",
        "data",
        "datalist",
        "dd",
        "del",
        "details",
        "dfn",
        "dialog",
        "dir",
        "div",
        "dl",
        "dt",
        "em",
        "embed",
        "fieldset",
        "figcaption",
        "figure",
        "font",
        "footer",
        "form",
        "frame",
        "frameset",
        "h1",
        "head",
        "header",
        "hr",
        "html",
        "i",
        "iframe",
        "img",
        "input",
        "ins",
        "kbd",
        "label",
        "legend",
        "li",
        "link",
        "main",
        "map",
        "mark",
        "meta",
        "meter",
        "nav",
        "noframes",
        "noscript",
        "object",
        "ol",
        "optgroup",
        "option",
        "output",
        "p",
        "param",
        "picture",
        "pre",
        "progress",
        "q",
        "rp",
        "rt",
        "ruby",
        "s",
        "samp",
        "script",
        "section",
        "select",
        "small",
        "source",
        "span",
        "strike",
        "strong",
        "style",
        "sub",
        "summary",
        "sup",
        "svg",
        "table",
        "tbody",
        "td",
        "template",
        "textarea",
        "tfoot",
        "th",
        "thead",
        "time",
        "title",
        "tr",
        "track",
        "tt",
        "u",
        "ul",
        "var",
        "video",
        "wbr",
    ]

    isXmlLang = False
    isHtmlLang = False
    isValidLang = False
    langName = ""

    tagNameList = []

    """
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
    </dict>
    """
    # normalTagMatchIter = re.finditer("<(?P<normalTagName>\w+)>[^<>]+<(?P=normalTagName)>", codeStr)
    """
        <ul>
            <li>
        <div>豆瓣：http://pypi.douban.com</div></li>
            <li>
        <div>阿里云：http://mirrors.aliyun.com/pypi/simple</div></li>
            <li>
        <div>清华大学：https://pypi.tuna.tsinghua.edu.cn/simple</div></li>
        </ul>
    """
    normalTagMatchIter = re.finditer("<(?P<normalTagName>\w+)>[^<>]*(</(?P=normalTagName)>)?", codeStr, re.M)
    normalTagMatchList = list(normalTagMatchIter)
    if normalTagMatchList:
        isXmlLang = True
        for eachNormalTagMatch in normalTagMatchList:
            normalTagName = eachNormalTagMatch.group("normalTagName")
            if normalTagName not in tagNameList:
                tagNameList.append(normalTagName)

    selfCloseTagMatchIter = re.finditer("<(?P<selfCloseTagName>\w+)\s*/>", codeStr)
    selfCloseTagMatchList = list(selfCloseTagMatchIter)
    if selfCloseTagMatchList:
        isXmlLang = True
        for eachSelfCloseTagMatch in selfCloseTagMatchList:
            selfCloseTagName = eachSelfCloseTagMatch.group("selfCloseTagName")
            if selfCloseTagName not in tagNameList:
                tagNameList.append(selfCloseTagName)

    if tagNameList:
        # ['ul', 'li', 'div']
        curHtmlTagNum = 0
        for eachTagName in tagNameList:
            if eachTagName in HtmlTagList:
                curHtmlTagNum += 1

        if curHtmlTagNum >= ValidHtmlMinTagNum:
            isHtmlLang = True
            isXmlLang = False

    isValidLang = isXmlLang or isHtmlLang
    if isValidLang:
        if isHtmlLang:
            langName = "html"
        elif isXmlLang:
            langName = "xml"

    # True, 'xml'
    return isValidLang, langName

def isJavascriptLanguage(codeStr):
    """Detect code str is javascript/json programming language or not

    Args:
        codeStr (str): input string of code
    Returns:
        is javascript language (bool), the language name: 'javascript'(str)
    Raises:
    """
    ValidJsMinKeyValueNum = 1

    isJsLang = False

    # is {xxx}
    # isMatchJson = re.match("^\{.+\}$", codeStr, re.S)
    """
        {
            "id": 70410,
            ...
    """
    isMatchJson = re.match("^\{.+\}?$", codeStr, re.S)
    if not isMatchJson:
        # or is [xxx]
        # isMatchJson = re.match("^\[.+\]$", codeStr, re.S)
        isMatchJson = re.match("^\[.+\]?$", codeStr, re.S)

    if isMatchJson:
        keyValueLineNum = 0
        allKeyValueList = []
        allDoubleQuoteKeyValueLine = re.findall('"\w+"\s*:\s*"?[^"]+"?,?$', codeStr, re.M)
        allKeyValueList.extend(allDoubleQuoteKeyValueLine)
        allSingleQuoteKeyValueLine = re.findall("'\w+'\s*:\s*'?[^']+'?,?$", codeStr, re.M)
        allKeyValueList.extend(allSingleQuoteKeyValueLine)
        keyValueLineNum = len(allKeyValueList)

        if keyValueLineNum >= ValidJsMinKeyValueNum:
            isJsLang = True

    return isJsLang

def isPythonLanguage(codeStr):
    """Detect code str is python programming language or not

    Args:
        codeStr (str): input string of code
    Returns:
        is python language (bool), the language name: 'python'(str)
    Raises:
    """
    ValidPythonMinRuleNum = 2

    isPyLang = False

    curValidNum = 0

    # import logging
    # import evernote.edam.type.ttypes as Types
    # # import evernote.edam.userstore.constants as UserStoreConstants
    # allImport = re.findall("import\s+[\w\.]+(\s+as\w+)?", codeStr, re.I)
    allImport = re.findall("import\s+[\w\.]+(?:\s+as\w+)?", codeStr, re.I)
    importNum = len(allImport)
    curValidNum += importNum

    # from libs.crifan import utils
    # # from evernote.api.client import EvernoteClient
    # from evernote import *
    allFromImport = re.findall("from\s+[\w\.]+\s+import\s+[\w\*]+", codeStr, re.I)
    fromImportNum = len(allFromImport)
    curValidNum += fromImportNum

    # class Evernote(object):
    allClassDef = re.findall("class\s+\w+(?:\([^\(\)]+\))?", codeStr, re.I)
    classDefNum = len(allClassDef)
    curValidNum += classDefNum

    specialKeyNum = 0
    #   def __init__(self, authToken, isSandbox=False, isChina=True):
    # if __name__ == "__main__":
    SpecialKeyList = [
        "__init__",
        "__main__",
        "__name__",
        "@staticmethod",
    ]
    for curSpecialKey in SpecialKeyList:
        allCurSpecialKey = re.findall(curSpecialKey, codeStr, re.I)
        curSpecialNum = len(allCurSpecialKey)
        specialKeyNum += curSpecialNum
    curValidNum += specialKeyNum

    # def getHost(isSandbox=False, isChina=True):
    # def initClient(self):
    # def findNotes(self, notebookId):
    # def createPost(self,
    allFunctionDef = re.findall("def\s+\w+\(\w+", codeStr, re.I)
    functionDefNum = len(allFunctionDef)
    curValidNum += functionDefNum

    # sys.path.append("lib")
    # sys.path.append("libs/evernote-sdk-python3/lib")
    # logging.debug(
    # logging.warning(
    # logging.error(
    # logging.exception(
    commonFuncNum = 0
    CommonFunctionPList = [
        "logging\.(?:(?:debug)|(?:info)|(?:warning)|(?:warn)|(?:error)|(?:critical)|(?:exception)|(?:log))",
        "sys\.path\.(?:(?:clear)|(?:copy)|(?:append)|(?:extend)|(?:pop)|(?:index)|(?:count)|(?:insert)|(?:remove)|(?:reverse)|(?:sort))",
        "os\.path\.(?:(?:abspath)|(?:basename)|(?:commonpath)|(?:commonprefix)|(?:dirname)|(?:exists)|(?:lexists)|(?:expanduser)|(?:expandvars)|(?:getatime)|(?:getmtime)|(?:getctime)|(?:getsize)|(?:isabs)|(?:isfile)|(?:isdir)|(?:islink)|(?:ismount)|(?:join)|(?:normcase)|(?:normpath)|(?:realpath)|(?:relpath)|(?:samefile)|(?:sameopenfile)|(?:samestat)|(?:split)|(?:splitdrive)|(?:splitext)|(?:supports_unicode_filenames))",
    ]
    for curCommonFuncP in CommonFunctionPList:
        allCommonFunc = re.findall(curCommonFuncP, codeStr, re.I)
        curCommonFuncNum = len(allCommonFunc)
        commonFuncNum += curCommonFuncNum
    curValidNum += commonFuncNum

    # mutiple line string:
    # (1) """xxx"""
    allMultileCommentDoubleQuote = re.findall('""".+?"""', codeStr, re.S)
    multileCommentDoubleQuoteNum = len(allMultileCommentDoubleQuote)
    curValidNum += multileCommentDoubleQuoteNum
    # (2) '''xxx'''
    allMultileCommentSingleQuote = re.findall("'''.+?'''", codeStr, re.S)
    multileCommentSingleQuoteNum = len(allMultileCommentSingleQuote)
    curValidNum += multileCommentSingleQuoteNum

    # other single rule
    OtherSingleRuleList = [
        # with open(up_filename, 'rb') as img:
        "with\s+open\(.+?\s+as\s+.+:",

        # attachment_id = response['id']
        """\w+\s*=\s*\w+\[['"]\w+['"]\]""",

        # post.content = 'This is a wonderful blog post about XML-RPC.'
        """\w+\.\w+\s*=\s*['"][^']+['"]""",

        # post.thumbnail = attachment_id
        # post.thumbnail = attachment.id
        # post = WordPressPost()
        # post.id = client.call(posts.NewPost(post))
        # "\w+\.\w+\s*=\s*[\.\w]+",
        "\w+(?:\.\w+)?\s*=\s*[\.\w]+(?:\(.*\))?",

        # up_filename = r'F:/aikanmeizi/' + prow[3] + "/" + prow[0]
        # """r['"][^"']+['"]""",
        # avoid wrong match:
        # soup = BeautifulSoup(noteContent, 'html.parser')
        # 
        # soup = mergePostTitleAndUrl(soup)
        """r['"][^"'\n]+['"]""", # internal NOT contain new line

        # >>> post = WordPressPost()
        # "^>>>\s*\w+",
        "^>>>.*$",

        # # posts == [WordPressPost, WordPressPost, ...]
        # "^#\s*\w+",
        "^#.*$",
    ]
    otherRuleTotalNum = 0
    for eachOtherSingleRule in OtherSingleRuleList:
        curRuleFoundList = re.findall(eachOtherSingleRule, codeStr, re.I|re.M)
        curRuleFoundNum = len(curRuleFoundList)

        # # for debug
        # if curRuleFoundNum > 0:
        #     logging.debug("%s -> %s", eachOtherSingleRule, curRuleFoundList)
        #     logging.debug("")

        otherRuleTotalNum += curRuleFoundNum
    curValidNum += otherRuleTotalNum

    if curValidNum >= ValidPythonMinRuleNum:
        isPyLang = True

    return isPyLang

def detectProgramLanguage(codeSnippet):
    """Detect code snippet possible programming language

    Args:
        codeSnippet (str): input string of code snippet
    Returns:
        str, programming language
    Raises:
    """

    # guessInstance = Guess()
    # languageName = guessInstance.language_name(codeSnippet)
    # return languageName
    # TODO: add re rule to detect python/java/xml/...
    # return defaultLan

    DefaultLang = "shell"

    curLang = None

    if not curLang:
        if isPythonLanguage(codeSnippet):
            curLang = "python"

    if not curLang:
        if isJavascriptLanguage(codeSnippet):
            curLang = "javascript"

    if not curLang:
        isHtmlOrXml, xmlOrHtmlLang = isHtmlXmlLanguage(codeSnippet)
        if isHtmlOrXml:
            curLang = xmlOrHtmlLang

    # if not curLang:
    #     if isJavaLanguage(codeSnippet):
    #         curLang = "java"

    if not curLang:
        curLang = DefaultLang

    return curLang

################################################################################
# Test
################################################################################

if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))