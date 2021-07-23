#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanPlaywright.py
Function: crifanLib's Playwright related functions
Version: 20210723
Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/thirdParty/crifanPlaywright.py
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20210723"
__copyright__ = "Copyright (c) 2021, Crifan Li"
__license__ = "GPL"

from playwright.sync_api import sync_playwright

# for debug
import logging

################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanPlaywright"

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

def initBrowser(browserType="chromium", browserConfig={"headless": False}):
    """
    For playwright, init to create a browser. For later use, such as google search

    Args:
        browserType (str): Playwright browser type: chromium / firefox / webkit
        browserConfig (dict): Playwright browser config. Default is {"headless": False}.
    Returns:
        BrowserType
    Examples:
        browserConfig
            {
                "headless": False,
                "proxy": {
                    "server": "http://127.0.0.1:58591",
                }
            }
    Raises:
    """
    curBrowserType = None

    if browserType:
        browserType = browserType.lower()

    # with sync_playwright() as p:
    # p = sync_playwright()
    p = sync_playwright().start()
    # 多次调用，会：
	# 发生异常: Error
    # It looks like you are using Playwright Sync API inside the asyncio loop.
    # Please use the Async API instead.

    if browserType == "chromium":
        curBrowserType = p.chromium
    elif browserType == "firefox":
        curBrowserType = p.firefox
    elif browserType == "webkit":
        curBrowserType = p.webkit
    print("curBrowserType=%s" % curBrowserType)
    # curBrowserType=<BrowserType name=chromium executable_path=/Users/limao/Library/Caches/ms-playwright/chromium-901522/chrome-mac/Chromium.app/Contents/MacOS/Chromium>

    if not curBrowserType:
        print("Unsupported playwright browser type: %s" % browserType)
        return None

    # browser = curBrowserType.launch(headless=False)
    # browser = curBrowserType.launch(**browserLaunchOptionDict)
    browser = curBrowserType.launch(**browserConfig)
    print("browser=%s" % browser)
    # browser=<Browser type=<BrowserType name=chromium executable_path=/Users/limao/Library/Caches/ms-playwright/chromium-901522/chrome-mac/Chromium.app/Contents/MacOS/Chromium> version=93.0.4576.0>

    return browser

def initPage(pageConfig=None, browser=None):
    """Init playwright browser new page

    Args:
        pageConfig (dict): page config. Default is None.
        browser (BrowserType): Playwright browser. Default is None. If None, create new one
    Returns:
        Page
    Examples:
        pageConfig
            {"pageLoadTimeout": 10}
    Raises:
    """
    if not browser:
        browser = initBrowser()

    page = browser.new_page()
    # print("page=%s" % page)

    if pageConfig:
        if "pageLoadTimeout" in pageConfig:
            curPageLoadTimeout = pageConfig["pageLoadTimeout"]
            curPageLoadTimeoutMilliSec = curPageLoadTimeout * 1000

            page.set_default_navigation_timeout(curPageLoadTimeoutMilliSec)
            page.set_default_timeout(curPageLoadTimeoutMilliSec)

    return page

def closeBrowser(browser):
    """
    For playwright, close browser

    Args:
        browser (BrowserType): Playwright browser
    Returns:
    Raises:
    """
    browser.close()


def parseUrl(inputUrl, page=None):
    """Parse (redirected final long) url, title, html from input (possible short link) url

    Args:
        inputUrl (dict): input original (short link) url
        page (Page): Playwright page. Default is None. If None, create a new one.
    Returns:
        parse result(dict)
    Raises:
    """
    respValue = None

    if not page:
        page = initPage()

    try:
        page.goto(inputUrl)

        parsedLongLink = page.url # https://api.interactive.angpi.cn/interactive.htm?dateUnix=1588341459669&adSpaceCode=MEDIA200501215739781110&tinyUrl=5NGSFX&domain=m6z.cn&bulletinId=66e0953cdc614aa6a72eb44ba7927b71&sys=pc&tencent=0&reqId=66e0953cdc614aa6a72eb44ba7927b71&mediaRequestId=66e0953cdc614aa6a72eb44ba7927b71
        logging.debug("parsedLongLink=%s", parsedLongLink) # 'https://miyuanxp1260.kuaizhan.com/?inviteCode=RWXK5M&osType=1'
        longLinkTitle = page.title() # '现金大派送'
        logging.debug("longLinkTitle=%s", longLinkTitle)
        longLinkHtml = page.content()
        logging.debug("longLinkHtml=%s", longLinkHtml)

        respValue = {
            "isParseOk": True,
            "url": parsedLongLink,
            "title": longLinkTitle,
            "html": longLinkHtml,
        }
    except Exception as err:
        errStr = str(err)
        # 'net::ERR_NAME_NOT_RESOLVED at http://dmh2.cn/9jaSp0\n=========================== logs ===========================\nnavigating to "http://dmh2.cn/9jaSp0", waiting until "load"\n============================================================\nNote: use DEBUG=pw:api environment variable to capture Playwright logs.'
        # 'net::ERR_CONNECTION_CLOSED at http://zhongan.com/Ahita\n=========================== logs ===========================\nnavigating to "http://zhongan.com/Ahita", waiting until "load"\n============================================================\nNote: use DEBUG=pw:api environment variable to capture Playwright logs.'
        # 'Timeout 10000ms exceeded.\n=========================== logs ===========================\nnavigating to "http://zhongan.com/Ahita", waiting until "load"\n============================================================\nNote: use DEBUG=pw:api environment variable to capture Playwright logs.'
        # 
        logging.debug("Playwright goto %s exception: %s", inputUrl, errStr)

        respValue = {
            "isParseOk": False,
            "errMsg": errStr, 
        }

    return respValue

def parseGoogleSearchResult(page):
    """
    Parse google search result from current (search result) page

    Args:
        page (Page): playwright browser Page
    Returns:
        result dict list
    Raises:
    """
    searchResultDictList = []

    """
    <div class="g">
        <h2 class="Uo8X3b OhScic zsYMMe">网络搜索结果</h2>
        <div data-hveid="CAIQAA" data-ved="2ahUKEwiUn6ShxtDxAhVUNKYKHbCkCD4QFSgAMAB6BAgCEAA">
            <div class="tF2Cxc">
                <div class="yuRUbf"><a
                        href="/url?sa=t&amp;rct=j&amp;q=&amp;esrc=s&amp;source=web&amp;cd=&amp;cad=rja&amp;uact=8&amp;ved=2ahUKEwiUn6ShxtDxAhVUNKYKHbCkCD4QFjAAegQIAhAD&amp;url=http%3A%2F%2Fm.7724.com%2Fccgjz%2F&amp;usg=AOvVaw02ypkYtu3h9TQzpCu3biwN"
                        data-ved="2ahUKEwiUn6ShxtDxAhVUNKYKHbCkCD4QFjAAegQIAhAD"
                        onmousedown="return rwt(this,'','','','','AOvVaw02ypkYtu3h9TQzpCu3biwN','','2ahUKEwiUn6ShxtDxAhVUNKYKHbCkCD4QFjAAegQIAhAD','','',event)"
                        target="_blank" rel="noopener" data-ctbtn="2"
                        data-cthref="/url?sa=t&amp;rct=j&amp;q=&amp;esrc=s&amp;source=web&amp;cd=&amp;cad=rja&amp;uact=8&amp;ved=2ahUKEwiUn6ShxtDxAhVUNKYKHbCkCD4QFjAAegQIAhAD&amp;url=http%3A%2F%2Fm.7724.com%2Fccgjz%2F&amp;usg=AOvVaw02ypkYtu3h9TQzpCu3biwN"><br>
                        <h3 class="LC20lb DKV0Md">城池攻坚战手机游戏下载-7724游戏</h3>
                        。。。。。。
                    </div>
                </div>
                <div class="IsZvec">
                    <div class="VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc"><span><em class="qkunPe">城池攻坚战</em>是一款非常刺激好玩的三国<em
                                class="qkunPe">题材</em>策略类手游。在<em
                                class="qkunPe">游戏</em>中，玩家将梦回三国乱世，成为一方诸侯，与百万玩家一起逐鹿天下!玩家想要在这片战乱不休的大&nbsp;...</span></div>
                </div>
            </div>
        </div>
    </div>
    。。。

    <div class="g">
        <div data-hveid="CA4QAA" data-ved="2ahUKEwiUn6ShxtDxAhVUNKYKHbCkCD4QFSgAMAl6BAgOEAA">
            <div class="tF2Cxc">
                <div class="yuRUbf"><a href="https://www.diyiyou.com/zt/zlccdyx/"
                        data-ved="2ahUKEwiUn6ShxtDxAhVUNKYKHbCkCD4QFjAJegQIDhAD"
                        onmousedown="return rwt(this,'','','','','AOvVaw2YT1TExiYAGLEIgDsnscDf','','2ahUKEwiUn6ShxtDxAhVUNKYKHbCkCD4QFjAJegQIDhAD','','',event)"
                        target="_blank" rel="noopener"><br>
                        <h3 class="LC20lb DKV0Md">占领城池的游戏推荐-耐玩的占领城池的游戏合集-第一手游网</h3>
                        。。。。。。
                </div>
                <div class="IsZvec">
                    <div class="VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc"><span class="MUxGbd wuQ4Ob WZ8Tjf">2020年12月26日 —
                        </span><span>推荐理由：<em class="qkunPe">城池攻坚战</em>是一款大型战争策略<em class="qkunPe">题材</em>的即时竞技类型手游，<em
                                class="qkunPe">游戏</em>以多元化兵种设定，加深战场交锋的策略地位，大气磅礴的三国古战场&nbsp;...</span></div>
                </div>
            </div>
        </div>
    </div>

    ...

    <div class="g">
        <div data-hveid="CAgQAA" data-ved="2ahUKEwi5upCe5NzxAhXLbt4KHXSLBz8QFSgAMAd6BAgIEAA">
            <div class="tF2Cxc">
                <div class="yuRUbf"><a href="https://www.youxi369.com/apps/50997.html"
                        data-ved="2ahUKEwi5upCe5NzxAhXLbt4KHXSLBz8QFjAHegQICBAD"
                        ping="/url?sa=t&amp;source=web&amp;rct=j&amp;url=https://www.youxi369.com/apps/50997.html&amp;ved=2ahUKEwi5upCe5NzxAhXLbt4KHXSLBz8QFjAHegQICBAD"><br>
                        <h3 class="LC20lb DKV0Md">城池攻坚战手游免费下载-城池攻坚战安卓最新版本 ... - 游戏369</h3>
                        <div class="TbwUpd NJjxre"><cite class="iUh30 Zu0yb qLRx3b tjvcx">https://www.youxi369.com<span
                                    class="dyjrff qzEoUe"> › apps</span></cite></div>
                    </a>
                    <div class="B6fmyf">
                        <div class="TbwUpd"><cite class="iUh30 Zu0yb qLRx3b tjvcx">https://www.youxi369.com<span
                                    class="dyjrff qzEoUe"> › apps</span></cite></div>
                        <div class="eFM0qc"><span>
                                <div jscontroller="hiU8Ie" class="action-menu"><a class="GHDvEf" href="#" aria-label="结果选项"
                                        aria-expanded="false" aria-haspopup="true" role="button"
                                        jsaction="PZcoEd;keydown:wU6FVd;keypress:uWmNaf"
                                        data-ved="2ahUKEwi5upCe5NzxAhXLbt4KHXSLBz8Q7B0wB3oECAgQBg"><span
                                            class="gTl8xb"></span></a>
                                    <ol class="action-menu-panel zsYMMe" role="menu" tabindex="-1"
                                        jsaction="keydown:Xiq7wd;mouseover:pKPowd;mouseout:O9bKS"
                                        data-ved="2ahUKEwi5upCe5NzxAhXLbt4KHXSLBz8QqR8wB3oECAgQBw">
                                        <li class="action-menu-item OhScic zsYMMe" role="menuitem"><a class="fl"
                                                href="https://webcache.googleusercontent.com/search?q=cache:SGA7R-UcWfEJ:https://www.youxi369.com/apps/50997.html+&amp;cd=8&amp;hl=zh-CN&amp;ct=clnk&amp;gl=jp"
                                                ping="/url?sa=t&amp;source=web&amp;rct=j&amp;url=https://webcache.googleusercontent.com/search%3Fq%3Dcache:SGA7R-UcWfEJ:https://www.youxi369.com/apps/50997.html%2B%26cd%3D8%26hl%3Dzh-CN%26ct%3Dclnk%26gl%3Djp&amp;ved=2ahUKEwi5upCe5NzxAhXLbt4KHXSLBz8QIDAHegQICBAI"><span>网页快照</span></a>
                                        </li>
                                    </ol>
                                </div>
                            </span></div>
                    </div>
                </div>
                <div class="IsZvec">
                    <div class="VwiC3b MUxGbd yDYNvb lyLwlc"><span class="MUxGbd wuQ4Ob WZ8Tjf">2021年6月4日 —
                        </span>城池攻坚战是一款非常刺激好玩的三国题材策略多人手游。在城池攻坚战官方版中，玩家将回到三国乱世，成为乱世霸主，指挥你的军队，进行&nbsp;...</div>
                </div>
            </div>
        </div>
    </div>

    """
    # searchResultSelector = "div[class='g'] div[class='IsZvec'] div span:last-child"
    # searchResultSelector = "div[class='g'] div[class='IsZvec'] div span:first-child"
    searchResultSelector = "div[class='g']"
    searchResultList = page.query_selector_all(searchResultSelector)
    # print("searchResultList=%s" % searchResultList)
    # searchResultList=[<JSHandle preview=JSHandle@node>, <JSHandle preview=JSHandle@node>, <JSHandle preview=JSHandle@node>, <JSHandle preview=JSHandle@node>, <JSHandle preview=JSHandle@node>, <JSHandle preview=JSHandle@node>, <JSHandle preview=JSHandle@node>, <JSHandle preview=JSHandle@node>, <JSHandle preview=JSHandle@node>]
    searchResultNum = len(searchResultList)
    # print("Found %s search result" % searchResultNum) # 9, 10

    # for debug
    # if searchResultNum < 8:
    if searchResultNum < 5:
        print("Unexpcted too little result count: %s" % searchResultNum)

    for curIdx, curResultElem in enumerate(searchResultList):
        curNum = curIdx + 1
        # print("%s [%d] %s" % ("-"*20, curNum, "-"*20))
        # print("curResultElem=%s" % curResultElem)

        # urlTitleElemSelector = "div[class='tF2Cxc']"
        urlTitleSelector = "div[class='tF2Cxc'] div[class='yuRUbf']"
        urlTitleElem = curResultElem.query_selector(urlTitleSelector)
        # print("urlTitleElem=%s" % urlTitleElem) # urlTitleElem=JSHandle@<div class="yuRUbf">…</div>

        urlSelector = "a[href^='http']"
        urlElem = urlTitleElem.query_selector(urlSelector)
        # print("urlElem=%s" % urlElem) # urlElem=JSHandle@node
        urlStr = urlElem.get_attribute("href")
        # print("urlStr=%s" % urlStr) # urlStr=https://www.325sy.com/game/1118.html

        titleSelector = "h3[class='LC20lb DKV0Md']"
        titleElem = urlTitleElem.query_selector(titleSelector)
        # print("titleElem=%s" % titleElem) # titleElem=JSHandle@node
        titleStr = titleElem.text_content()
        # print("titleStr=%s" % titleStr) # titleStr=城池攻坚战_三国题材为基础的国战类策略手游- 325手游

        dateDescSelector = "div[class='IsZvec'] div[class^='VwiC3b']"
        dateDescElem = curResultElem.query_selector(dateDescSelector)

        # spanElemList = dateDescElem.query_selector_all("span")
        dateStr = ""
        originDateStr = ""
        dateSelector = "span[class^='MUxGbd']"
        dateElem = dateDescElem.query_selector(dateSelector) # None
        if dateElem:
            originDateStr = dateElem.text_content()
            # print("originDateStr=%s" % originDateStr) # '2021年4月19日 —'
            dateStr = originDateStr.replace(" — ", "")
            # print("dateStr=%s" % dateStr) # '2021年4月19日'

        dateDescStr = dateDescElem.text_content() # '下载后请重新注册账号，以免串号没有任何返利! 推荐用梨子手游游戏盒下载，找游戏更方便，还有上线送满级VIP、无限元宝等福利等你来拿! 《城池攻坚战送两万\xa0...'
        dateDescStr = dateDescStr.strip()
        # print("dateDescStr=%s" % dateDescStr)
        descStr = dateDescStr.replace(originDateStr, "")
        # print("descStr=%s" % descStr)

        curSearchResultDict = {
            "url": urlStr,
            "title": titleStr,
            "date": dateStr,
            "description": descStr,
        }
        # print("curSearchResultDict=%s" % curSearchResultDict)
        # curSearchResultDict={'url': 'https://www.325sy.com/game/1118.html', 'title': '城池攻坚战_三国题材为基础的国战类策略手游- 325手游', 'date': '2021年4月19日', 'description': '《城池攻坚战-送2万真充》是一款以三国题材为基础的国战类策略手机游戏！进入游戏之后，首先升级领取你的2W真充.激活运营活动，你就是\xa0...'}
        searchResultDictList.append(curSearchResultDict)

    return searchResultDictList

def getGoogleSearchResult(searchKeyword, browser=None, isAutoCloseBrowser=False):
    """
    Emulate google search, return search result

    Args:
        searchKeyword (str): str to search
        browser (BrowserType): Playwright browser. Default is None. If None, create new one
        isAutoCloseBrowser (bool): whether auto close browser after search
    Returns:
        result dict list
    Raises:
    Examples:
        '游戏题材 城池攻坚战'
    """
    GoogleHomeUrl = "https://www.google.com/"

    searchResultDictList = []

    # if not browser:
    #     browser = initBrowser()

    # page = browser.new_page()
    # print("page=%s" % page)

    page = initPage(browser=browser)

    page.goto(GoogleHomeUrl)

    # <input class="gLFyf gsfi" jsaction="paste:puy29d;" maxlength="2048" name="q" type="text" aria-autocomplete="both" aria-haspopup="false" autocapitalize="off" autocomplete="off" autocorrect="off" autofocus="" role="combobox" spellcheck="false" title="Google 搜索" value="" aria-label="搜索" data-ved="0ahUKEwj8vNuMwdDxAhVmw4sBHb-jBCYQ39UDCAQ">
    SearchInputSelector = "input.gLFyf.gsfi"
    # page.click(SearchInputSelector)
    page.fill(SearchInputSelector, searchKeyword)

    EnterKey = "Enter"
    page.keyboard.press(EnterKey)

    # wait -> makesure element visible
    # <div id="result-stats">找到约 384,000 条结果<nobr> （用时 0.28 秒）&nbsp;</nobr></div>
    SearchFoundSelector = 'div#result-stats'
    page.wait_for_selector(SearchFoundSelector, state="visible")


    """
        <table class="AaVjTc" style="border-collapse:collapse;text-align:left" role="presentation">
            <tbody>
                <tr jsname="TeSSVd" valign="top">
                    <td class="d6cvqb"><span class="SJajHc"
                            style="background:url(/images/nav_logo321.webp) no-repeat;background-position:-24px 0;width:28px"></span>
                    </td>
                    <td class="YyVfkd"><span class="SJajHc"
                            style="background:url(/images/nav_logo321.webp) no-repeat;background-position:-53px 0;width:20px"></span>1
                    </td>
        。。。
                    <td><a aria-label="Page 10" class="fl"
                            href="/search?q=%E6%B8%B8%E6%88%8F%E9%A2%98%E6%9D%90+%E6%96%B0%E6%96%97%E7%BD%97%E5%A4%A7%E9%99%86&amp;ei=k-vrYIaDOa6Vr7wPsbaisAY&amp;start=90&amp;sa=N&amp;ved=2ahUKEwjGmIjb_dzxAhWuyosBHTGbCGYQ8tMDegQIARBN"><span
                                class="SJajHc NVbCr"
                                style="background:url(/images/nav_logo321.webp) no-repeat;background-position:-74px 0;width:20px"></span>10</a>
                    </td>
                    <td aria-level="3" class="d6cvqb" role="heading"><a
                            href="/search?q=%E6%B8%B8%E6%88%8F%E9%A2%98%E6%9D%90+%E6%96%B0%E6%96%97%E7%BD%97%E5%A4%A7%E9%99%86&amp;ei=k-vrYIaDOa6Vr7wPsbaisAY&amp;start=10&amp;sa=N&amp;ved=2ahUKEwjGmIjb_dzxAhWuyosBHTGbCGYQ8NMDegQIARBP"
                            id="pnnext" style="text-align:left"><span class="SJajHc NVbCr"
                                style="background:url(/images/nav_logo321.webp) no-repeat;background-position:-96px 0;width:71px"></span><span
                                style="display:block;margin-left:53px">下一页</span></a></td>
                </tr>
            </tbody>
        </table>

    """
    # 底部 Goooooooogle 多页面导航的部分，确保出现 -》 避免页面加载不完整，后续搜索结果只有2个，而不是完整的个数（一般是8/9/10个）
    # <table class="AaVjTc" style="border-collapse:collapse;text-align:left" role="presentation">
    bottomNaviPageSelector = "table[role='presentation']"
    page.wait_for_selector(bottomNaviPageSelector, state="visible")

    searchResultDictList = parseGoogleSearchResult(page)
    # searchResultNum = len(searchResultDictList)
    # print("searchResultNum=%s" % searchResultNum)

    page.close()

    if isAutoCloseBrowser:
        # close browser
        closeBrowser(browser)

    return searchResultDictList


################################################################################
# Test
################################################################################

if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))

    # test code
    PROXY_HTTP = "http://127.0.0.1:58591"
    PROXY_SOCKS5 = "socks5://127.0.0.1:51837"
    browserConfig = {
        "headless": False,
        # "headless": True,
        "proxy": {
            "server": PROXY_HTTP,
        }
    }
    browser = initBrowser(browserConfig=browserConfig)

    searchStr = '游戏题材 新斗罗大陆'
    resultDictList = getGoogleSearchResult(searchStr, browser=browser)
    resultNum = len(resultDictList)
    print("Google search %s found %s result" % (searchStr, resultNum))

    searchStr = '游戏题材 城池攻坚战'
    resultDictList = getGoogleSearchResult(searchStr, browser=browser)
    resultNum = len(resultDictList)
    print("Google search %s found %s result" % (searchStr, resultNum))

    closeBrowser(browser)
