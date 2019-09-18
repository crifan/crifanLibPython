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

from crifanDict import sortDictByKey

def demoSortDictByKey():
  originDict = {
    "c": "abc",
    "a": 1,
    "b": 2
  }
  print("originDict=%s" % originDict)
  # originDict={'c': 'abc', 'a': 1, 'b': 2}
  sortedOrderedDict = sortDictByKey(originDict)
  print("sortedOrderedDict=%s" % sortedOrderedDict)
  # sortedOrderedDict=OrderedDict([('a', 1), ('b', 2), ('c', 'abc')])

if __name__ == "__main__":
  demoSortDictByKey()
