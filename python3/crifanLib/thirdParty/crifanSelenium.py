#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanSelenium.py
Function: crifanLib's Selenium related functions
Version: 20210813
Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/thirdParty/crifanSelenium.py
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20210813"
__copyright__ = "Copyright (c) 2021, Crifan Li"
__license__ = "GPL"

# # isUseSeleniumwire = False
# isUseSeleniumwire = True

# if isUseSeleniumwire:
#     from seleniumwire import webdriver # Support capture http request and response
# else:
#     from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException, NoSuchElementException

# for debug
import logging
import re

################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanSelenium"

################################################################################
# Global Variable
################################################################################
gVal = {

}

gConst = {
}

################################################################################
# Function
################################################################################

def getWebDirver(isUseSeleniumwire=False):
    """Init selenium webdriver

    Args:
        isUseSeleniumwire (bool): get selenium-wire webdriver or not. Default is False.
    Returns:
        driver
    Raises:
    Examples:
    """
    if isUseSeleniumwire:
        from seleniumwire import webdriver # Support capture http request and response
    else:
        from selenium import webdriver

    return webdriver

def initBrowser(browserConfig, isUseSeleniumwire=False):
    """Init browser driver for selenium

    Args:
        browserConfig (dict): browser config
        isUseSeleniumwire (bool): get selenium-wire webdriver or not. Default is False.
    Returns:
        driver
    Raises:
    Examples:
        browserConfig
            normal Selenium: {'headless': True, 'pageLoadTimeout': 10}
            Selenium-wire: {'headless': True, 'pageLoadTimeout': 10, "seleniumwire": {"disable_capture":True}}
    """
    webdriver = getWebDirver(isUseSeleniumwire=isUseSeleniumwire)
    chromeOptions = webdriver.ChromeOptions()

    if "headless" in browserConfig:
        isCurHeadless = browserConfig["headless"]
        if isCurHeadless:
            chromeOptions.add_argument('--headless')

    if "disableGpu" in browserConfig:
        isDisableGpu = browserConfig["disableGpu"]
        if isDisableGpu:
            chromeOptions.add_argument('--disable-gpu')

    # for debug
    # chromeOptions.add_experimental_option("excludeSwitches", ["enable-automation"])
    # chromeOptions.add_experimental_option('useAutomationExtension', False)
    # chromeOptions.add_argument('window-size=1920x1080')
    # chromeOptions.add_argument('--window-size=1920x1080')

    driverConfigDict = {
        "options": chromeOptions
    }

    if "seleniumwire" in browserConfig:
        if isUseSeleniumwire:
            driverConfigDict["seleniumwire_options"] = browserConfig["seleniumwire"]
        else:
            del browserConfig["seleniumwire"]

    driver = webdriver.Chrome(**driverConfigDict)
    # driver = webdriver.Chrome(options=chromeOptions)

    # # for debug
    # driver.set_window_size(1920, 1080)

    if "pageLoadTimeout" in browserConfig:
        curPageLoadTimeout = browserConfig["pageLoadTimeout"]
        driver.set_page_load_timeout(curPageLoadTimeout)

    return driver

def closeBrowser(driver):
    """
    For Selenium, close browser driver

    Args:
        driver (driver): Selenium browser driver
    Returns:
    Raises:
    """
    driver.quit()

def parseUrl(inputUrl, driver=None):
    """Parse (redirected final long) url, title, html from input (possible short link) url

    Args:
        inputUrl (dict): input original (short link) url
        driver (WebDriver): selenium web driver. Default is None. If None, create a new one.
    Returns:
        parse result(dict)
    Raises:
    Examples:
        http://4g3.cn/GmPwE -> 
            https://zhongan.tiancaibaoxian.com/za/npb?cid=B2874&mobile=18297013235
            众安百万医疗险(升级版)
            <!DOCTYPE html>
                <html lang="en">

                <head>
                    <meta charset="UTF-8">
                    <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0" name="viewport" />
                    <title>众安百万医疗险(升级版)</title>
                ...
                    </script>
                    </body>
            </html>
    """
    if not driver:
        # webdriver = getWebDirver()
        # driver = webdriver.Chrome()
        driver = initBrowser()

    respValue = None

    try:
        driver.get(inputUrl)

        finalUrl = driver.current_url
        logging.debug("finalUrl=%s", finalUrl)

        finalTitle = driver.title
        # '春节提现服'
        # '三维推关于短网址_二维码_多场景应用过期使用提醒'
        # '极品传奇'
        logging.debug("finalTitle=%s", finalTitle)

        finalHtml = driver.page_source
        # logging.info("finalHtml=%s", finalHtml)

        respValue = {
            "isParseOk": True,
            "url": finalUrl,
            "title": finalTitle,
            "html": finalHtml,
        }
    except Exception as e:
        errStr = str(e)
        # 'Message: unknown error: net::ERR_NAME_NOT_RESOLVED\n  (Session info: chrome=91.0.4472.164)\n'
        logging.debug("selenium parse %s exception: %s", inputUrl, errStr)
        """
        selenium parse http://dmh2.cn/9jaSp0 exception: Message: unknown error: net::ERR_NAME_NOT_RESOLVED
            (Session info: chrome=91.0.4472.164)
        """

        respValue = {
            "isParseOk": False,
            "errMsg": errStr, 
        }

    return respValue

def cleanCapturedRequests(driver):
    """Clean selenium-wire captured requests
        to avoid later, after many get, accumulated too much requests

    Args:
        driver (WebDriver): selenium-wire web driver
    Returns:
    Raises:
    Examples:
    """
    # driver.requests = None
    if hasattr(driver, "requests"):
        del driver.requests

def getText(curElement):
    """
    Get Selenium element text

    Args:
        curElement (WebElement): selenium web element
    Returns:
        str
    Raises:
    """
    # # for debug
    # elementHtml = curElement.get_attribute("innerHTML")
    # print("elementHtml=%s" % elementHtml)

    elementText = curElement.text # sometime NOT work
    # print("get text ok")

    if not elementText:
        elementText = curElement.get_attribute("innerText")
        # print("get_attribute innerText ok")

    if not elementText:
        elementText = curElement.get_attribute("textContent")
        # print("get_attribute textContent ok")

    # print("elementText=%s" % elementText)
    return elementText

def parseBingSearchResult(driver, isIncludeAd=True, log=logging):
    """
    Parse bing search result from current (search result) page

    Args:
        driver (WebDriver): selenium web driver
        isIncludeAd (bool): return result is include ad part or not
        log (logging): log instance. Default is system's logging
    Returns:
        result dict list
    Raises:
    """
    searchResultDictList = []

    # # 获取所有的页面句柄
    # handleList = driver.window_handles
    # log.debug("handleList=%s", handleList)
    # latestHandle = handleList[-1]
    # log.debug("latestHandle=%s", latestHandle)
    # # 切换至当前页面
    # driver.switch_to.window(latestHandle)
    # log.debug("switch to latest window")

    # driver.refresh()

    # <ol id="b_results">
    resultId = "b_results"

    # driver.find_element_by_xpath("//ol[@id='b_results']")

    resultElem = driver.find_element_by_id(resultId)
    log.debug("resultElem=%s", resultElem)
    log.info("resultElem.is_displayed()=%s", resultElem.is_displayed())
    if not resultElem:
        return searchResultDictList

    # allLiXpath = "//li[@class='b_algo' or @starts-with(@class, 'b_ad')]"
    # allLiXpath = '//li[@class="b_algo" or starts-with(@class, "b_ad")]'
    # allLiXpath = "//li[@class='b_algo' or starts-with(@class, 'b_ad')]"
    # resultLiList = resultElem.find_elements_by_xpath(allLiXpath)
    # log.info("resultLiList=%s", resultLiList)
    # resultLiNum = len(resultLiList)
    # log.info("resultLiNum=%s", resultLiNum)

    normlLiXpath = ".//li[@class='b_algo']"
    normalLiList = resultElem.find_elements_by_xpath(normlLiXpath)
    normalLiNum = len(normalLiList)
    log.info("normalLiNum=%s", normalLiNum)

    # normal result item
    """
        <li class="b_algo">
            <h2><a target="_blank" href="http://www.drv5.cn/azgame/77154.html"
                    h="ID=SERP,5143.1"><strong>白夜琉璃</strong>手游下载-<strong>白夜琉璃</strong>手游内测版v1.4.8-第五驱动</a></h2>
            <div class="b_caption">
                <div class="b_attribution" u="0|5124|4545703417479742|AOP9gfi8m1gTJYYm89LkD12SrZYxtwiM">
                    <cite>www.drv5.cn/azgame/77154.html</cite><span class="c_tlbxTrg"><span class="c_tlbxH"
                            h="BASE:CACHEDPAGEDEFAULT" k="SERP,5144.1"></span></span></div>
                <p>2021-5-11 · 白夜琉璃是一款浪漫情缘<strong>题材</strong>的唯美仙侠<strong>游戏</strong>在这个血色的玄幻世界里可以体验到无比精彩的战斗，多样的挑战将给每个玩家带去无比真实的修行体验，让你能够更好的融入到这个修行者的世界，
                    。</p>
            </div>
        </li>
        <li class="b_algo">
            <h2><a target="_blank" href="https://www.lanrentuku.com/shouyou/47585.html"
                    h="ID=SERP,5160.1"><strong>白夜琉璃</strong>手游下载-<strong>白夜琉璃</strong>手游手机安卓版v1.4.8-懒人下载</a></h2>
            <div class="b_caption">
                <div class="b_attribution" u="1|5058|4544492236377359|iCr1uUVRGmUSmPG2Qas_VurCNnMh9v9I">
                    <cite>https://www.lanrentuku.com/shouyou/47585.html</cite><span class="c_tlbxTrg"><span class="c_tlbxH"
                            h="BASE:CACHEDPAGEDEFAULT" k="SERP,5161.1"></span></span></div>
                <p>2021-5-11 · <strong>白夜琉璃</strong>是一款浪漫情缘<strong>题材</strong>的唯美仙侠<strong>游戏</strong>在这个血色的玄幻世界里可以体验到无比精彩的战斗，在不断的磨砺与战斗之中强大自身，让你能够更好的融入到这个修行者的世界，多样的挑战将给每个玩家带去无比真实的修行体验，
                    。</p>
            </div>
        </li>
    """
    for curIdx, eachNormalLi in enumerate(normalLiList):
        log.info("%s [%d] %s", "-"*10, curIdx + 1, "-"*10)
        log.debug("eachNormalLi=%s", eachNormalLi)
        log.info("eachNormalLi.is_displayed()=%s", eachNormalLi.is_displayed())

        try:
            eachNormalLiHtml = eachNormalLi.get_attribute("innerHTML")
            log.debug("eachNormalLiHtml=%s", eachNormalLiHtml)
        except StaleElementReferenceException as staleErr:
            staleErrMsg = str(staleErr)
            log.error("eachNormalLi get innerHTML error: %s", staleErrMsg)
            driver.refresh()

        curTitle = ""
        curUrl = ""
        curDate = ""
        curDesc = ""

        try:
            """
                <h2><a target="_blank" href="http://www.drv5.cn/azgame/77154.html"
                        h="ID=SERP,5136.1"><strong>白夜琉璃</strong>手游下载-<strong>白夜琉璃</strong>手游内测版v1.4.8-第五驱动</a>
                </h2>
            """
            # h2AItem = eachNormalLi.find_element_by_xpath("//h2/a")
            h2AItem = eachNormalLi.find_element_by_xpath(".//h2/a")
            log.debug("h2AItem=%s", h2AItem)
            log.info("h2AItem.is_displayed()=%s", h2AItem.is_displayed())
            # h2AItemHtml = h2AItem.get_attribute("innerHTML")
            # log.debug("h2AItemHtml=%s", h2AItemHtml)
        except:
            log.error("Failed to find title(h2 a) element")
            continue

        # curTitle = h2AItem.text
        curTitle = getText(h2AItem)
        curUrl = h2AItem.get_attribute("href")
        log.debug("curTitle=%s, curUrl=%s", curTitle, curUrl)

        try:
            """
                <div class="b_caption">
                    <div class="b_attribution" u="0|5124|4545703417479742|AOP9gfi8m1gTJYYm89LkD12SrZYxtwiM">
                        <cite>www.drv5.cn/azgame/77154.html</cite><span class="c_tlbxTrg"><span class="c_tlbxH"
                                h="BASE:CACHEDPAGEDEFAULT" k="SERP,5144.1"></span></span></div>
                    <p>2021-5-11 · 白夜琉璃是一款浪漫情缘<strong>题材</strong>的唯美仙侠<strong>游戏</strong>在这个血色的玄幻世界里可以体验到无比精彩的战斗，多样的挑战将给每个玩家带去无比真实的修行体验，让你能够更好的融入到这个修行者的世界，
                        。</p>
                </div>

                <div class="b_caption hasdl">
                    <div class="b_attribution" u="0N|5120|4545703425540641|52dNYmAZ0LkTJYYm89LkD12SrZYxtwiM">
                        <cite>www.drv5.cn/azgame/77154.html</cite><a href="#" class="trgr_icon" aria-label="Actions for this site"
                            aria-haspopup="true" aria-expanded="false" role="button"><span class="c_tlbxTrg"><span
                                    class="c_tlbxTrgIcn sw_ddgn"></span><span class="c_tlbxH" h="BASE:CACHEDPAGEDEFAULT"
                                    k="SERP,5137.1"></span></span></a></div>
                    <p>2021-5-11 · 白夜琉璃是一款浪漫情缘<strong>题材</strong>的唯美仙侠<strong>游戏</strong>在这个血色的玄幻世界里可以体验到无比精彩的战斗，多样的挑战将给每个玩家带去无比真实的修行体验，让你能够更好的融入到这个修行者的世界，
                        。</p>
                </div>
                <div class="qbrs_data" data-appns="SERP" data-k="5375"></div>
            """
            bCaptionElem = eachNormalLi.find_element_by_xpath(".//div[starts-with(@class, 'b_caption')]")
        except:
            log.warning("Failed to find element: div[b_caption / b_caption hasdl]")
            continue

        log.debug("bCaptionElem=%s", bCaptionElem)

        try:
            # descItem = eachNormalLi.find_element_by_xpath(".//div[@class='b_caption']/p")
            descItem = bCaptionElem.find_element_by_xpath(".//p")
        except:
            log.warning("Failed to find element: description p")
            # continue

            # try to find b_richcard 's tab-content
            # Note: here for b_richcard only parse first tab content as description
            """
                <div class="b_caption">
                    <div class="b_attribution" u="8|5066|4611540973649931|HIyGQVh1PBQxFgDgJoDdz6j7pUw3Fhlb">
                        <cite>https://zhuanlan.zhihu.com/p/121145399</cite><span class="c_tlbxTrg"><span class="c_tlbxH"
                                h="BASE:CACHEDPAGEDEFAULT" k="SERP,5255.1"></span></span></div>
                    <div class="b_richcard">
                        <div class="rc_herotabheader">
                        ...
                                <div class="tab-content">
                                    <div id="tab_2" data-appns="SERP" data-k="5363.2" role="tabpanel" aria-labelledby="tab_2_head"
                                        data-priority="">
                                        <ul class="b_vList b_divsec">
                                            <li data-priority="">
                                                <div><span
                                                        title="经典即时战略游戏（RTS）《帝国时代》系列，可谓是许多玩家的“童年回忆”。作者也是“帝国”的老玩家了，现在时不时还会开上一两把。 《帝国时代》（Age of Empires）是微软公司开发的即时战略游戏，游戏中玩家可以扮演不同文明在历史长河中的各个时代发展经济、建造城市，也可以通过训练军队发动战争征服其他文明。 初代游戏设定为人类史前的石器时代发展到铁器时代的过程（石器时代—工具时代—青铜时代—铁器时代），第二代游戏主要讲述中世纪历史（黑暗时代—封建时代—城堡时代—帝王时代）；第三代游戏在玩法上与前代有所不同，讲述的是地理大发现之后欧洲列强探索、殖民新大陆的故事（发现时代—殖民时代—堡垒时代—工业时代—帝国时代/革命），游戏资料片《酋长》中新增了美洲土著文明：易洛魁、苏族与阿兹特克，玩家可以选择使用原住民与欧洲列强进行对抗，资料片《亚洲王朝》则将美洲土著更换为亚洲三大文明：中华文明、日本文明和印度文明。 《帝国时代终极版》其实是《帝国时代》初代游戏的复刻版本（PC端目前仅支持在Windows10系统运行），体验远古文明从野蛮到智慧的转变。 第二代游戏可谓系列游戏中的最经典之作，游戏有丰富的剧本战役，也可以进行多样的标准游戏（我最喜欢的模式是弑君模式），还有“帝国”系列最有趣的“自建地图”地图编辑器，玩家可以通过编辑器创建自己的剧本，书写时代英雄的故事。 第三代游戏玩法上与前两代大不相同，新增“主城”概念（就是殖民国家的首都），玩家可以在标准游戏中创建主城，游戏中主城可以运送物资到殖民地，玩家也可以“装饰”主城，让其更“漂亮”。不过本作中文明数量大大减少，原版只有8个列强国家（英国、法国、普鲁士、荷兰、西班牙、葡萄牙、俄罗斯、奥斯曼）。三代的游戏画面也更进为3D画面，剧本战役也更加生动，新增的许多概念也让其与前两代游戏相比有了极大的区别度。 在《帝国时代》中担任国王、扮演将军征战沙场，指挥军队，也是一件很有趣（上瘾）的事情呢。 据说《帝国时代4》将在未来发售，还是很期待“老帝国”的新作的！">经典即时战略游戏（RTS）《帝国时代》系列，可谓是许多玩家的“童年回忆”。作者也是“帝国”的老玩家了，现在时不时还会开上一两把。
                                                        《帝国时代》（Age of
                                                        Empires）是微软公司开发的即时战略游戏，游戏中玩家可以扮演不同文明在历史长河中的各个时代发展经济、建造城市，也可以通过训练军队发动战争征服其他文明。
                                                        初代游戏设定为人类史前的石器时代发展到铁器时代的过程（石器时代—工具时代—青铜时代—铁器时代），第二代游戏主要讲述中世纪历史（黑暗时代—封建时代—城堡时代—帝王时代）；
                                                        …</span></div>
                                            </li>
            """
            firstTabItem = bCaptionElem.find_element_by_xpath(".//div[@class='b_richcard']//ul[@class='b_vList b_divsec']")
            descItem = firstTabItem

        log.debug("descItem=%s", descItem)
        curDesc = getText(descItem)
        log.debug("curDesc=%s", curDesc) # 2021-5-11 · 白夜琉璃是一款浪漫情缘题材的唯美仙侠游戏在这个血色的玄幻世界里可以体验到无比精彩的战斗，在不断的磨砺与战斗之中强大自身，让你能够更好的融入到这个修行者的世界，多样的挑战将给每个玩家带去无比真实的修行体验， 。

        if not curDesc:
            log.error("Failed to find description")

        foundDate = re.search("^(?P<curDate>\d+-\d+-\d+)[\s·]*(?P<pureDesc>.+)$", curDesc)
        if foundDate:
            curDate = foundDate.group("curDate") # '2021-5-11'
            pureDesc = foundDate.group("pureDesc") # '白夜琉璃是一款浪漫情缘题材的唯美仙侠游戏在这个血色的玄幻世界里可以体验到无比精彩的战斗，在不断的磨砺与战斗之中强大自身，让你能够更好的融入到这个修行者的世界，多样的挑战将给每个玩家带去无比真实的修行体验， 。'
            log.debug("curDate=%s, pureDesc=%s", curDate, pureDesc)
            curDesc = pureDesc

        curSearchResultDict = {
            "url": curUrl,
            "title": curTitle,
            "date": curDate,
            "description": curDesc,
        }
        log.info("curSearchResultDict=%s", curSearchResultDict)
        searchResultDictList.append(curSearchResultDict)

    # first ad item
    """
        <li class="b_ad">
            <ul>
                <li class="b_adLastChild">
                    <div class="sb_add sb_adTA">
                        <h2><a id="tile_link_cn" target="_blank" class=" b_restorableLink"
                                onmousedown="ad_pt_mousedown_cn(this)" onmouseup="ad_pt_mouseup_cn(this)"
                                href="http://e.so.com/search/eclk?p=dac8DLoMp5KV6LLF4qKf_LLuqlgwadNTcdmVwLMv6rJu6AEsht7C_darl2_QXquzKxu0sJtliKThz1xVpI8DRTMcm5djUgKARzVcTToe5bHpa-jCy3BuA7arrxd641N3fJB6PThDEBq0U5VGAk502OHWwE4XHTap6_FZszlE2SpV8BP8-VUJahRWYxcPOASP_O158ojqdBncS4QMzSW6F3bFmSPtjq_D-2WY1EjdTIWJktETB_Oi5GWHQKA1yJilQFMZVhQmsmshEOyTRHUkU5-YXR9dAoHhD-Y4iDUGdNKQNpa8LGBIiD97Iw75ekuWE79cYm0F4mMvB2Cg4xiNTKYAX3sVtILG3STUtVRzySKCu0xwUDbXB-_u0x2KiUzXcDZD1ymgU0p5EK2l2TSi5yamarcfRrpMF9eKP_L-S2ENmns4BP5DlEN0S_XQ_vlbG8To_6ssqiEKdJmGj0JVm8iGlut8fEfcEA8DA0ZxVw0We1_kulRatXYapd64MmShssGx__K5GNZeGpfhJaZhWzd7j26QJi5kBblTut9oIJhJ0vtOtaGvC4zKiw1MwayTxbh32OpuXhnxkghgaqKzj5hzyHsXfhVHtBp5RpIld_ZEbz5jlILD2vlSBsAiiA15GYdrStSqJfF-l4IKhNcg9sq27zlCzQGc9Sv3of_R9tE-vCtM5vYEUYUmbXxjtxCBdn0-Uy7NDTkgqfBEdBxOtvzKofGd897G02A5j2HDLgeCV37kew&amp;ns=0&amp;v=2&amp;at=AeeZveWknOeQieeSg-a4uOaIjwJfMjAyMQHnmb3lpJznkInnkoMC55S16ISR54mIX-eCueWHu-i_m-WFpQHmuLjmiI8C&amp;aurl=aHR0cDovL2x1Y2suc25nODg5LmNvbS9vbi95eC1zeS94aWFueGlhNDEvczUvY2NpZDAyNjgv&amp;sig=09e3&amp;bt=1"
                                h="ID=SERP,5397.1,Ads"><strong>白夜琉璃游戏</strong>_2021<strong>白夜琉璃</strong>电脑版_点击进入<strong>游戏</strong></a>
                        </h2>
                        <div class="b_caption">
                            <div class="b_attribution"><cite>luck.sng889.com</cite></div>
                            <p class=""><span class="b_adProvider">来自
                                    360</span>2021免费仙侠<strong>游戏</strong>「<strong>白夜琉璃</strong>」,全新地图,爆率升级!结婚组队,自由PK!「<strong>白夜琉璃</strong>」今日新服开启,注册送首充,送VIP!<span
                                    class="b_adSlug b_opttxt b_divdef">广告</span></p>
                        </div>
                        <div class="ad_fls">
    ...
                        </div>
                    </div>
                </li>
            </ul>
        </li>
    """

    # bottom ad item
    """
        <li class="b_ad b_adBottom">
            <ul>
                <li class="b_adLastChild">
                    <div class="sb_add sb_adTA">
                        <h2><a id="tile_link_cn" target="_blank" class=" b_restorableLink"
                                onmousedown="ad_pt_mousedown_cn(this)" onmouseup="ad_pt_mouseup_cn(this)"
                                href="http://e.so.com/search/eclk?p=dac8DLoMp5KV6LLF4qKf_LLuqlgwadNTcdmVwLMv6rJu6AEsht7C_darl2_QXquzKxu0sJtliKThz1xVpI8DRTMcm5djUgKARzVcTToe5bHpa-jCy3BuA7arrxd641N3fJB6PThDEBq0U5VGAk502OHWwE4XHTap6_FZszlE2SpV8BP8-VUJahRWYxcPOASP_O158ojqdBncS4QMzSW6F3bFmSPtjq_D-2WY1EjdTIWJktETB_Oi5GWHQKA1yJilQFMZVhQmsmshEOyTRHUkU5-YXR9dAoHhD-Y4iDUGdNKQNpa8LGBIiD97Iw75ekuWE79cYm0F4mMvB2Cg4xiNTKYAX3sVtILG3STUtVRzySKCu0xwUDbXB-_u0x2KiUzXcDZD1ymgU0p5EK2l2TSi5yamarcfRrpMF9eKP_L-S2ENmns4BP5DlEN0S_XQ_vlbG8To_6ssqiEKdJmGj0JVm8iGlut8fEfcEA8DA0ZxVw0We1_kulRatXYapd64MmShssGx__K5GNZeGpfhJaZhWzd7j26QJi5kBblTut9oIJhJ0vtOtaGvC4zKiw1MwayTxbh32OpuXhnxkghgaqKzj5hzyHsXfhVHtBp5RpIld_ZEbz5jlILD2vlSBsAiiA15GYdrStSqJfF-l4IKhNcg9sq27zlCzQGc9Sv3of_R9tE-vCtM5vYEUYUmbXxjtxCBdn0-Uy7NDTkgqfBEdBxOtvzKofGd897G02A5j2HDLgeCV37kew&amp;ns=0&amp;v=2&amp;at=AeeZveWknOeQieeSg-a4uOaIjwJfMjAyMQHnmb3lpJznkInnkoMC55S16ISR54mIX-eCueWHu-i_m-WFpQHmuLjmiI8C&amp;aurl=aHR0cDovL2x1Y2suc25nODg5LmNvbS9vbi95eC1zeS94aWFueGlhNDEvczUvY2NpZDAyNjgv&amp;sig=09e3&amp;bt=1"
                                h="ID=SERP,5412.1,Ads"><strong>白夜琉璃游戏</strong>_2021<strong>白夜琉璃</strong>电脑版_点击进入<strong>游戏</strong></a>
                        </h2>
                        <div class="b_caption">
                            <div class="b_attribution"><cite>luck.sng889.com</cite></div>
                            <p class=""><span class="b_adProvider">来自
                                    360</span>2021免费仙侠<strong>游戏</strong>「<strong>白夜琉璃</strong>」,全新地图,爆率升级!结婚组队,自由PK!「<strong>白夜琉璃</strong>」今日新服开启,注册送首充,送VIP!<span
                                    class="b_adSlug b_opttxt b_divdef">广告</span></p>
                        </div>
                    </div>
                </li>
            </ul>
        </li>
    """
    if isIncludeAd:
        adSearchResultList = []

        adLiXpath = ".//li[starts-with(@class, 'b_ad')]"
        adLiList = resultElem.find_elements_by_xpath(adLiXpath)
        adLiNum = len(adLiList)
        log.info("adLiNum=%s", adLiNum)

        for eachAdElem in adLiList:
            curAdTitle = ""
            curAdUrl = ""
            curAdDate = ""
            curAdDesc = ""

            try:
                titleElem = eachAdElem.find_element_by_xpath(".//h2/a[@id='tile_link_cn']")
                curAdTitle = getText(titleElem)
                curAdUrl = titleElem.get_attribute("href")
            except:
                log.warning("Failed to find ad title (h2 a[tile_link_cn]) element")
                continue

            try:
                descElem = eachAdElem.find_element_by_xpath(".//div[@class='b_caption']//p")
                curAdDesc = getText(descElem)
            except:
                log.warning("Failed to find ad title (div p) element")

            curAdSearchResultDict = {
                "url": curAdUrl,
                "title": curAdTitle,
                "date": curAdDate,
                "description": curAdDesc,
            }
            log.info("curAdSearchResultDict=%s", curAdSearchResultDict)
            adSearchResultList.append(curAdSearchResultDict)

        searchResultDictList.extend(adSearchResultList)

    return searchResultDictList

def getBingSearchResult(searchKeyword, driver=None, log=logging):
    """
    Emulate bing search, return search result

    Args:
        searchKeyword (str): str to search
        driver (WebDriver): selenium web driver. Default is None. If None, create a new one
        log (logging): log instance. Default is system's logging
    Returns:
        result dict list
    Raises:
    Examples:
        '游戏题材 白夜琉璃'
    """
    if not driver:
        # driver = webdriver.Chrome()
        driver = initBrowser()
        log.warning("Newly created browser %s", driver)

    BingHomeUrl = "https://cn.bing.com/"
    # https://cn.bing.com/search?q=%e7%99%bd%e5%a4%9c%e4%bd%bf%e5%be%92&FORM=R5FD7

    MaxWaitSeconds = 10

    searchResultDictList = []

    try:
        log.info("opening %s", BingHomeUrl)
        driver.get(BingHomeUrl)

        # old: <input class="b_searchbox" id="sb_form_q" name="q" title="输入搜索词" type="search" value="" maxlength="100" autocapitalize="off" autocorrect="off" autocomplete="off" spellcheck="false" aria-controls="sw_as">
        # new: <input id="sb_form_q" class="sb_form_q" name="q" type="search" maxlength="1000" autocomplete="off" aria-label="Enter your search term" autofocus="" aria-controls="sw_as" aria-autocomplete="both" aria-owns="sw_as">
        searchBoxId = "sb_form_q"
        # searchBoxElem = driver.find_element_by_id(searchBoxId)
        # log.info("Found search box %s", searchBoxElem)
        searchBoxElem = WebDriverWait(driver, MaxWaitSeconds).until(
            EC.presence_of_element_located((By.ID, searchBoxId))
        )
        log.info("open complete, showing search input box: %s", searchBoxId)

        # driver.refresh()

        searchBoxElem.send_keys(searchKeyword)
        log.info("Inputed text %s", searchKeyword)

        # # old: <input type="submit" class="b_searchboxSubmit" id="sb_form_go" tabindex="0" name="go">
        # # new: <label for="sb_form_go" class="search icon tooltip" id="search_icon" aria-label="搜索网页" tabindex="-1"><...></svg></label>
        # searchButtonFor = "search_icon"
        # searchButtonElem = driver.find_element(by="id", value=searchButtonFor)
        # searchButtonElem.click()
        # log.info("Clicked button %s to trigger seach", searchButtonElem)

        # many time error: 'Message: no such element: Unable to locate element: {"method":"css selector","selector":"[id="search_icon"]"}\n (Session info: headless chrome=92.0.4515.131)\n'
        # so change to press Enter
        searchBoxElem.send_keys(Keys.RETURN)

        # wait bing search complete -> show some element
        # <span class="sb_count">9,120,000 条结果</span>
        searchCountElem = WebDriverWait(driver, MaxWaitSeconds).until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='sb_count']"))
        )
        log.info("Search complete, showing result: %s", searchCountElem)

        # Note: add refresh to avoid later stale exception:
        #   selenium open https://cn.bing.com/ exception: Message: stale element reference: element is not attached to the page document
        #     (Session info: headless chrome=92.0.4515.131)
        # driver.refresh()

        searchResultDictList = parseBingSearchResult(driver, log=log)
        searchResultNum = len(searchResultDictList)
        log.info("Found %d search result", searchResultNum)
    except Exception as e:
        errStr = str(e)
        # 'Message: timeout: Timed out receiving message from renderer: 10.000\n  (Session info: chrome=92.0.4515.107)\n'
        log.error("selenium open %s exception: %s", BingHomeUrl, errStr)

    return searchResultDictList

################################################################################
# Test
################################################################################

if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))

    # test code
    configDict={'headless': True, 'pageLoadTimeout': 10}
    driver = initBrowser(configDict)

    shortLink = "http://v4g.cn/4AcKyz"
    parseUrl(shortLink, driver=driver)

    closeBrowser(driver)
