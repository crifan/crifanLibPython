#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanSelenium.py
Function: crifanLib's Selenium related functions
Version: 20210723
Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/thirdParty/crifanSelenium.py
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20210723"
__copyright__ = "Copyright (c) 2021, Crifan Li"
__license__ = "GPL"

# from selenium import webdriver
from seleniumwire import webdriver # Support capture http request and response

# for debug
import logging

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

def initBrowser(browserConfig):
    """Init browser driver for selenium

    Args:
        browserConfig (dict): browser config
    Returns:
        driver
    Raises:
    Examples:
        browserConfig
            {'headless': True, 'pageLoadTimeout': 10}
    """
    curPageLoadTimeout = browserConfig["pageLoadTimeout"]
    isCurHeadless = browserConfig["headless"]

    chromeOptions = webdriver.ChromeOptions()
    if isCurHeadless:
        chromeOptions.add_argument('--headless')
    driver = webdriver.Chrome(options=chromeOptions)
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
        driver = webdriver.Chrome()

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
