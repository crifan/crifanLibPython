#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanList.py
Function: crifanLib's list related functions.
Version: 20210511
Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/crifanList.py
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20210511"
__copyright__ = "Copyright (c) 2021, Crifan Li"
__license__ = "GPL"


# from . import crifanString
import crifanLib.crifanString
import crifanLib.crifanSystem


################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanList"

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
# List Function
################################################################################


################################################################################
# List
################################################################################


# Note: following set method not support complex list values
# def uniqueList(oldList):
#     """remove overlapped item in the list"""
#     # newList = []
#     # for x in oldList:
#     #     if x not in newList:
#     #         newList.append(x)
#     newSet = set(oldList)
#     newList = list(newSet)
#     return newList

def uniqueList(oldList):
    """unique list

    Args:
        oldList (list): old list
    Returns:
        uniqued new list
    Raises:
    """
    newList = []
    for curItem in oldList:
        if curItem not in newList:
            newList.append(curItem)
        # else:
        #     # for debug
        #     print("Duplicated %s" % curItem)
    return newList


def genListStr(listValue, encForUniVal="UTF-8", isRetainLastComma=False, delimiter=","):
    """
    generate string of values in list, separated by delimiter
    eg:
    input: ["20121202", "天平山赏红枫", "动物"]
    output: 20121202,天平山赏红枫,动物
    """
    # print "listValue=",listValue;

    generatedListStr = ""
    for eachValue in listValue:
        if crifanLib.crifanSystem.isPython2():
            if isinstance(eachValue, unicode):
                encodedStr = eachValue.encode(encForUniVal)
                generatedListStr += encodedStr
            else:
                generatedListStr += str(eachValue)
        else:
            generatedListStr += str(eachValue)

        generatedListStr += delimiter

    if (not isRetainLastComma):
        if (generatedListStr and (generatedListStr[-1] == delimiter)):
            # remove last ,
            generatedListStr = generatedListStr[:-1]
    return generatedListStr


def removeEmptyInList(list):
    """remove the empty ones in list"""
    newList = []
    for val in list:
        if val:
            newList.append(val)
    return newList


def filterList(listToFilter, listToCompare):
    """
        for listToFilter, remove the ones which is in listToCompare,
        also return the ones which is already exist in listToCompare
    :param listToFilter:
    :param listToCompare:
    :return:
    """
    filteredList = []
    existedList = []
    for singleOne in listToFilter:  # remove processed
        if (not (singleOne in listToCompare)):
            # omit the ones in listToCompare
            filteredList.append(singleOne)
        else:
            # record the already exist ones
            existedList.append(singleOne)
    return (filteredList, existedList)


def tupleListToDict(tupleList):
    """
        convert tuple list to dict value
        [(u'type', u'text/javascript'), (u'src', u'http://partner.googleadservices.com/gampad/google_service.js')]
        { u'type':u'text/javascript', u'src':u'http://partner.googleadservices.com/gampad/google_service.js' }
    :param tupleList:
    :return:
    """
    convertedDict = {}
    for eachTuple in tupleList:
        (key, value) = eachTuple
        convertedDict[key] = value
    return convertedDict

################################################################################
# Test
################################################################################



if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))