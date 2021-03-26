"""
Filename: baiduOcr.py
Function: simple version of https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/thirdParty/crifanBaiduOcr.py
Version: 20210326
Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/thirdParty/crifanBaiduOcr_simple.py
"""

import re
import base64
import requests
import time
import logging
from collections import OrderedDict

################################################################################
# Internal Function
################################################################################

def readBinDataFromFile(filePath):
	"""Read binary data from file

	Args:
		filePath (str): file path
	Returns:
		bytes, file binary data
	Raises:
	"""
	binaryData = None
	try:
		readFp = open(filePath, "rb")
		binaryData = readFp.read()
		readFp.close()
	except:
		binaryData = None

	return binaryData

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

	def imageToWords(self, imagePath=None, imageBytes=None):
		"""Detect text from image using Baidu OCR api

		Args:
			imagePath (str): image path
			imageBytes (bytes): image bytes
		Returns:
			baidu OCR response words_result (json)
		Raises:
		"""

		# # Note: if using un-paid = free baidu api, need following wait sometime to reduce: qps request limit
		# time.sleep(0.15)

		respWordsResutJson = ""

		# 读取图片二进制数据
		if not imageBytes:
			imageBytes = readBinDataFromFile(imagePath)

		encodedImgData = base64.b64encode(imageBytes)

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

		logging.debug("baidu OCR: imgage=%s -> respJson=%s", imagePath, respJson)

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
				# foundCurWords = re.search(curInputWords, eachWords)
				foundCurWords = re.search(curInputWords, eachWords, re.I)
				if foundCurWords:
					curMatchedResultList.append(eachWordsResult)
					if not isMatchMultiple:
						break

			orderedMatchedResultDict[curInputWords] = curMatchedResultList
		return orderedMatchedResultDict

	def isStrInImage(self,
		strOrStrList,
		imgPath=None,
		imgBytes=None,
		wordsResultJson=None,
		isMatchMultiple=True,
		isRespShortInfo=False
	):
		"""Found words in current screen

		Args:
			strOrStrList (str/list): single input str or str list
			imgPath (str): image file path
			imgBytes (bytes): image file binary data; default=None; if None, will get from imgPth
			wordsResultJson (dict): baidu OCR result dict; if None, will get from imgPath
			isMatchMultiple (bool): for each single str, to match multiple output or only match one output; default=True
			isRespShortInfo (bool): return simple=short=nomarlly bool or list[bool] info or return full matched result info
		Returns:
			matched result, type=bool/list/dict/tuple, depends on diffrent condition
		Raises:
		"""
		retValue = None

		if not wordsResultJson:
			wordsResultJson = self.imageToWords(imgPath, imgBytes)

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
