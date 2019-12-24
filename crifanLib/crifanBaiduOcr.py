#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanBaiduOcr.py
Function: crifanLib's python Baidu image OCR related functions
Version: v20191224
Note:
1. latest version and more can found here:
https://github.com/crifan/crifanLibPython
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "v20191224"
__copyright__ = "Copyright (c) 2020, Crifan Li"
__license__ = "GPL"

import os
import re
import base64
import requests
import time
import logging
from collections import OrderedDict

try:
    from PIL import Image, ImageDraw
except:
    print("need `pip install pillow` if use crifanBaiduOcr functions")

from crifanLib.crifanFile  import readBinDataFromFile
from crifanLib.crifanDatetime  import getCurDatetimeStr

################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanBaiduOcr"

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
# Python Baidu OCR Function
################################################################################

class BaiduOCR():
	# OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic" # 通用文字识别
	# OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/general"        # 通用文字识别（含位置信息版）
	# OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic" # 通用文字识别（高精度版）
	OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate"       # 通用文字识别（高精度含位置版）

	TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'

	RESP_ERR_CODE_QPS_LIMIT_REACHED = 18
	RESP_ERR_TEXT_QPS_LIMIT_REACHED = "Open api qps request limit reached"

	RESP_ERR_CODE_DAILY_LIMIT_REACHED = 17
	RESP_ERR_TEXT_DAILY_LIMIT_REACHED = "Open api daily request limit reached"

	API_KEY = 'change_to_your_baidu_ocr_api_key'
	SECRET_KEY = 'change_to_your_baidu_ocr_secret_key'

	def initOcr(self):
		self.curToken = self.baiduFetchToken()

	def baiduFetchToken(self):
		"""Fetch Baidu token for OCR"""
		params = {
			'grant_type': 'client_credentials',
			'client_id': self.API_KEY,
			'client_secret': self.SECRET_KEY
		}

		resp = requests.get(self.TOKEN_URL, params=params)
		respJson = resp.json()

		respToken = ""

		if ('access_token' in respJson.keys() and 'scope' in respJson.keys()):
			if not 'brain_all_scope' in respJson['scope'].split(' '):
				logging.error('please ensure has check the  ability')
			else:
				respToken = respJson['access_token']
		else:
			logging.error('please overwrite the correct API_KEY and SECRET_KEY')

		# '24.869xxxxxxxxxxxxxxxxxxxxxxx2.2592000.1578465979.282335-17921535'
		return respToken

	def baiduImageToWords(self, imageFullPath):
		"""Detect text from image using Baidu OCR api"""

		# # Note: if using un-paid = free baidu api, need following wait sometime to reduce: qps request limit
		# time.sleep(0.15)

		respWordsResutJson = ""

		# 读取图片二进制数据
		imgBinData = readBinDataFromFile(imageFullPath)
		encodedImgData = base64.b64encode(imgBinData)

		paramDict = {
			"access_token": self.curToken
		}

		headerDict = {
			"Content-Type": "application/x-www-form-urlencoded"
		}

		# 参数含义：http://ai.baidu.com/ai-doc/OCR/vk3h7y58v
		dataDict = {
			"image": encodedImgData,
			"recognize_granularity": "small",
			# "vertexes_location": "true",
		}
		resp = requests.post(self.OCR_URL, params=paramDict, headers=headerDict, data=dataDict)
		respJson = resp.json()

		logging.debug("baidu OCR: imgage=%s -> respJson=%s", imageFullPath, respJson)

		if "error_code" in respJson:
			logging.warning("respJson=%s" % respJson)
			errorCode = respJson["error_code"]
			# {'error_code': 17, 'error_msg': 'Open api daily request limit reached'}
			# {'error_code': 18, 'error_msg': 'Open api qps request limit reached'}
			# the limit count can found from
			# 文字识别 - 免费额度 | 百度AI开放平台
			# https://ai.baidu.com/ai-doc/OCR/fk3h7xu7h
			# for "通用文字识别（高精度含位置版）" is "50次/天"
			if errorCode == self.RESP_ERR_CODE_QPS_LIMIT_REACHED:
				# wait sometime and try again
				time.sleep(1.0)
				resp = requests.post(self.OCR_URL, params=paramDict, headers=headerDict, data=dataDict)
				respJson = resp.json()
				logging.debug("baidu OCR: for errorCode=%s, do again, imgage=%s -> respJson=%s", errorCode, imageFullPath, respJson)
			elif errorCode == self.RESP_ERR_CODE_DAILY_LIMIT_REACHED:
				logging.error("Fail to continue using baidu OCR api today !!!")
				respJson = None

		"""
		{
		"log_id": 6937531796498618000,
		"words_result_num": 32,
		"words_result": [
			{
			"chars": [
				...
		"""
		if "words_result" in respJson:
			respWordsResutJson = respJson

		return respWordsResutJson


	def calcWordsLocation(self, wordStr, curWordsResult):
		"""Calculate words location from result

		Args:
			wordStr (str): the words to check
			curWordsResult (dict): the baidu OCR result of current words
		Returns:
			location, a tuple (x, y, width, height)
		Raises:
		Examples
				wordStr="首充"
				curWordsResult= {
						"chars": [
                            {
                                "char": "寻",
                                "location": {
                                    "width": 15,
                                    "top": 51,
                                    "left": 725,
                                    "height": 24
                                }
							},
							...
                            {
                                "char": "首",
                                "location": {
                                    "width": 15,
                                    "top": 51,
                                    "left": 971,
                                    "height": 24
                                }
							},
							{
                                "char": "充",
                                "location": {
                                    "width": 15,
                                    "top": 51,
                                    "left": 986,
                                    "height": 24
                                }
							}
						],
						"location": {
							"width": 280,
							"top": 51,
							"left": 725,
							"height": 24
						},
						"words": "寻宝福利大厅商城首充"
					}
				-> (971, 51, 30, 24)
		"""
		(x, y, width, height) = (0, 0, 0, 0)
		matchedStr = curWordsResult["words"]
		# Note: for special, contain multilple words, here only process firt words
		foundWords = re.search(wordStr, matchedStr)
		if foundWords:
			logging.debug("foundWords=%s" % foundWords)

			firstMatchedPos = foundWords.start()
			lastMatchedPos = foundWords.end() - 1

			matchedStrLen = len(matchedStr)
			charResultList = curWordsResult["chars"]
			charResultListLen = len(charResultList)

			firstCharResult = None
			lastCharResult = None
			if matchedStrLen == charResultListLen:
				firstCharResult = charResultList[firstMatchedPos]
				lastCharResult = charResultList[lastMatchedPos]
			else:
				# Special: for 'Loading' matched ' Loading', but charResultList not include first space ' ', but from fisrt='L' to end='g'
				# so using find the corresponding char, then got its location
				# Note: following method not work for regex str, like '^游戏公告$'

				firtToMatchChar = wordStr[0]
				lastToMatchChar = wordStr[-1]

				for eachCharResult in charResultList:
					if firstCharResult and lastCharResult:
						break

					eachChar = eachCharResult["char"]
					if firtToMatchChar == eachChar:
						firstCharResult = eachCharResult
					elif lastToMatchChar == eachChar:
						lastCharResult = eachCharResult

			# Note: follow no need check words, to support input ^游戏公告$ to match "游戏公告"
			# firstLocation = None
			# lastLocation = None
			# if firstCharResult["char"] == firtToMatchChar:
			# 	firstLocation = firstCharResult["location"]
			# if lastCharResult["char"] == lastToMatchChar:
			# 	lastLocation = lastCharResult["location"]
			firstLocation = firstCharResult["location"]
			lastLocation = lastCharResult["location"]

			# if firstLocation and lastLocation:

			# support both horizontal and vertical words
			firstLeft = firstLocation["left"]
			lastLeft = lastLocation["left"]
			minLeft = min(firstLeft, lastLeft)
			x = minLeft

			firstHorizontalEnd = firstLeft + firstLocation["width"]
			lastHorizontalEnd = lastLeft + lastLocation["width"]
			maxHorizontalEnd = max(firstHorizontalEnd, lastHorizontalEnd)
			width = maxHorizontalEnd - x

			lastTop = lastLocation["top"]
			minTop = min(firstLocation["top"], lastTop)
			y = minTop

			lastVerticalEnd = lastTop + lastLocation["height"]
			height = lastVerticalEnd - y

		return x, y, width, height

	def locationToCenterPos(self, wordslocation):
		"""Convert location of normal button to center position

		Args:
			wordslocation (tuple): words location, (x, y, width, height)
				Example: (267, 567, 140, 39)
		Returns:
			tuple, (x, y), the location's center position, normal used later to click it
				Example: (337.0, 586.5)
		Raises:
		"""
		x, y, width, height = wordslocation
		centerX = x + width/2
		centerY = y + height/2
		centerPosition = (centerX, centerY)
		return centerPosition

	def isWordsInResult(self, respJson, wordsOrWordsList, isMatchMultiple=False):
		"""Check words is in result or not

		Args:
			respJson (dict): Baidu OCR responsed json
			wordsOrWordsList (str/list): single input str or str list
			isMatchMultiple (bool): for each single str, to match multiple output or only match one output
		Returns:
			dict, matched result
		Raises:
		"""
		# Note: use OrderedDict instead dict to keep order, for later get first match result to process
		orderedMatchedResultDict = OrderedDict()

		inputWordsList = wordsOrWordsList
		if isinstance(wordsOrWordsList, str):
			inputWords = str(wordsOrWordsList)
			inputWordsList = [inputWords]

		wordsResultList = respJson["words_result"]
		for curInputWords in inputWordsList:
			curMatchedResultList = []
			for eachWordsResult in wordsResultList:
				eachWords = eachWordsResult["words"]
				foundCurWords = re.search(curInputWords, eachWords)
				if foundCurWords:
					curMatchedResultList.append(eachWordsResult)
					if not isMatchMultiple:
						break

			orderedMatchedResultDict[curInputWords] = curMatchedResultList
		return orderedMatchedResultDict


	def isWordsInCurScreen(self, wordsOrWordsList, imgPath=None, isMatchMultiple=False, isRespShortInfo=False):
		"""Found words in current screen

		Args:
			wordsOrWordsList (str/list): single input str or str list
			imgPath (str): current screen image file path; default=None; if None, will auto get current scrren image
			isMatchMultiple (bool): for each single str, to match multiple output or only match one output; default=False
			isRespShortInfo (bool): return simple=short=nomarlly bool or list[bool] info or return full info which contain imgPath and full matched result.
		Returns:
			matched result, type=bool/list[bool]/dict/tuple, depends on diffrent condition
		Raises:
		"""
		retValue = None

		if not imgPath:
			# do screenshot
			imgPath = self.getCurScreen()

		wordsResultJson = self.baiduImageToWords(imgPath)

		isMultipleInput = False
		inputWords = None
		inputWordsList = []

		if isinstance(wordsOrWordsList, list):
			isMultipleInput = True
			inputWordsList = list(wordsOrWordsList)
		elif isinstance(wordsOrWordsList, str):
			isMultipleInput = False
			inputWords = str(wordsOrWordsList)
			inputWordsList = [inputWords]

		matchedResultDict = self.isWordsInResult(wordsResultJson, wordsOrWordsList, isMatchMultiple)

		# add caclulated location and words
		# Note: use OrderedDict instead dict to keep order, for later get first match result to process
		processedResultDict = OrderedDict()
		for eachInputWords in inputWordsList:
			isCurFound = False
			# curLocatoinList = []
			# curWordsList = []
			curResultList = []

			curWordsMatchedResultList = matchedResultDict[eachInputWords]
			if curWordsMatchedResultList:
				isCurFound = True
				for curIdx, eachWordsMatchedResult in enumerate(curWordsMatchedResultList):
					curMatchedWords = eachWordsMatchedResult["words"]
					calculatedLocation = self.calcWordsLocation(eachInputWords, eachWordsMatchedResult)
					# curLocatoinList.append(calculatedLocation)
					# curWordsList.append(curMatchedWords)
					curResult = (curMatchedWords, calculatedLocation)
					curResultList.append(curResult)

			# processedResultDict[eachInputWords] = (isCurFound, curLocatoinList, curWordsList)
			processedResultDict[eachInputWords] = (isCurFound, curResultList)
		logging.debug("For %s, matchedResult=%s from imgPath=%s", wordsOrWordsList, processedResultDict, imgPath)

		if isMultipleInput:
			if isRespShortInfo:
				isFoundList = []
				for eachInputWords in processedResultDict.keys():
					isCurFound, noUse = processedResultDict[eachInputWords]
					isFoundList.append(isCurFound)
				# Note: no mattter isMatchMultiple, both only return single boolean for each input words
				retBoolList = isFoundList
				retValue = retBoolList
			else:
				if isMatchMultiple:
					retTuple = processedResultDict, imgPath
					retValue = retTuple
				else:
					# Note: use OrderedDict instead dict to keep order, for later get first match result to process
					respResultDict = OrderedDict()
					for eachInputWords in processedResultDict.keys():
						# isCurFound, curLocatoinList, curWordsList = processedResultDict[eachInputWords]
						isCurFound, curResultList = processedResultDict[eachInputWords]
						# singleLocation = None
						# singleWords = None
						singleResult = (None, None)
						if isCurFound:
							# singleLocation = curLocatoinList[0]
							# singleWords = curWordsList[0]
							singleResult = curResultList[0]
						# respResultDict[eachInputWords] = (isCurFound, singleLocation, singleWords)
						respResultDict[eachInputWords] = (isCurFound, singleResult)
					retTuple = respResultDict, imgPath
					retValue = retTuple
		else:
			singleInputResult = processedResultDict[inputWords]
			# isCurFound, curLocatoinList, curWordsList = singleInputResult
			isCurFound, curResultList = singleInputResult
			if isRespShortInfo:
				# Note: no mattter isMatchMultiple, both only return single boolean for each input words
				retBool = isCurFound
				retValue = retBool
			else:
				if isMatchMultiple:
					# retTuple = isCurFound, curLocatoinList, curWordsList, imgPath
					retTuple = isCurFound, curResultList, imgPath
					retValue = retTuple
				else:
					singleResult = (None, None)
					# singleLocation = None
					# singleWords = None
					if isCurFound:
						# singleLocation = curLocatoinList[0]
						# singleWords = curWordsList[0]
						singleResult = curResultList[0]
					# retTuple = isCurFound, singleLocation, singleWords, imgPath
					retTuple = isCurFound, singleResult, imgPath
					retValue = retTuple

		logging.debug("Input: %s, output=%s", wordsOrWordsList, retValue)
		return retValue

	def getCurScreen(self):
		"""get current screenshot image file path"""
		curDatetimeStr = getCurDatetimeStr()
		# curFilename = curDatetimeStr + ".png"
		curFilename = curDatetimeStr + ".jpg"
		fullImgFilePath = os.path.join(os.getcwd(), curFilename)
		fullImgFilePath = self.driver.screenshot(fullImgFilePath)
		return fullImgFilePath

	def getWordsInCurScreen(self):
		"""get words in current screenshot"""
		screenImgPath = self.getCurScreen()
		wordsResultJson = self.baiduImageToWords(screenImgPath)
		return wordsResultJson

	def checkExistInScreen(self,
			imgPath=None,
			mandatoryStrList=[],
			mandatoryMinMatchCount=0,
			optionalStrList=[],
			# optionalMinMatchCount=2,
			optionalMinMatchCount=1,
			isRespFullInfo=False
		):
		"""Check whether mandatory and optional str list in current screen or not

		Args:
			imgPath (str): current screen image file path; default=None; if None, will auto get current scrren image
			mandatoryStrList (list): mandatory str, at least match `mandatoryMinMatchCount`, or all must match if `mandatoryMinMatchCount`=0
			mandatoryMinMatchCount (int): minimal match count for mandatory list
			optionalStrList (list): optional str, some may match
			optionalMinMatchCount (int): for `optionalStrList`, the minimal match count, consider to match or not
			isRespFullInfo (bool): return full info or not, full info means match location result and imgPath
		Returns:
			matched result, type=bool/tuple, depends on `isRespFullInfo`
		Raises:
		"""
		if not imgPath:
			imgPath = self.getCurScreen()
		logging.debug("imgPath=%s", imgPath)

		isExist = False
		# Note: use OrderedDict instead dict to keep order, for later get first match result to process
		respMatchLocation = OrderedDict()

		isMandatoryMatch = True
		isMandatoryShouldMatchAll = (mandatoryMinMatchCount <= 0)
		isOptionalMatch = True

		allStrList = []
		allStrList.extend(mandatoryStrList)
		allStrList.extend(optionalStrList)

		optionalMatchCount = 0
		mandatoryMatchCount = 0
		allResultDict, _ = self.isWordsInCurScreen(allStrList, imgPath, isMatchMultiple=True)
		for eachStr, (isFoundCur, curResultList) in allResultDict.items():
			if eachStr in mandatoryStrList:
				if isFoundCur:
					mandatoryMatchCount += 1
					respMatchLocation[eachStr] = curResultList
				else:
					if isMandatoryShouldMatchAll:
						isMandatoryMatch = False
						break
			elif eachStr in optionalStrList:
				if isFoundCur:
					optionalMatchCount += 1
					respMatchLocation[eachStr] = curResultList

		if mandatoryStrList:
			if not isMandatoryShouldMatchAll:
				if mandatoryMatchCount >= mandatoryMinMatchCount:
					isMandatoryMatch = True
				else:
					isMandatoryMatch = False

		if optionalStrList:
			if optionalMatchCount >= optionalMinMatchCount:
				isOptionalMatch = True
			else:
				isOptionalMatch = False

		isExist = isMandatoryMatch and isOptionalMatch
		logging.debug("isMandatoryMatch=%s, isOptionalMatch=%s -> isExist=%s", isMandatoryMatch, isOptionalMatch, isExist)

		if isRespFullInfo:
			logging.debug("mandatoryStrList=%s, optionalStrList=%s -> isExist=%s, respMatchLocation=%s, imgPath=%s", 
				mandatoryStrList, optionalStrList, isExist, respMatchLocation, imgPath)
			return (isExist, respMatchLocation, imgPath)
		else:
			logging.debug("mandatoryStrList=%s, optionalStrList=%s -> isExist=%s", 
				mandatoryStrList, optionalStrList, isExist)
			return isExist

	def isExistAnyStr(self, strList, imgPath=None, isRespFullInfo=False):
		"""Is any str exist or not

		Args:
			strList (list): str list to check exist or not
			imgPath (str): current screen image file path; default=None; if None, will auto get current scrren image
			isRespFullInfo (bool): return full info or not, full info means match location result and imgPath
		Returns:
			matched result, type=bool/tuple, depends on `isRespFullInfo`
		Raises:
		"""
		if not imgPath:
			imgPath = self.getCurScreen()

		checkResult = self.checkExistInScreen(
			imgPath=imgPath,
			optionalStrList=strList,
			optionalMinMatchCount=1,
			isRespFullInfo=isRespFullInfo,
		)
		if isRespFullInfo:
			isExistAny, matchResult, imgPath = checkResult
			logging.debug("isExistAny=%s, matchResult=%s, imgPath=%s for %s", isExistAny, matchResult, imgPath, strList)
			return (isExistAny, matchResult, imgPath)
		else:
			isExistAny = checkResult
			logging.debug("isExistAny=%s, for %s", isExistAny, strList)
			return isExistAny

	def isExistAllStr(self, strList, imgPath=None, isRespFullInfo=False):
		"""Is all str exist or not

		Args:
			strList (list): str list to check exist or not
			imgPath (str): current screen image file path; default=None; if None, will auto get current scrren image
			isRespFullInfo (bool): return full info or not, full info means match location result and imgPath
		Returns:
			matched result, type=bool/tuple, depends on `isRespFullInfo`
		Raises:
		"""
		if not imgPath:
			imgPath = self.getCurScreen()
		checkResult = self.checkExistInScreen(imgPath=imgPath, mandatoryStrList=strList, isRespFullInfo=isRespFullInfo)
		if isRespFullInfo:
			isExistAll, matchResult, imgPath = checkResult
			logging.debug("isExistAll=%s, matchResult=%s, imgPath=%s for %s", isExistAll, matchResult, imgPath, strList)
			return (isExistAll, matchResult, imgPath)
		else:
			isExistAll = checkResult
			logging.debug("isExistAll=%s, for %s", isExistAll, strList)
			return isExistAll


################################################################################
# Test
################################################################################

if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))