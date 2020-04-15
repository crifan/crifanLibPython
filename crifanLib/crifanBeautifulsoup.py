#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanBeautifulSoup.py
Function: crifanLib's BeautifulSoup related functions.
Version: v20200414
Note:
1. latest version and more can found here:
https://github.com/crifan/crifanLibPython
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "v20200414"
__copyright__ = "Copyright (c) 2019, Crifan Li"
__license__ = "GPL"


try:
    from BeautifulSoup import BeautifulSoup, Tag, CData, NavigableString
except ImportError:
    print("crifanBeautifulSoup: Can not found lib BeautifulSoup")

from bs4 import BeautifulSoup


# from . import crifanList
import crifanLib.crifanList

################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanBeautifulSoup"

################################################################################
# Global Variable
################################################################################
gVal = {
    'currentLevel': 0
}

gConst = {
}

################################################################################
# Internal Function
################################################################################


################################################################################
# BeautifulSoup Function
################################################################################


################################################################################
# BeautifulSoup
################################################################################


def removeSoupContentsTagAttr(soupContents, tagName, tagAttrKey, tagAttrVal="", recursive=False):
    """
        remove specific tag[key]=value in soup contents (list of BeautifulSoup.Tag/BeautifulSoup.NavigableString)
        eg:
        (1)
        removeSoupContentsTagAttr(soupContents, "p", "class", "cc-lisence")
        to remove <p class="cc-lisence" style="line-height:180%;">......</p>, from
        [
        u'\n',
        <p class="cc-lisence" style="line-height:180%;">......</p>,
        u'\u5bf9......\u3002',
         <p>跑题了。......我争取。</p>,
         <br />,
         u'\n',
         <div class="clear"></div>,
        ]
        (2)
        contents = removeSoupContentsTagAttr(contents, "div", "class", "addfav", True);
        remove <div class="addfav">.....</div> from:
        [u'\n',
        <div class="postFooter">......</div>,
        <div style="padding-left:2em">
        ...
        <div class="addfav">......</div>
        ...
        </div>,
        u'\n']
    :param soupContents:
    :param tagName:
    :param tagAttrKey:
    :param tagAttrVal:
    :param recursive:
    :return:
    """
    global gVal

    # print "in removeSoupContentsClass"
    # print "[",gVal['currentLevel'],"] input tagName=",tagName," tagAttrKey=",tagAttrKey," tagAttrVal=",tagAttrVal
    # logging.debug("[%d] input, %s[%s]=%s, soupContents:%s", gVal['currentLevel'],tagName,tagAttrKey,tagAttrVal, soupContents)
    # logging.debug("[%d] input, %s[%s]=%s", gVal['currentLevel'],tagName, tagAttrKey, tagAttrVal)

    filtedContents = []
    for singleContent in soupContents:
        # logging.debug("current singleContent=%s",singleContent)

        # logging.info("singleContent=%s", singleContent)
        # print "type(singleContent)=",type(singleContent)
        # print "singleContent.__class__=",singleContent.__class__
        # if(isinstance(singleContent, BeautifulSoup)):
        # if(BeautifulSoup.Tag == singleContent.__class__):
        # if(isinstance(singleContent, instance)):
        # if(isinstance(singleContent, BeautifulSoup.Tag)):
        if (isinstance(singleContent, Tag)):
            # print "isinstance true"

            # logging.debug("singleContent: name=%s, attrMap=%s, attrs=%s",singleContent.name, singleContent.attrMap, singleContent.attrs)
            # if( (singleContent.name == tagName)
            # and (singleContent.attrMap)
            # and (tagAttrKey in singleContent.attrMap)
            # and ( (tagAttrVal and (singleContent.attrMap[tagAttrKey]==tagAttrVal)) or (not tagAttrVal) ) ):
            # print "++++++++found tag:",tagName,"[",tagAttrKey,"]=",tagAttrVal,"\n in:",singleContent
            # #print "dir(singleContent)=",dir(singleContent)
            # logging.debug("found %s[%s]=%s in %s", tagName, tagAttrKey, tagAttrVal, singleContent.attrMap)

            # above using attrMap, but attrMap has bug for:
            # singleContent: name=script, attrMap=None, attrs=[(u'type', u'text/javascript'), (u'src', u'http://partner.googleadservices.com/gampad/google_service.js')]
            # so use attrs here
            # logging.debug("singleContent: name=%s, attrs=%s", singleContent.name, singleContent.attrs)
            attrsDict = crifanLib.crifanList.tupleListToDict(singleContent.attrs)
            if ((singleContent.name == tagName)
                    and (singleContent.attrs)
                    and (tagAttrKey in attrsDict)
                    and ((tagAttrVal and (attrsDict[tagAttrKey] == tagAttrVal)) or (not tagAttrVal))):
                # print "++++++++found tag:",tagName,"[",tagAttrKey,"]=",tagAttrVal,"\n in:",singleContent
                # print "dir(singleContent)=",dir(singleContent)
                # logging.debug("found %s[%s]=%s in %s", tagName, tagAttrKey, tagAttrVal, attrsDict)
                print("found %s[%s]=%s in %s" % (tagName, tagAttrKey, tagAttrVal, attrsDict))
            else:
                if (recursive):
                    # print "-----sub call"
                    gVal['currentLevel'] = gVal['currentLevel'] + 1
                    # logging.debug("[%d] now will filter %s[%s=]%s, for singleContent.contents=%s", gVal['currentLevel'], tagName,tagAttrKey,tagAttrVal, singleContent.contents)
                    # logging.debug("[%d] now will filter %s[%s=]%s", gVal['currentLevel'], tagName,tagAttrKey,tagAttrVal)
                    filteredSingleContent = singleContent
                    filteredSubContentList = removeSoupContentsTagAttr(filteredSingleContent.contents, tagName,
                                                                       tagAttrKey, tagAttrVal, recursive)
                    gVal['currentLevel'] = gVal['currentLevel'] - 1
                    filteredSingleContent.contents = filteredSubContentList
                    # logging.debug("[%d] after filter, sub contents=%s", gVal['currentLevel'], filteredSingleContent)
                    # logging.debug("[%d] after filter contents", gVal['currentLevel'])
                    filtedContents.append(filteredSingleContent)
                else:
                    # logging.debug("not recursive, append:%s", singleContent)
                    # logging.debug("not recursive, now append singleContent")
                    filtedContents.append(singleContent)

            # name = singleContent.name
            # if(name == tagName):
            # print "name is equal, name=",name

            # attrMap = singleContent.attrMap
            # print "attrMap=",attrMap
            # if attrMap:
            # if tagAttrKey in attrMap:
            # print "tagAttrKey=",tagAttrKey," in attrMap"
            # if(tagAttrVal and (attrMap[tagAttrKey]==tagAttrVal)) or (not tagAttrVal):
            # print "++++++++found tag:",tagName,"[",tagAttrKey,"]=",tagAttrVal,"\n in:",singleContent
            # #print "dir(singleContent)=",dir(singleContent)
            # logging.debug("found tag, tagAttrVal=%s, %s[%s]=%s", tagAttrVal, tagName, tagAttrVal, attrMap[tagAttrKey])
            # else:
            # print "key in attrMap, but value not equal"
            # if(recursive):
            # print "-----sub call 111"
            # gVal['currentLevel'] = gVal['currentLevel'] + 1
            # singleContent = removeSoupContentsTagAttr(singleContent.contents, tagName, tagAttrKey, tagAttrVal, recursive)
            # gVal['currentLevel'] = gVal['currentLevel'] -1
            # filtedContents.append(singleContent)
            # else:
            # print "key not in attrMap"
            # if(recursive):
            # print "-----sub call 222"
            # gVal['currentLevel'] = gVal['currentLevel'] + 1
            # singleContent = removeSoupContentsTagAttr(singleContent.contents, tagName, tagAttrKey, tagAttrVal, recursive)
            # gVal['currentLevel'] = gVal['currentLevel'] -1
            # filtedContents.append(singleContent)
            # else:
            # print "attrMap is None"
            # if(recursive):
            # print "-----sub call 333"
            # gVal['currentLevel'] = gVal['currentLevel'] + 1
            # singleContent = removeSoupContentsTagAttr(singleContent.contents, tagName, tagAttrKey, tagAttrVal, recursive)
            # gVal['currentLevel'] = gVal['currentLevel'] -1
            # filtedContents.append(singleContent)
            # else:
            # print "name not equal, name=",name," tagName=",tagName
            # if(recursive):
            # print "-----sub call 444"
            # gVal['currentLevel'] = gVal['currentLevel'] + 1
            # singleContent = removeSoupContentsTagAttr(singleContent.contents, tagName, tagAttrKey, tagAttrVal, recursive)
            # gVal['currentLevel'] = gVal['currentLevel'] -1
            # filtedContents.append(singleContent)
        else:
            # is BeautifulSoup.NavigableString
            # print "not BeautifulSoup instance"
            filtedContents.append(singleContent)

    # print "filterd contents=",filtedContents
    # logging.debug("[%d] before return, filtedContents=%s", gVal['currentLevel'], filtedContents)

    return filtedContents


def soupContentsToUnicode(soupContents):
    """convert soup contents into unicode string"""
    # method 1
    mappedContents = map(CData, soupContents)
    # print "mappedContents OK"
    # print "type(mappedContents)=",type(mappedContents) #type(mappedContents)= <type 'list'>
    contentUni = ''.join(mappedContents)
    # print "contentUni=",contentUni

    # #method 2
    # originBlogContent = ""
    # logging.debug("Total %d contents for original soup contents:", len(soupContents))
    # for i, content in enumerate(soupContents):
    # if(content):
    # logging.debug("[%d]=%s", i, content)
    # originBlogContent += unicode(content)
    # else :
    # logging.debug("[%d] is null", i)

    # logging.debug("---method 1: map and join---\n%s", contentUni)
    # logging.debug("---method 2: enumerate   ---\n%s", originBlogContent)

    # # -->> seem that two method got same blog content

    # logging.debug("soup contents to unicode string OK")
    return contentUni


def findFirstNavigableString(soupContents):
    """find the first BeautifulSoup.NavigableString from soup contents"""
    firstString = None
    for eachContent in soupContents:
        # note here must import NavigableString from BeautifulSoup
        if (isinstance(eachContent, NavigableString)):
            firstString = eachContent
            break

    return firstString

#-------------------------------------------------------------------------------
# bs4 = BeautifulSoup v4
#-------------------------------------------------------------------------------

def xmlToSoup(xmlStr):
    """convert to xml string to soup
        Note: xml is tag case sensitive -> retain tag upper case -> NOT convert tag to lowercase

    Args:
        xmlStr (str): xml str, normally page source
    Returns:
        soup
    Raises:
    """
    # HtmlParser = 'html.parser'
    # XmlParser = 'xml'
    XmlParser = 'lxml-xml'
    curParser = XmlParser
    soup = BeautifulSoup(xmlStr, curParser)
    return soup


def bsChainFind(curLevelSoup, queryChainList):
    """BeautifulSoup find with query chain

    Args:
        curLevelSoup (soup): BeautifulSoup
        queryChainList (list): str list of all level query dict
    Returns:
        soup
    Raises:
    Examples:
        input: 
            [
                {
                    "tag": "XCUIElementTypeWindow",
                    "attrs": {"visible":"true", "enabled":"true", "width": "%s" % ScreenX, "height": "%s" % ScreenY}
                },
                {
                    "tag": "XCUIElementTypeButton",
                    "attrs": {"visible":"true", "enabled":"true", "width": "%s" % ScreenX, "height": "%s" % ScreenY}
                },
                {
                    "tag": "XCUIElementTypeStaticText",
                    "attrs": {"visible":"true", "enabled":"true", "value":"可能离开微信，打开第三方应用"}
                },
            ]
        output:
            soup node of 
                <XCUIElementTypeStaticText type="XCUIElementTypeStaticText" value="可能离开微信，打开第三方应用" name="可能离开微信，打开第三方应用" label="可能离开微信，打开第三方应用" enabled="true" visible="true" x="71" y="331" width="272" height="18"/>
                in :
                <XCUIElementTypeWindow type="XCUIElementTypeWindow" enabled="true" visible="true" x="0" y="0" width="414" height="736">
                    <XCUIElementTypeOther type="XCUIElementTypeOther" enabled="true" visible="true" x="0" y="0" width="414" height="736">
                        <XCUIElementTypeOther type="XCUIElementTypeOther" enabled="true" visible="true" x="0" y="0" width="414" height="736">
                            <XCUIElementTypeOther type="XCUIElementTypeOther" enabled="true" visible="true" x="0" y="0" width="414" height="736">
                                <XCUIElementTypeButton type="XCUIElementTypeButton" enabled="true" visible="true" x="0" y="0" width="414" height="736">
                                    <XCUIElementTypeStaticText type="XCUIElementTypeStaticText" enabled="true" visible="false" x="47" y="288" width="0" height="0"/>
                                    <XCUIElementTypeStaticText type="XCUIElementTypeStaticText" value="可能离开微信，打开第三方应用" name="可能离开微信，打开第三方应用" label="可能离开微信，打开第三方应用" enabled="true" visible="true" x="71" y="331" width="272" height="18"/>
                                    <XCUIElementTypeStaticText type="XCUIElementTypeStaticText" value="取消" name="取消" label="取消" enabled="true" visible="true" x="109" y="409" width="36" height="22"/>
                                    <XCUIElementTypeStaticText type="XCUIElementTypeStaticText" value="继续" name="继续" label="继续" enabled="true" visible="true" x="269" y="409" width="36" height="22"/>
                                </XCUIElementTypeButton>
                            </XCUIElementTypeOther>
                        </XCUIElementTypeOther>
                    </XCUIElementTypeOther>
                </XCUIElementTypeWindow>
    """
    foundSoup = None
    if queryChainList:
        chainListLen = len(queryChainList)

        if chainListLen == 1:
            # last one
            curLevelFindDict = queryChainList[0]
            curTag = curLevelFindDict["tag"]
            curAttrs = curLevelFindDict["attrs"]
            foundSoup = curLevelSoup.find(curTag, attrs=curAttrs)
        else:
            highestLevelFindDict = queryChainList[0]
            curTag = highestLevelFindDict["tag"]
            curAttrs = highestLevelFindDict["attrs"]
            foundSoupList = curLevelSoup.find_all(curTag, attrs=curAttrs)
            if foundSoupList:
                childrenChainList = queryChainList[1:]
                for eachSoup in foundSoupList:
                    eachSoupResult = bsChainFind(eachSoup, childrenChainList)
                    if eachSoupResult:
                        foundSoup = eachSoupResult
                        break

    return foundSoup

################################################################################
# Test
################################################################################



if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))