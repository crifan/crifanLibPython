# Functon: Crifan's facebook-wda wrapper common functions
# Author: Crifan Li
# Update: 20200615

import os
import sys
import time
import logging

from PIL import Image, ImageDraw

import wda
from wda import ScreenshotQuality

# not following import need update according to actual crifan lib
from . import utils
from . import crifanLogging
from . import appCrawlerCommon

################################################################################
# Const
################################################################################

WdaServerPort = 8100
# WdaServerHost = "localhost" # for iOS Simulator
# WdaServerHost = "192.168.31.43" # for iOS real device: iPhone 6
# WdaServerHost = "192.168.31.44" # for iOS real device: iPhone 6
# WdaServerHost = "192.168.31.228" # for iOS real device: iPhone 6 Plus
# WdaServerHost = "192.168.31.229" # for iOS real device: iPhone 6 Plus

# WdaServerHost = "192.168.31.57" # for iOS real device: iPhone 8 Plus
WdaServerHost = "localhost" # for iOS real device: iPhone 8 Plus + (iproxy/mobiledevice) local port forwarding


# cfgSnapshotTimeout = 65 # to avoid: Cannot take the snapshot of Window after 15 seconds
cfgSnapshotTimeout = 300 # to avoid: Cannot take the snapshot of Window after 15 seconds
cfgScreenQuality = ScreenshotQuality.Low.value # 2, to further reduce screenshot jpg size
cfgScalingFactor = 50 # scale down to origin screen size

# cfgIncludeNonModalElements = True
cfgIncludeNonModalElements = False

# cfgShouldUseCompactResponses = True
cfgShouldUseCompactResponses = False

# cfgElementResponseAttributes = "type,label"
# cfgElementResponseAttributes = "type,label,name,text,rect,attribute/name,attribute/value"
# cfgElementResponseAttributes = "type,label,name,text,rect,visible,accessible,attribute/name,attribute/value"
cfgElementResponseAttributes = "type,label,name,text,rect,attribute/name,attribute/value,attribute/visible,attribute/accessible,"
# cfgElementResponseAttributes = "type,label,name,text,rect"

# cfgPageChangeWaitSecond = 0.5
cfgPageChangeWaitSecond = 0.2

cfgFindElementTimeout = 5.0 # find elemenmt timeout, for current 5.0 seconds is large enough, if not existed, given more time, still can not found
# cfgWdaHttpTimeout = 60.0
cfgWdaHttpTimeout = 6000.0 # for XCode breakpoint debug
cfgWdaDebug = True # Enable debug will see http Request and Response
# cfgWdaDebug = False

################################################################################
# Global Variable
################################################################################

gCurAppId = None
gServerUrl = None
gWdaClient = None
gCurSession = None

# DebugWeixinFolder = "debug/iPhone_6/微信"
# DebugSaveFolder = "debug/iPhone8P"
# DebugSaveFolder = "debug/iPhone_Real"
# DebugSaveFolder = "debug/iPhone_Real/app"
CurrentFile = os.path.abspath(__file__) # '/Users/limao/dev/xxx/crawler/appAutoCrawler/AppCrawler/iOSAutomation/wdaTest/libs/crifanWda.py'
WdaTestLibsFolder = os.path.dirname(CurrentFile) # '/Users/limao/dev/xxx/crawler/appAutoCrawler/AppCrawler/iOSAutomation/wdaTest/libs'
WdaTestFolder = os.path.dirname(WdaTestLibsFolder) # '/Users/limao/dev/xxx/crawler/appAutoCrawler/AppCrawler/iOSAutomation/wdaTest'
iOSAutomationFolder = os.path.dirname(WdaTestFolder) # '/Users/limao/dev/xxx/crawler/appAutoCrawler/AppCrawler/iOSAutomation'

# DebugSaveFolder = "debug/iPhone_Real/app"
DebugSaveFolder = os.path.join(iOSAutomationFolder, "debug", "iPhone_Real", "app") # '/Users/limao/dev/xxx/crawler/appAutoCrawler/AppCrawler/iOSAutomation/debug/iPhone_Real/app'

# gCurDeubgFolder = ""
# gCurDeubgFolder = DebugWeixinFolder
gCurDeubgFolder = DebugSaveFolder

# gDebugScreenshotRootFolder = os.path.join(gCurDeubgFolder, "screenshot") # '/Users/limao/dev/xxx/crawler/appAutoCrawler/AppCrawler/iOSAutomation/wdaTest/debug/iPhone_Real/app/screenshot'
# gDebugSourceRootFolder = os.path.join(gCurDeubgFolder, "source") # '/Users/limao/dev/xxx/crawler/appAutoCrawler/AppCrawler/iOSAutomation/wdaTest/debug/iPhone_Real/app/source'

################################################################################
# facebook-wda Function
################################################################################


def saveScreenshot(wdaClient, filePrefix="", imageFormat="jpg", saveFolder=""):
    """
        do screehsot for ios device and saved to jpg
            same screenshot image file size compare:
                png: 734KB
                jpg: 100KB
            so better to use jpg
    """
    savedScreenFile = None

    curDatetimeStr = utils.getCurDatetimeStr()
    # screenFilename = "%s_screen.%s" % (curDatetimeStr, imageFormat)
    screenFilename = "%s.%s" % (curDatetimeStr, imageFormat)
    if filePrefix:
        screenFilename = "%s_%s" % (filePrefix, screenFilename)
        # 'com.netease.cloudmusic_20200221_170305.jpg'
    screenFilename = os.path.join(saveFolder, screenFilename)

    if imageFormat == "png":
        curPillowObj = wdaClient.screenshot(png_filename=screenFilename)
        savedScreenFile = screenFilename
    elif (imageFormat == "jpg") or (imageFormat == "jpeg"):
        curPillowObj = wdaClient.screenshot()
        # logging.debug("curPillowObj=%s", curPillowObj)
        # curPillowObj=<PIL.PngImagePlugin.PngImageFile image mode=RGB size=750x1334 at 0x10F6CEE80>
        # convert to PIL.Image and then save as jpg
        curPillowObj.save(screenFilename)
        savedScreenFile = screenFilename
    else:
        logging.debug("Unsupported image format: %s", imageFormat)

    if savedScreenFile:
        logging.debug("saved screenshot: %s", savedScreenFile)
    return savedScreenFile

def getPageSource(wdaClient, sourceFormat="xml"):
    """Get current page source of xml/json

    Args:
        wdaClient (Client): wda client
        sourceFormat (str): source format: xml/json
    Returns:
        str
    Raises:
    """
    pageSource = ""

    utils.calcTimeStart("getPageSource")
    if sourceFormat == "xml":
        curPageXml = wdaClient.source() # format XML
        pageSource = curPageXml
    elif sourceFormat == "json":
        curPageJson = wdaClient.source(accessible=True) # default false, format JSON
        pageSource = curPageJson
    else:
        logging.error("Unsupported source format: %s", sourceFormat)
    getSourceTime = utils.calcTimeEnd("getPageSource")
    logging.info("Cost %.2f seconds to get source source", getSourceTime)

    return pageSource

def saveSource(wdaClient, filePrefix="", sourceFormat="xml", saveFolder=""):
    """save current page source"""
    savedSourceFile = None

    curDatetimeStr = utils.getCurDatetimeStr()
    # sourceFilename = "%s_source.%s" % (curDatetimeStr, sourceFormat) # '20200221_152817_source.xml'
    sourceFilename = "%s.%s" % (curDatetimeStr, sourceFormat)
    if filePrefix:
        sourceFilename = "%s_%s" % (filePrefix, sourceFilename)
        # 'com.netease.cloudmusic_20200221_170337.xml'
    sourceFilename = os.path.join(saveFolder, sourceFilename)

    pageSource = getPageSource(wdaClient, sourceFormat=sourceFormat)
    utils.saveTextToFile(sourceFilename, pageSource)
    savedSourceFile = sourceFilename

    # if sourceFormat == "xml":
    #     curPageXml = wdaClient.source() # format XML
    #     # logging.debug("curPageXml=%s", curPageXml)
    #     utils.saveTextToFile(sourceFilename, curPageXml)
    #     savedSourceFile = sourceFilename
    # elif sourceFormat == "json":
    #     curPageJson = wdaClient.source(accessible=True) # default false, format JSON
    #     # logging.debug("curPageJson=%s", curPageJson)
    #     utils.saveJsonToFile(sourceFilename, curPageJson)
    #     savedSourceFile = sourceFilename
    # else:
    #     logging.debug("Unsupported source format: %s", sourceFormat)

    logging.debug("saved page source: %s", savedSourceFile)
    return savedSourceFile

def scaleToOrginSize(screenshotImgPath, curScale):
    """resize to original screen size, according to session scale"""
    curScreenImg = Image.open(screenshotImgPath)
    originSize = curScreenImg.size # 750x1334
    newWidthInt = int(float(originSize[0]) / curScale)
    newHeightInt = int(float(originSize[1]) / curScale)
    scaledSize = (newWidthInt, newHeightInt) # 375x667
    scaledFile = screenshotImgPath
    utils.resizeImage(curScreenImg, newSize=scaledSize, outputImageFile=scaledFile)
    return scaledFile

def findElement(curSession, query={}, timeout=cfgFindElementTimeout):
    """Find element from query

    Args:
        curSession (Session): current session
        query (dict): query condition
    Returns:
        bool, Element/str
            True, Element
            False, error message
    Raises:
    """
    logging.debug("query=%s", query)
    isFound, respInfo = False, "Unkown error"

    # # preproces rect
    # rectKeyList = ["x", "y", "width", "height"]
    # rectDict = {}
    # for eachRectKey in rectKeyList:
    #     if eachRectKey in query.keys():
    #         eachRectValue = query[eachRectKey]
    #         eachRectValueInt = int(eachRectValue)
    #         rectDict[eachRectKey] = eachRectValueInt
    #         del query[eachRectKey]
    # if rectDict:
    #     query["rect"] = rectDict

    # isFound, respInfo = curSession(**query, timeout=timeout).get()
    elementSelector = curSession(**query, timeout=timeout)
    logging.debug("elementSelector=%s", elementSelector)
    isFound, respInfo = elementSelector.get()
    logging.debug("query=%s -> isFound=%s, respInfo=%s", query, isFound, respInfo)
    return isFound, respInfo

def clickElement(curSession, curElement, resetAfterClick=True, wait=cfgPageChangeWaitSecond):
    """Click Element
            is visible=true, direct call tap
            if visible=false, invisiable, try to tap center position

    Args:
        curSession (Session): current session
        curElement (Element): wda Element
        resetAfterClick (bool): reset element after click
            for most case click cause page changed, element can not found
            so reset to avoid later debug will try get its attributes, but not found, so cause error
        wait(float): after click wait some seconds (for reload to new page)
    Returns:
    Raises:
    """
    clickOk = False
    if curElement.visible:
        curElement.tap()
        logging.debug("taped element: %s", curElement)
        clickOk = True
    else:
        curRect = curElement.bounds
        rectCenter = curRect.center
        centerX = rectCenter[0]
        centerY = rectCenter[1]
        curSession.click(centerX, centerY)
        clickOk = True
        logging.debug("clicked element position: %s,%s", centerX, centerY)
    
    if resetAfterClick:
        logging.info("now reset element after click %s", curElement)
        curElement = None

    # sleep sometime to wait for change to new page
    logging.debug("sleep %s seconds after click", wait)
    time.sleep(wait)

    return clickOk

def findAndClickElement(curSession, query={}, timeout=cfgFindElementTimeout, enableDebug=False):
    """Find and click element

    Args:
        curSession (Session): current session
        query (dict): query parameter for find element
        timeout (float): max timeout seconds for find element
        enableDebug (bool): if enable debug, then draw clicked rectange for current screen
    Returns:
        bool
    Raises:
    """
    foundAnClicked = False

    isFound, respInfo = findElement(curSession, query=query, timeout=timeout)
    logging.debug("isFound=%s, respInfo=%s", isFound, respInfo)
    if isFound:
        curElement = respInfo

        if enableDebug:
            # for debug
            curScreenFile = debugSaveScreenshot(curScale=curSession.scale)
            utils.imageDrawRectangle(curScreenFile, rectLocation=curElement.bounds)

        clickElement(curSession, curElement)
        logging.info("Clicked element %s", query)

        foundAnClicked = True
    else:
        logging.error("Not found element %s", query)

    return foundAnClicked

def findAndClickButtonElementBySoup(curSession, curButtonSoup=None, curButtonName=None):
    """
        iOS的bug：根据bs找到了soup元素（往往是一个button）后，用 clickCenterPosition=clickElementCenterPosition 去点击中间坐标，往往会有问题
            实际上点击的是别的位置，别的元素
        为了规避此bug，所以去：
            通过soup，再去找button的wda的元素，然后根据元素去点击
                则都是可以正常点击，不会有误点击的问题
    """
    curButtonQuery = {"type":"XCUIElementTypeButton", "enabled":"true"}
    extraQuery = {}

    # change to wda element query then click by element
    if curButtonName:
        extraQuery["name"] = curButtonName
    else:
        if curButtonSoup:
            curSoupAttrs = curButtonSoup.attrs
            if hasattr(curSoupAttrs, "name"):
                curButtonName = curSoupAttrs["name"]
                # rights close white
                # login close
                extraQuery["name"] = curButtonName
            else:
                # no name attribute, use position
                x = curSoupAttrs["x"]
                y = curSoupAttrs["y"]
                width = curSoupAttrs["width"]
                height = curSoupAttrs["height"]
                extraQuery["x"] = x
                extraQuery["y"] = y
                extraQuery["width"] = width
                extraQuery["height"] = height
                # {'enabled': 'true', 'height': '32', 'type': 'XCUIElementTypeButton', 'width': '31', 'x': '339', 'y': '122'}

    # merge query 
    # curButtonQuery = {**curButtonQuery, **extraQuery}
    curButtonQuery.update(extraQuery)

    foundAndClicked = findAndClickElement(curSession, curButtonQuery)
    return foundAndClicked

def findAndClickCenterPosition(curSession, bsChainList, isUseWdaQueryAndClick=False):
    """use Beautifulsoup chain list to find soup node then click node center position

    Args:
        bsChainList (list): dict list for dict of tag and attrs
        isUseWdaQueryAndClick (bool): for special node bs click not work, so need change to wda query element then click by element
    Returns:
        bool: found and cliked or not
    Raises:
    """
    foundAndClicked = False
    curPageXml = getPageSource(gWdaClient)
    soup = utils.xmlToSoup(curPageXml)
    foundSoup = utils.bsChainFind(soup, bsChainList)
    if foundSoup:
        if isUseWdaQueryAndClick:
            foundAndClicked = findAndClickButtonElementBySoup(curSession, foundSoup)
        else:
            appCrawlerCommon.clickCenterPosition(curSession, foundSoup.attrs)
            foundAndClicked = True

    return foundAndClicked

############################### Debug Function ###############################

def debugSaveSource(sourceFormat="xml"):
    global gWdaClient, gCurAppId
    """add debug info for save source"""
    utils.calcTimeStart("saveSource")
    # savedSourceFile = saveSource(gWdaClient, gCurAppId, saveFolder=gCurDeubgFolder)
    savedSourceFile = saveSource(gWdaClient, gCurAppId, sourceFormat=sourceFormat, saveFolder=gCurDeubgFolder)
    # savedSourceFile = saveSource(gWdaClient, sourceFormat=sourceFormat, saveFolder=gDebugSourceRootFolder)
    # savedSourceFile = saveSource(gWdaClient, sourceFormat=sourceFormat, saveFolder=gCurDeubgFolder)
    saveSourceTime = utils.calcTimeEnd("saveSource")
    logging.debug("Cost time %.2fs for save source %s", saveSourceTime, savedSourceFile)

def debugSaveScreenshot(isResizeToOriginal=True, curScale=2.0):
    """add debug info for save screenshot"""
    global gWdaClient, gCurAppId

    # for if enable debug screenshot image content too long
    # so disable debug screenshot
    needEnableLater = False
    if wda.DEBUG:
        wda.DEBUG = False
        needEnableLater = True

    utils.calcTimeStart("saveScreenshot")
    savedImgFile = saveScreenshot(gWdaClient, gCurAppId, saveFolder=gCurDeubgFolder)
    # savedImgFile = saveScreenshot(gWdaClient, saveFolder=gDebugScreenshotRootFolder)
    # savedImgFile = saveScreenshot(gWdaClient, saveFolder=gCurDeubgFolder)
    saveScreenshotTime = utils.calcTimeEnd("saveScreenshot")

    if needEnableLater:
        wda.DEBUG = True

    logging.debug("Cost time %.2fs for save screenshot %s", saveScreenshotTime, savedImgFile)
    if isResizeToOriginal:
        # and resize to original screen size
        savedImgFile = scaleToOrginSize(savedImgFile, curScale)
    return savedImgFile

def initSessionSettings(curSession):
    curSettings = curSession.get_settings()
    logging.debug("curSettings=%s", curSettings)

    # newSnapshotTimeout = 65
    # respNewSettings = curSession.setSnapshotTimeout(newSnapshotTimeout)
    # logging.debug("respNewSettings=%s", respNewSettings)

    # debugSaveScreenshot(isResizeToOriginal=False)

    # respNewSettings = curSession.set_settings({"": ScreenshotQuality.Original.value})
    # logging.debug("respNewSettings=%s", respNewSettings)
    # debugSaveScreenshot(isResizeToOriginal=False)

    # respNewSettings = curSession.set_settings({"screenshotQuality": ScreenshotQuality.Low.value})
    # logging.debug("respNewSettings=%s", respNewSettings)
    # debugSaveScreenshot(isResizeToOriginal=False)

    newSettings = {
        "snapshotTimeout": cfgSnapshotTimeout,
        "screenshotQuality": cfgScreenQuality,
        "mjpecfgScalingFactor": cfgScalingFactor,
        "includeNonModalElements": cfgIncludeNonModalElements,
        "shouldUseCompactResponses": cfgShouldUseCompactResponses,
        "elementResponseAttributes": cfgElementResponseAttributes,

        # "useJSONSource": True,
        # "simpleIsVisibleCheck": True,
    }
    respNewSettings = curSession.set_settings(newSettings)
    logging.debug("respNewSettings=%s", respNewSettings)
    # debugSaveScreenshot(isResizeToOriginal=False)
    # debugSaveScreenshot()
    # debugSaveSource()

def getCurAppId():
    global gWdaClient
    curAppInfo = gWdaClient.app_current()
    logging.debug("curAppInfo=%s", curAppInfo)
    # curAppInfo={'processArguments': {'env': {}, 'args': []}, 'name': '', 'pid': 15235, 'bundleId': 'com.apple.springboard'}
    # curAppInfo={'running': True, 'state': 4, 'generation': 0, 'processArguments': {'env': {}, 'args': []}, 'title': '', 'bundleId': 'com.fenbi.ape.zebstrika', 'label': '斑马AI课', 'path': '', 'name': '', 'pid': 7511}
    if curAppInfo:
        if "bundleId" in curAppInfo:
            curAppId = curAppInfo["bundleId"] # com.fenbi.ape.zebstrika
    return curAppId

def getCurSession(isForceRestartApp=False, newAppId=None):
    global gWdaClient
    if isForceRestartApp:
        # force re-start some iOS app
        curSession = gWdaClient.session(newAppId)
    else:
        # not force start app, keep current screen
        curSession = gWdaClient
    return curSession

def initSessionScale(curSession):
    needEnableLater = False
    if wda.DEBUG:
        wda.DEBUG = False
        needEnableLater = True

    # init session internally init scale
    # which will do screenshot
    # if enable debug -> screenshot image content too long
    # so disable debug screenshot temp then restore origin value

    # just get once = init for later directly use
    logging.info("curSession.scale=%s", curSession.scale)

    if needEnableLater:
        wda.DEBUG = True


def wdaInit():
    global gServerUrl, gWdaClient, gCurAppId, gCurSession

    wda.HTTP_TIMEOUT = cfgWdaHttpTimeout
    wda.DEBUG = cfgWdaDebug

    # gWdaClient = wda.Client('http://localhost:8100')
    gServerUrl = 'http://%s:%s' % (WdaServerHost, WdaServerPort)
    logging.info("gServerUrl=%s", gServerUrl)
    gWdaClient = wda.Client(gServerUrl)
    logging.info("gWdaClient=%s", gWdaClient)
    gCurAppId = getCurAppId()
    logging.info("gCurAppId=%s", gCurAppId)
    gCurSession = getCurSession()
    logging.info("gCurSession=%s", gCurSession)

    initSessionSettings(gCurSession)

    initSessionScale(gCurSession)
