import sys
import os
curFolder = os.path.abspath(__file__)
parentFolder = os.path.dirname(curFolder)
parentParentFolder = os.path.dirname(parentFolder)
parentParentParentFolder = os.path.dirname(parentParentFolder)
sys.path.append(curFolder)
sys.path.append(parentFolder)
sys.path.append(parentParentFolder)
sys.path.append(parentParentParentFolder)

import datetime
from crifanBaiduOcr import *

def testBaiduOcr():
  # init OCR
  initOcr()

  screenImgPath = getCurScreen()
  respJson = baiduImageToWords(screenImgPath)
  wordsResultNum = respJson["words_result_num"]
  if wordsResultNum > 0:
    allWordsEmpty = False
  
  calculatedLocation = self.calcWordsLocation(eachInputWords, eachWordsMatchedResult)

  curCenterX, curCenterY = self.locationToCenterPos(eachLocation)

  matchedResultDict = self.isWordsInResult(wordsResultJson, wordsOrWordsList, isMatchMultiple)

  allResultDict, imgPath = self.isWordsInCurScreen(allStrList, imgPath, isMatchMultiple=True)

  curScreenWords = self.getWordsInCurScreen()

  checkResult = self.checkExistInScreen(imgPath=eachAutoDoingImgPath, optionalStrList=autoDoingStrList, isRespFullInfo=True)
  checkResult = self.checkExistInScreen(
    imgPath=imgPath,
    mandatoryStrList=mandatoryList,
    mandatoryMinMatchCount=1,
    optionalStrList=optionalList,
    optionalMinMatchCount=minOptionalMatchCount,
    isRespFullInfo=isRespFullInfo,
  )
  matchResult = self.checkExistInScreen(
    imgPath=eachTestImgPath,
    optionalStrList=loadingStrList,
    optionalMinMatchCount=1,
    isRespFullInfo=True
  )
  checkResult = self.checkExistInScreen(imgPath=jianLingLongImgPath, mandatoryStrList=mandatoryList, optionalStrList=optionalList, isRespFullInfo=True)
  isHome, matchResult, imgPath = self.checkExistInScreen(
    mandatoryStrList=mandatoryList,
    mandatoryMinMatchCount=1,
    optionalStrList=optionalList,
    isRespFullInfo=True,
  )

  isExist, matchResult, imgPath = self.isExistAnyStr(buttonStrList, imgPath=imgPath, isRespFullInfo=True)
  respResult = self.isExistAnyStr(mandatoryList, imgPath=imgPath, isRespFullInfo=isRespFullInfo)
  isLaunch, _, imgPath = self.isExistAnyStr(lanuchStrList, isRespFullInfo=True)
  respBoolOrTuple = self.isExistAnyStr(gotoPayStrList, isRespFullInfo=isRespLocation)
  self.isExistAllStr(realPayStrList, isRespFullInfo=isRespLocation)



if __name__ == "__main__":
  testBaiduOcr()
