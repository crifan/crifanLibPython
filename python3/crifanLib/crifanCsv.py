#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanCsv.py
Function: crifanLib's csv related functions.
Version: 20210119
Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/crifanCsv.py
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20210119"
__copyright__ = "Copyright (c) 2021, Crifan Li"
__license__ = "GPL"


import codecs
import csv


################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanCsv"

################################################################################
# Global Variable
################################################################################

################################################################################
# Internal Function
################################################################################


################################################################################
# Cookie Function
################################################################################

def loadCsvFromFile(csvFilePath, fileEncoding="utf-8-sig", isReturnDictList=True):
    """read data from csv file

    Args:
        csvFilePath (str): full csv file path
        fileEncoding (str): file encoding, default to 'utf-8-sig'. utf-8-sig can auto remove '\ufeff' if present
        isReturnDictList (bool): return data is row dict list or tuple(header list, row list list)
    Returns:
        isReturnDictList=True  -> csv row dict list
        isReturnDictList=False -> (csv header list, csv row data list)
    Raises:
    """
    csvDictList = []

    csvHeaderList = []
    csvRowListList = []

    with codecs.open(csvFilePath, "r", encoding=fileEncoding) as csvFp:
        csvReader = csv.reader(csvFp)
        csvHeaderList = next(csvReader)
        print("csvHeaderList=%s" % csvHeaderList)
        # <class 'list'>: ['url', '品牌', '子品牌', '车型', '车系']
        # ['appName', 'pkgName', 'authorName', 'categoryName', 'appDownCount', 'apkUrl', 'detailUrl', 'searchKeyword']
        for eachRowList in csvReader:
            # print("eachRowList=%s" % eachRowList)
            # eachRowList=['https://car.autohome.com.cn/pic/series-s19501/3548.html#pvareaid=2042220', 'Elemental', 'Elemental', '2014款 基本型', 'Elemental RP1']
            # eachRowList=['传奇世界手游', 'com.tencent.cqsj', '盛大游戏', '网络游戏', '2577672', 'https://imtt.dd.qq.com/16891/apk/6B6261E845EB53DF06F6DFBE884B61C8.apk?fsname=com.tencent.cqsj_3.6.1.20_3006.apk&csr=1bbd', 'https://sj.qq.com/myapp/detail.htm?apkName=com.tencent.cqsj', '传奇']
            csvRowListList.append(eachRowList)

    if isReturnDictList:
        for eachRowList in csvRowListList:
            curRowDict = {}
            for curIdx, curHeader in enumerate(csvHeaderList):
                curRowValue = eachRowList[curIdx]
                curRowDict[curHeader] = curRowValue

            csvDictList.append(curRowDict)

        return csvDictList
    else:
        return csvHeaderList, csvRowListList

def saveToCsvByDictList(csvDictList, outputFilePath):
    # generate csv headers from dict list
    firstItemDict = csvDictList[0]
    csvHeaders = list(firstItemDict.keys())
    with codecs.open(outputFilePath, "w", "UTF-8") as outCsvFp:
        csvDictWriter = csv.DictWriter(outCsvFp, fieldnames=csvHeaders)

        # write header by inner function from fieldnames
        csvDictWriter.writeheader()

        for eachRowDict in csvDictList:
            csvDictWriter.writerow(eachRowDict)

def saveToCsvByHeaderAndList(csvHeaderList, csvRowListList, outputFilePath):
    with codecs.open(outputFilePath, "w", "UTF-8") as outCsvFp:
        csvWriter = csv.writer(outCsvFp)

        # write header from list
        csvWriter.writerow(csvHeaderList)

        # type1: write each row
        # for eachRowList in csvRowListList:
        #   csvWriter.writerow(eachRowList)

        # type2: write all rows
        csvWriter.writerows(csvRowListList)

################################################################################
# Test
################################################################################


if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))