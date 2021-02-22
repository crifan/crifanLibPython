#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanBaiduOcr.py
Function: crifanLib's python Baidu image OCR related functions
Version: 20210222
Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/thirdParty/crifanBaiduOcr.py
Usage: https://book.crifan.com/books/python_common_code_snippet/website/common_code/multimedia/image/baidu_ocr.html
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20210222"
__copyright__ = "Copyright (c) 2021, Crifan Li"
__license__ = "GPL"

import os
import re
import base64
import requests
import time
import logging
from collections import OrderedDict
from difflib import SequenceMatcher

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
	"""
		百度OCR
			QuickStart
				https://ai.baidu.com/ai-doc/OCR/dk3iqnq51

			费用 价格 通用场景文字识别
				https://ai.baidu.com/ai-doc/OCR/9k3h7xuv6
			
			接口调用
				通用文字识别（高精度含位置版）
					https://ai.baidu.com/ai-doc/OCR/tk3h7y2aq
				
				通用文字识别（标准含位置版）
					https://ai.baidu.com/ai-doc/OCR/vk3h7y58v
	"""

	OCR_URL_GENERAL_BASIC = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"		# 通用文字识别
	OCR_URL_GENERAL = "https://aip.baidubce.com/rest/2.0/ocr/v1/general"					# 通用文字识别（含位置信息版）
	OCR_URL_ACCURATE_BASIC = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"		# 通用文字识别（高精度版）
	OCR_URL_ACCURATE = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate"					# 通用文字识别（高精度含位置版）

	OCR_URL = OCR_URL_ACCURATE

	TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'

	RESP_ERR_CODE_QPS_LIMIT_REACHED = 18
	RESP_ERR_TEXT_QPS_LIMIT_REACHED = "Open api qps request limit reached"

	RESP_ERR_CODE_DAILY_LIMIT_REACHED = 17
	RESP_ERR_TEXT_DAILY_LIMIT_REACHED = "Open api daily request limit reached"

	API_KEY = 'change_to_your_baidu_ocr_api_key'
	SECRET_KEY = 'change_to_your_baidu_ocr_secret_key'

	def __init__(self, api_key=None, secret_key=None):
		if api_key:
			self.API_KEY = api_key
		if secret_key:
			self.SECRET_KEY = secret_key
		self.curToken = self.updateToken()

	def updateToken(self):
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
				logging.error('please ensure has check the ability')
			else:
				respToken = respJson['access_token']
		else:
			logging.error('please overwrite the correct API_KEY and SECRET_KEY')

		# '24.869xxxxxxxxxxxxxxxxxxxxxxx2.2592000.1578465979.282335-17921535'
		return respToken

	def imageToWords(self, imageFullPath):
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

		# 参数含义：
		# 	通用文字识别（标准含位置版）
		# 		http://ai.baidu.com/ai-doc/OCR/vk3h7y58v
		#	通用文字识别（高精度含位置版）
		# 		http://ai.baidu.com/ai-doc/OCR/tk3h7y2aq
		dataDict = {
			"image": encodedImgData,
			"recognize_granularity": "small",
			# "vertexes_location": "true",
			"detect_direction": "true", # default: false
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
				logging.error("Fail to continue using baidu OCR api today for exceed free limit of single day !!!")
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
			charResultListMaxIdx = charResultListLen - 1

			firstCharResult = None
			lastCharResult = None
			if matchedStrLen == charResultListLen:
				firstCharResult = charResultList[firstMatchedPos]
				lastCharResult = charResultList[lastMatchedPos]
			else:
				# Special: for 'Loading' matched ' Loading', but charResultList not include first space ' ', but from fisrt='L' to end='g'
				# so using find the corresponding char, then got its location
				# Note: following method not work for regex str, like '^游戏公告$'

				wordStrLen = len(wordStr)
				wordStrMaxIdx = wordStrLen - 1
				firtToMatchChar = wordStr[0]

				for eachIdx, eachCharResult in enumerate(charResultList):
					eachChar = eachCharResult["char"]
					if firtToMatchChar == eachChar:
						firstCharResult = eachCharResult
						endNextIdx = eachIdx + wordStrLen
						matchedPartList = charResultList[eachIdx:endNextIdx]
						matchedPartStr = ""
						for eachMatchedPart in matchedPartList:
							matchedPartStr += eachMatchedPart["char"]
						isMatch = re.match(wordStr, matchedPartStr)
						if isMatch:
							endIdx = eachIdx + wordStrMaxIdx
							lastCharResult = charResultList[endIdx]
							break

			# Note: follow no need check words, to support input ^游戏公告$ to match "游戏公告"
			# firstLocation = None
			# lastLocation = None
			# if firstCharResult["char"] == firtToMatchChar:
			# 	firstLocation = firstCharResult["location"]
			# if lastCharResult["char"] == lastToMatchChar:
			# 	lastLocation = lastCharResult["location"]

			# Special:
			# wordStr = '^(点击)?任意地方继续' 
			# matchedStr = '点击任意地方继续 Dereloprment Build'
			# -> firstCharResult is None
			# add following try to avoid: TypeError: 'NoneType' object is not subscriptable
			if not firstCharResult:
				firstCharResult = charResultList[firstMatchedPos]

			if not lastCharResult:
				if lastMatchedPos <= charResultListMaxIdx:
					lastCharResult = charResultList[lastMatchedPos]
				else:
					lastCharResult = charResultList[-1]

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


	def isWordsInResult(self, respJson, strOrStrList, isMatchMultiple=True):
		"""Check words is in result or not

		Args:
			respJson (dict): Baidu OCR responsed json
			strOrStrList (str/list): single input str or str list
			isMatchMultiple (bool): for each single str, to match multiple output or only match one output. default True
		Returns:
			dict, matched result
		Raises:
		"""
		# Note: use OrderedDict instead dict to keep order, for later get first match result to process
		orderedMatchedResultDict = OrderedDict()

		inputStrList = strOrStrList
		if isinstance(strOrStrList, str):
			inputStr = str(strOrStrList)
			inputStrList = [inputStr]

		wordsResultList = respJson["words_result"]
		for curInputWords in inputStrList:
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

	def isStrInImage(self,
		strOrStrList,
		imgPath=None,
		wordsResultJson=None,
		isMatchMultiple=True,
		isRespShortInfo=False
	):
		"""Found words in current screen

		Args:
			strOrStrList (str/list): single input str or str list
			imgPath (str): current screen image file path; default=None; if None, will auto get current scrren image
			wordsResultJson (dict): baidu OCR result dict; if None, will auto generate from imgPath
			isMatchMultiple (bool): for each single str, to match multiple output or only match one output; default=True
			isRespShortInfo (bool): return simple=short=nomarlly bool or list[bool] info or return full matched result info
		Returns:
			matched result, type=bool/list/dict/tuple, depends on diffrent condition
		Raises:
		"""
		retValue = None

		if not wordsResultJson:
			wordsResultJson = self.imageToWords(imgPath)

		isMultipleInput = False
		inputStr = None
		inputStrList = []

		if isinstance(strOrStrList, list):
			isMultipleInput = True
			inputStrList = list(strOrStrList)
		elif isinstance(strOrStrList, str):
			isMultipleInput = False
			inputStr = str(strOrStrList)
			inputStrList = [inputStr]

		matchedResultDict = self.isWordsInResult(wordsResultJson, strOrStrList, isMatchMultiple)

		# add caclulated location and words
		# Note: use OrderedDict instead dict to keep order, for later get first match result to process
		processedResultDict = OrderedDict()
		for eachInputWords in inputStrList:
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
		logging.debug("For %s, matchedResult=%s from imgPath=%s", strOrStrList, processedResultDict, imgPath)

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
					retValue = processedResultDict
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
							singleResult = curResultList[0]
						respResultDict[eachInputWords] = (isCurFound, singleResult)
					retValue = respResultDict
		else:
			singleInputResult = processedResultDict[inputStr]
			# isCurFound, curLocatoinList, curWordsList = singleInputResult
			isCurFound, curResultList = singleInputResult
			if isRespShortInfo:
				# Note: no mattter isMatchMultiple, both only return single boolean for each input words
				retBool = isCurFound
				retValue = retBool
			else:
				if isMatchMultiple:
					retTuple = isCurFound, curResultList
					retValue = retTuple
				else:
					singleResult = (None, None)
					if isCurFound:
						singleResult = curResultList[0]
					retTuple = isCurFound, singleResult
					retValue = retTuple

		logging.debug("Input: %s, output=%s", strOrStrList, retValue)
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

	def checkIncludeExcludeInScreen(self,
			imgPath=None,
			includeMandatoryStrList=[],
			includeMandatoryMinMatchCount=0,
			includeOptionalStrList=[],
			includeOptionalMinMatchCount=1,
			excludeStrList=[],
			isRespFullInfo=False
		):
		"""Check include mandatory/optional str in and exclude str not in current screen

		Args:
			imgPath (str): current screen image file path; default=None; if None, will auto get current scrren image
			includeMandatoryStrList (list): mandatory str, at least match `includeMandatoryMinMatchCount`, or all must match if `mandatoryMinMatchCount`=0
			includeMandatoryMinMatchCount (int): minimal match count for mandatory list
			includeOptionalStrList (list): optional str, some may match
			includeOptionalMinMatchCount (int): for `includeOptionalStrList`, the minimal match count, consider to match or not
			excludeStrList (list): excluded str list, means should not found these str
			isRespFullInfo (bool): return full info or not, full info means match location result and imgPath
		Returns:
			matched result, type=bool/tuple, depends on `isRespFullInfo`
		Raises:
		"""
		isFinalMatch = False
		isIncludeMatch=False
		isExcludeMatch = False
		includeMatchResult = None
		excludeMatchResult = None

		if not imgPath:
			imgPath = self.getCurScreenshot()
		logging.debug("imgPath=%s", imgPath)

		wordsResultJson = self.baiduImageToWords(imgPath)

		# first check exclude str list
		isRespShortInfo = not isRespFullInfo

		# # for debug
		# excludeStr = excludeStrList[0]
		# excludeResult = self.isWordsInCurScreen(excludeStr, imgPath=imgPath, wordsResultJson=wordsResultJson, isRespShortInfo=isRespShortInfo)
		excludeResult = self.isWordsInCurScreen(excludeStrList, imgPath=imgPath, wordsResultJson=wordsResultJson, isRespShortInfo=isRespShortInfo)

		if isRespFullInfo:
			excludeResultDict, imgPath = excludeResult
			excludeMatchResult = OrderedDict()
			for eachStr, (isFoundCur, curResultList) in excludeResultDict.items():
				if eachStr in excludeStrList:
					if isFoundCur:
						isExcludeMatch = True
						excludeMatchResult[eachStr] = curResultList

			if isExcludeMatch:
				isFinalMatch = False
				return isFinalMatch, includeMatchResult, excludeMatchResult, imgPath, wordsResultJson
		else:
			if isinstance(excludeResult, list):
				for eachFound in excludeResult:
					if eachFound:
						isExcludeMatch = True
						break
			elif isinstance(excludeResult, bool):
				isExcludeMatch = excludeResult

			if isExcludeMatch:
				isFinalMatch = False
				return isFinalMatch

		# then check mandatory and optional str list
		includeResult = self.checkExistInScreen(
			imgPath=imgPath,
			wordsResultJson=wordsResultJson,
			mandatoryStrList=includeMandatoryStrList,
			mandatoryMinMatchCount=includeMandatoryMinMatchCount,
			optionalStrList=includeOptionalStrList,
			optionalMinMatchCount=includeOptionalMinMatchCount,
			isRespFullInfo=isRespFullInfo,
		)
		if isRespFullInfo:
			isIncludeMatch, includeMatchResult, imgPath, wordsResultJson = includeResult
			return isIncludeMatch, includeMatchResult, excludeMatchResult, imgPath, wordsResultJson
		else:
			isIncludeMatch = includeResult
			return isIncludeMatch

	def checkSameWordsLocation(self, locationDict1, locationDict2):
		"""Check whether two words location is same
			logic:
				>=3 of 4 point value is same
					same: point value is same or diff <= 2

		Args:
			locationDict1 (dict): location 1 dict
			locationDict2 (dict): location 2 dict
		Returns:
			bool
		Raises:
		Examples:
			Input:
				locationDict1: {'height': 38, 'left': 23, 'top': 21, 'width': 37}
				locationDict2: {'height': 38, 'left': 22, 'top': 21, 'width': 38}
			Output: True
		"""
		MinSamePointNum = 3
		# MaxPointDiff = 2
		MaxPointDiff = 3

		isLocationSame = False
		locationSameNum = 0

		widthDiff = abs(locationDict1["width"] - locationDict2["width"])
		isWidthSame = widthDiff <= MaxPointDiff
		if isWidthSame:
			locationSameNum += 1

		topDiff = abs(locationDict1["top"] - locationDict2["top"])
		isTopSame = topDiff <= MaxPointDiff
		if isTopSame:
			locationSameNum += 1

		leftDiff = abs(locationDict1["left"] - locationDict2["left"])
		isLeftSame = leftDiff <= MaxPointDiff
		if isLeftSame:
			locationSameNum += 1

		heightDiff = abs(locationDict1["height"] - locationDict2["height"])
		isHeightSame = heightDiff <= MaxPointDiff
		if isHeightSame:
			locationSameNum += 1

		if locationSameNum >= MinSamePointNum:
			# at least 3 dimension of location is same, consider as item is same
			isLocationSame = True

		return isLocationSame

	def checkStrSimilarRatio(self, str1, str2):
		"""Check two str similar ratio

		Args:
			str1 (str): str 1
			str2 (str): str 2
		Returns:
			float
		Raises:
		Examples:
			1
				Input: 'XP:8400134506246', 'eP:840013450624'
				Output: 0.9032258064516129
			1
				Input: '60/660', '1370/1370'
				Output: 0.4
		"""
		matcher = SequenceMatcher(None, str1, str2)
		simimarRatio = matcher.ratio()
		return simimarRatio

	def checkSameWords(self, wordsInfoDict1, wordsInfoDict2):
		"""Check whether two words is same
			logic:
				same str
				same location

		Args:
			wordsInfoDict1 (dict): words 1 info dict
			wordsInfoDict2 (dict): words 1 info dict
		Returns:
			bool
		Raises:
		Examples:
			1
				input:
					wordsInfoDict1: {'chars': [{...}], 'location': {'height': 38, 'left': 23, 'top': 21, 'width': 37}, 'words': '战'}
					wordsInfoDict2: {'chars': [{...}], 'location': {'height': 38, 'left': 22, 'top': 21, 'width': 38}, 'words': '战'}
				output: True
			2
				input
					{'chars': [{...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, ...], 'location': {'height': 32, 'left': 812, 'top': 1001, 'width': 674}, 'words': '线情况,请在设直中勾选屏BOSS特效!'}
					{'chars': [{...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, ...], 'location': {'height': 33, 'left': 812, 'top': 1001, 'width': 672}, 'words': '线情况,请在设直中勾选屏敞BOSS特效!'}
				output: True
		"""
		# WordsMinSimilarRatio = 0.8
		WordsMinSimilarRatio = 0.9

		isStrSame = False
		isLocationSame = False

		wordsStr1 = wordsInfoDict1['words']
		wordsStr2 = wordsInfoDict2['words']
		isStrSame = wordsStr1 == wordsStr2
		if not isStrSame:
			simimarRatio = self.checkStrSimilarRatio(wordsStr1, wordsStr2) # 0.9032258064516129
			isStrSame = simimarRatio >= WordsMinSimilarRatio

		if isStrSame:
			locationDict1 = wordsInfoDict1['location']
			locationDict2 = wordsInfoDict2['location']
			isLocationSame = self.checkSameWordsLocation(locationDict1, locationDict2)

		isWordsSame = isStrSame and isLocationSame
		return isWordsSame

	def calcPageSimlarity(self,
			imgPath1=None,
			wordsResultJson1=None,
			imgPath2=None,
			wordsResultJson2=None,
		):
		"""Calculate the similarity ratio between page 1 and page 2

		Args:
			imgPath1 (str): screen image file path for page 1; default=None; if None, try use wordsResultJson1
			wordsResultJson1 (dict): baidu OCR result dict for page 1; if None, will auto generate from imgPath1
			imgPath2 (str): screen image file path for page 2; default=None; if None, try use wordsResultJson2
			wordsResultJson2 (dict): baidu OCR result dict for page 2; if None, will auto generate from imgPath2
		Returns:
			float, 0.0~1.0
		Raises:
		"""
		similarityRatio = 0.0

		if not wordsResultJson1:
			wordsResultJson1 = self.baiduImageToWords(imgPath1)

		if not wordsResultJson2:
			wordsResultJson2 = self.baiduImageToWords(imgPath2)

		"""
		{
			"log_id": 6218587667782385182,
			"direction": 0,
			"words_result_num": 32,
			"words_result": [
				{
					"chars": [
						{
						"char": "战",
						"location": { "width": 27, "top": 19, "left": 12, "height": 44 }
						}
					],
					"location": { "width": 44, "top": 19, "left": 12, "height": 44 },
					"words": "战"
				},
				{
					"chars": [
						{
							"char": "攻",
							"location": { "width": 30, "top": 0, "left": 241, "height": 48 }
						},
						{
							"char": "击",
							"location": { "width": 29, "top": 0, "left": 301, "height": 48 }
						},
						{
							"char": "力",
							"location": { "width": 29, "top": 0, "left": 361, "height": 48 }
						},
						{
							"char": ":",
							"location": { "width": 23, "top": 0, "left": 399, "height": 48 }
						},
						{
							"char": "1",
							"location": { "width": 23, "top": 0, "left": 430, "height": 48 }
						},
						{
							"char": "8",
							"location": { "width": 25, "top": 0, "left": 474, "height": 48 }
						},
						{
							"char": "8",
							"location": { "width": 25, "top": 0, "left": 519, "height": 48 }
						}
					],
					"location": { "width": 311, "top": 0, "left": 241, "height": 48 },
					"words": "攻击力:188"
				},

				...

				],
				"location": { "width": 314, "top": 1050, "left": 1011, "height": 28 },
				"words": "EXP:840013450624"
				}
			]
		}
		"""

		wordsResultDictList1 = wordsResultJson1['words_result']
		wordsResultDictList2 = wordsResultJson2['words_result']

		totalNum = 0
		sameNum = 0

		for eachWordsInfoDict1 in wordsResultDictList1:
			for eachWordsInfoDict2 in wordsResultDictList2:
				isWordsSame = self.checkSameWords(eachWordsInfoDict1, eachWordsInfoDict2)
				if isWordsSame:
					sameNum += 1
					break

			totalNum += 1

		if totalNum > 0:
			similarityRatio = sameNum / totalNum

		return similarityRatio

	def checkSamePage(self,
			imgPath1=None,
			wordsResultJson1=None,
			imgPath2=None,
			wordsResultJson2=None,
		):
		"""Check whether page 1 and page 2 is same or not

		Args:
			imgPath1 (str): screen image file path for page 1; default=None; if None, try use wordsResultJson1
			wordsResultJson1 (dict): baidu OCR result dict for page 1; if None, will auto generate from imgPath1
			imgPath2 (str): screen image file path for page 2; default=None; if None, try use wordsResultJson2
			wordsResultJson2 (dict): baidu OCR result dict for page 2; if None, will auto generate from imgPath2
		Returns:
			bool
		Raises:
		"""
		CfgSamePageMinRatio = 0.8 # 80%
		# CfgSamePageMinRatio = 0.9 # 90%

		isSamePage = False

		similarityRatio = self.calcPageSimlarity(imgPath1, wordsResultJson1, imgPath2, wordsResultJson2)
		if similarityRatio >= CfgSamePageMinRatio:
			isSamePage = True

		return isSamePage

	def checkExistInScreen(self,
			imgPath=None,
			wordsResultJson=None,
			mandatoryStrList=[],
			mandatoryMinMatchCount=0,
			optionalStrList=[],
			# optionalMinMatchCount=2,
			optionalMinMatchCount=1,
			isRespFullInfo=False
		):
		"""Check whether include mandatory/optional str in current screen or not

		Args:
			imgPath (str): current screen image file path; default=None; if None, will auto get current scrren image
			wordsResultJson (dict): baidu OCR result dict; if None, will auto generate from imgPath
			mandatoryStrList (list): mandatory str, at least match `mandatoryMinMatchCount`, or all must match if `mandatoryMinMatchCount`=0
			mandatoryMinMatchCount (int): minimal match count for mandatory list
			optionalStrList (list): optional str, some may match
			optionalMinMatchCount (int): for `optionalStrList`, the minimal match count, consider to match or not
			isRespFullInfo (bool): return full info or not, full info means match location result and imgPath
		Returns:
			matched result
				isRespFullInfo=False -> bool
				isRespFullInfo=True -> tuple: (isExist, respMatchLocation, imgPath, wordsResultJson)
		Raises:
		"""
		if not wordsResultJson:
			if not imgPath:
				imgPath = self.getCurScreenshot()

			wordsResultJson = self.baiduImageToWords(imgPath)

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
		allResultDict, _ = self.isWordsInCurScreen(allStrList, imgPath=imgPath, wordsResultJson=wordsResultJson, isMatchMultiple=True)
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
			logging.debug("mandatoryStrList=%s, optionalStrList=%s -> isExist=%s, respMatchLocation=%s, imgPath=%s, wordsResultJson=%s", 
				mandatoryStrList, optionalStrList, isExist, respMatchLocation, imgPath, wordsResultJson)
			# return (isExist, respMatchLocation, imgPath)
			return (isExist, respMatchLocation, imgPath, wordsResultJson)
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
			imgPath = self.getCurScreenshot()

		checkResult = self.checkExistInScreen(
			imgPath=imgPath,
			optionalStrList=strList,
			optionalMinMatchCount=1,
			isRespFullInfo=isRespFullInfo,
		)
		if isRespFullInfo:
			isExistAny, matchResult, imgPath, wordsResultJson = checkResult
			logging.debug("isExistAny=%s, matchResult=%s, imgPath=%s for %s", isExistAny, matchResult, imgPath, strList)
			return (isExistAny, matchResult, imgPath, wordsResultJson)
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
			imgPath = self.getCurScreenshot()
		checkResult = self.checkExistInScreen(imgPath=imgPath, mandatoryStrList=strList, isRespFullInfo=isRespFullInfo)
		if isRespFullInfo:
			isExistAll, matchResult, imgPath, wordsResultJson = checkResult
			logging.debug("isExistAll=%s, matchResult=%s, imgPath=%s for %s", isExistAll, matchResult, imgPath, strList)
			return (isExistAll, matchResult, imgPath, wordsResultJson)
		else:
			isExistAll = checkResult
			logging.debug("isExistAll=%s, for %s", isExistAll, strList)
			return isExistAll


################################################################################
# Test
################################################################################

if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))