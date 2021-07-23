#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanGame.py
Function: crifanLib's python game related functions
Version: 20210723
Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/crifanGame.py
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20210723"
__copyright__ = "Copyright (c) 2021, Crifan Li"
__license__ = "GPL"


import copy

from .thirdParty.crifanPlaywright import initBrowser, getGoogleSearchResult

################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################

CURRENT_LIB_FILENAME = "crifanGame"

################################################################################
# Definition
################################################################################

# for calc game theme and game play

gGameThemeDictList = [
    {
        "name": "仙侠",
        "optionList": ["仙侠", "修仙"]
    },
    {
        "name": "传奇",
        "optionList": ["传奇"]
    },
    {
        "name": "魔幻",
        "optionList": ["魔幻", "魔法"]
    },
    {
        "name": "三国",
        "optionList": ["三国"]
    },
    {
        "name": "二次元",
        "optionList": ["二次元"]
    },
    {
        "name": "武侠",
        "optionList": ["武侠"]
    },
    {
        "name": "战争",
        "optionList": ["战争"]
    },
    {
        "name": "战国",
        "optionList": ["战国"]
    },
    {
        "name": "漫改",
        "optionList": ["漫改"]
    },
    {
        "name": "末日",
        "optionList": ["末日", "废土"]
    },
    {
        "name": "中国神话",
        "optionList": ["中国神话"]
    },
    {
        "name": "古风",
        "optionList": ["古风", "宫廷", "国风"]
    },
    {
        "name": "西游",
        "optionList": ["西游"]
    },
    {
        "name": "体育",
        "optionList": ["体育"]
    },
    {
        "name": "科幻",
        "optionList": ["科幻"]
    },
    {
        "name": "现代",
        "optionList": ["现代"]
    },
    # {
    #     "name": "其他",
    #     "optionList": ["其他"]
    # },
]


gGamePlayDictList = [
    {
        "name": "动作",
        "optionList": ["动作", "ARPG"]
    },
    {
        "name": "角色扮演",
        "optionList": ["角色扮演", "RPG"]
    },
    {
        "name": "策略",
        "optionList": ["策略", "SLG"]
    },
    {
        "name": "卡牌",
        "optionList": ["卡牌"]
    },
    {
        "name": "网赚",
        "optionList": ["网赚"]
    },
    {
        "name": "放置",
        "optionList": ["放置"]
    },
    {
        "name": "经营",
        "optionList": ["经营"]
    },
    {
        "name": "回合制",
        "optionList": ["回合制"]
    },
    {
        "name": "塔防",
        "optionList": ["塔防"]
    },
    {
        "name": "乙女",
        "optionList": ["乙女", "女性向恋爱养成", "恋爱养成"]
    },
    {
        "name": "捕鱼",
        "optionList": ["捕鱼"]
    },
    {
        "name": "益智",
        "optionList": ["益智", "消除"]
    },
    {
        "name": "射击",
        "optionList": ["射击"]
    },
    {
        "name": "文字",
        "optionList": ["文字"]
    },
    # {
    #     "name": "其他",
    #     "optionList": ["其他"]
    # },
]

################################################################################
# Global Variable
################################################################################

################################################################################
# Internal Function
################################################################################


################################################################################
# Game Function
################################################################################

def calcGameThemeOrPlay(descStr, gameThemeOrPlayDictList):
    """
    Calc game theme or game play from input description string

    Args:
        descStr (str): (google serch return single result item) descripton string 
        gameThemeOrPlayDictList (list): game theme or game play dict list
    Returns:
        gameTheme or gamePlay(str)
    Raises:
    """
    curThemeOrPlay = ""

    resultDictList = copy.deepcopy(gameThemeOrPlayDictList)

    arpgCount = 0

    for eachItemDict in resultDictList:
        # eachItemName = eachItemDict["name"]
        eachItemOptionList = eachItemDict["optionList"]
        allOptionCount = 0
        for eachOption in eachItemOptionList:
            curOptionCount = descStr.count(eachOption)

            # # for debug
            # if curOptionCount > 0:
            #     print("Found %s %s" % (curOptionCount, eachOption))
            #     print()

            # Specal: 要把 RPG的个数 减去 ARPG的个数，才是真正的 RPG的个数
            if eachOption == "ARPG":
                arpgCount = curOptionCount

                # # for debug
                # if arpgCount > 0:
                #     print("found ARPG count: %s" % arpgCount)
                #     print()

            elif eachOption == "RPG":
                # # for debug
                # if curOptionCount > 0:
                #     print("fake RPG count: %s" % curOptionCount)
                #     print()

                curOptionCount -= arpgCount

                # # for debug
                # if curOptionCount > 0:
                #     print("real RPG count: %s" % curOptionCount)
                #     print()

            allOptionCount += curOptionCount

        eachItemDict['showCount'] = allOptionCount

    # sortedResultDictList = sorted(resultDictList.items(), key=lambda item: item["showCount"])
    sortedResultDictList = sorted(resultDictList, key=lambda item: item["showCount"], reverse=True)
    # print("sortedResultDictList=%s" % sortedResultDictList)

    # hasShowCountList = filter(lambda resultItem:resultItem["showCount"] > 0, sortedResultDictList)
    hasShowCountResultDictFiltered = filter(lambda resultItem:resultItem["showCount"] > 0, sortedResultDictList)
    hasShowCountList = list(hasShowCountResultDictFiltered)
    print("hasShowCountList=%s" % hasShowCountList)

    if hasShowCountList:
        highestCountDict = hasShowCountList[0]
        if highestCountDict["showCount"] > 0:
            curThemeOrPlay = highestCountDict["name"]

    # print("curThemeOrPlay=%s" % curThemeOrPlay)
    return curThemeOrPlay

def generateGameThemePlay(gameName, searchFunc, extraBrowserParaDict={}):
    """
    Generate game theme and game play from game name

    Args:
        gameName (str): game name
        searchFunc (Function): search function. Normally is use playwright/... to emulate google search
        extraBrowserParaDict (dict): extra browser parameter dict. Default is {}.
    Returns:
        gameTheme, gamePlay (tuple)
    Raises:
    Examples:
        白夜琉璃 -> 仙侠, 角色扮演
    """
    print("gameName=%s" % gameName) # game_name=迷你世界

    gameThemeSearchStr = '游戏题材 %s' % gameName
    # resultDictList = getGoogleSearchResult(gameThemeSearchStr, **extraBrowserParaDict)
    resultDictList = searchFunc(gameThemeSearchStr, **extraBrowserParaDict)
    resultNum = len(resultDictList)
    print("Google search '%s' found %s result" % (gameThemeSearchStr, resultNum))

    allDescStrList = []
    for eachResultDict in resultDictList:
        curDescStr = eachResultDict["description"]
        allDescStrList.append(curDescStr)

    allDescStr = "\n".join(allDescStrList)
    # print("allDescStr=%s" % allDescStr)

    curGameTheme = calcGameThemeOrPlay(allDescStr, gGameThemeDictList)
    # print("curGameTheme=%s" % curGameTheme)
    curGamePlay = calcGameThemeOrPlay(allDescStr, gGamePlayDictList)
    # print("curGamePlay=%s" % curGamePlay)

    return curGameTheme, curGamePlay

################################################################################
# Test
################################################################################

if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))

    # parse game theme from game name

    PROXY_HTTP = "http://127.0.0.1:58591"
    browserConfig = {
        "headless": False,
        # "headless": True,
        "proxy": {
            "server": PROXY_HTTP,
        }
    }
    gPlaywrightBrowser = initBrowser(browserConfig=browserConfig)

    realGameName = "白夜琉璃"

    extraBrowserParaDict = {"browser": gPlaywrightBrowser}
    googleSearchFunc = getGoogleSearchResult
    calcedGameTheme, calcedGamePlay = generateGameThemePlay(realGameName, googleSearchFunc, extraBrowserParaDict)
    # logging.info("calcedGameTheme=%s, calcedGamePlay=%s", calcedGameTheme, calcedGamePlay)
