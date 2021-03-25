#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanDict.py
Function: crifanLib's dict related functions
Version: 20210325
Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/crifanDict.py
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20210325"
__copyright__ = "Copyright (c) 2021, Crifan Li"
__license__ = "GPL"


import sys
import re
import json
from collections import OrderedDict
import crifanLib.crifanSystem

################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanDict"

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
#  Function
################################################################################


def recursiveMergeDict(aDict, bDict):
    """
    Recursively merge dict a to b, return merged dict b
    Note: Sub dict and sub list's won't be overwritten but also updated/merged

    example:
(1) input and output example:
input:
{
  "keyStr": "strValueA",
  "keyInt": 1,
  "keyBool": true,
  "keyList": [
    {
      "index0Item1": "index0Item1",
      "index0Item2": "index0Item2"
    },
    {
      "index1Item1": "index1Item1"
    },
    {
      "index2Item1": "index2Item1"
    }
  ]
}

and

{
  "keyStr": "strValueB",
  "keyInt": 2,
  "keyList": [
    {
      "index0Item1": "index0Item1_b"
    },
    {
      "index1Item1": "index1Item1_b"
    }
  ]
}

output:

{
  "keyStr": "strValueB",
  "keyBool": true,
  "keyInt": 2,
  "keyList": [
    {
      "index0Item1": "index0Item1_b",
      "index0Item2": "index0Item2"
    },
    {
      "index1Item1": "index1Item1_b"
    },
    {
      "index2Item1": "index2Item1"
    }
  ]
}

(2) code usage example:
import copy
cDict = recursiveMergeDict(aDict, copy.deepcopy(bDict))

Note:
bDict should use deepcopy, otherwise will be altered after call this function !!!

    """
    aDictItems = None
    if crifanLib.crifanSystem.isPython2(): # is python 2
      aDictItems = aDict.iteritems()
    else: # is python 3
      aDictItems = aDict.items()

    for aKey, aValue in aDictItems:
      # print("------ [%s]=%s" % (aKey, aValue))
      if aKey not in bDict:
        bDict[aKey] = aValue
      else:
        bValue = bDict[aKey]
        # print("aValue=%s" % aValue)
        # print("bValue=%s" % bValue)
        if isinstance(aValue, dict):
          recursiveMergeDict(aValue, bValue)
        elif isinstance(aValue, list):
          aValueListLen = len(aValue)
          bValueListLen = len(bValue)
          bValueListMaxIdx = bValueListLen - 1
          for aListIdx in range(aValueListLen):
            # print("---[%d]" % aListIdx)
            aListItem = aValue[aListIdx]
            # print("aListItem=%s" % aListItem)
            if aListIdx <= bValueListMaxIdx:
              bListItem = bValue[aListIdx]
              # print("bListItem=%s" % bListItem)
              recursiveMergeDict(aListItem, bListItem)
            else:
              # print("bDict=%s" % bDict)
              # print("aKey=%s" % aKey)
              # print("aListItem=%s" % aListItem)
              bDict[aKey].append(aListItem)

    return bDict

def sortDictByKey(originDict):
    """
        Sort dict by key
    """
    originItems = originDict.items()
    sortedOriginItems = sorted(originItems)
    sortedOrderedDict = OrderedDict(sortedOriginItems)
    return sortedOrderedDict

def insertKeyValueAfterDictKey(curDict, afterKey, newKey, newValue):
    """Insert new key and new value after specific key

    Args:
        afterKey (str): name of after the key in dict
        newKey (str): new key to insert
        newValue (Any?): new value to insert
    Returns:
    Raises:
    """
    # keyList = curDict.keys()
    keyList = list(curDict.keys())
    keyMaxNum = len(keyList)
    keyMaxIdx = keyMaxNum - 1
    # valuesList = curDict.values()
    valuesList = list(curDict.values())
    afterKeyIndex = keyList.index(afterKey) # 6
    if afterKeyIndex < keyMaxIdx:
        toInsertIndex = afterKeyIndex + 1
        keyList.insert(toInsertIndex, newKey)
        valuesList.insert(toInsertIndex, newValue)
    else:
        keyList.append(newKey)
        valuesList.append(newValue)
    updatedDict = {}
    for keyIdx, eachKey in enumerate(keyList):
        eachValue = valuesList[keyIdx]
        updatedDict[eachKey] = eachValue
    return updatedDict

def removeJsonComment(jsonStr):
    """Remove comments from json string

    Args:
        jsonStr (str): json str with comments
    Returns:
        str
    Raises:
    Examples:
      {
        "key1": "value1", # line tail comment
        # whole line comment
        "key2": "value2" // line tail comment
        // whole line comment
      }
    """
    pureJsonStr = jsonStr

    # whole line with #
    #                 # International
    pureJsonStr = re.sub("^\s*#.*$\n+", "", pureJsonStr, flags=re.M)

    # whole line with //
    #     // "mode": "SINGLE",
    pureJsonStr = re.sub("^\s*//.*$\n+", "", pureJsonStr, flags=re.M)

    # line tail with #
    pureJsonStr = re.sub("\s+#.*$", "", pureJsonStr, flags=re.M)

    # line tail with //
    pureJsonStr = re.sub("\s+//.*$", "", pureJsonStr, flags=re.M)

    return pureJsonStr

def strToDict(dictRawStr):
    """Convert string to dict

    Args:
        dictRawStr (str): dict raw string (with comment, with True/False ...)
    Returns:
        dict
    Raises:
    """
    dictStr = removeJsonComment(dictRawStr)

    # True/False -> true, false
    dictStr = re.sub("\s*True\s*(,?)", "true\g<1>", dictStr)
    dictStr = re.sub("\s*False\s*(,?)", "false\g<1>", dictStr)

    curDict = json.loads(dictStr)

    return curDict


################################################################################
# Test
################################################################################

if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))