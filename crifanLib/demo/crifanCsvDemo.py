# Function: Demo how use python save/write list/dict to csv file
# Version: 20190404
# Author: Crifan Li

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crifanCsv import saveToCsvByHeaderAndList, saveToCsvByDictList

OutputFilenameByHeaderAndList = "OutputDemoData_ByHeaderAndList.csv"
OutputFilenameByDictList = "OutputDemoData_ByDictList.csv"

OutputCsvHeader = ["单词", "重复频率", "来源列表"]

curFile = os.path.abspath(__file__)
curFolder = os.path.dirname(curFile)

DemoRowListList = [
  ["a", 0.5, ['NewConcept', 'FamilyAndFriends']],
  ["about", 0.75, ['NewConcept', 'YLE', 'EverybodyUp']],
  ["above", 0.5, ['NewConcept', 'YLE']],
  ["abroad", 0.25, ['NewConcept']]
]

DemoDictList = [
  {
    "单词": "a",
    "重复频率": 0.5,
    "来源列表": ['NewConcept', 'FamilyAndFriends'],
  },
  {
    "单词": "about",
    "重复频率": 0.75,
    "来源列表": ['NewConcept', 'YLE', 'EverybodyUp'],
  },
  {
    "单词": "above",
    "重复频率": 0.5,
    "来源列表": ['NewConcept', 'YLE'],
  },
  {
    "单词": "abroad",
    "重复频率": 0.25,
    "来源列表": ['NewConcept'],
  },
]

def demoCsvOutput():
  # Demo1: save by list of each row item list
  fullFilePathByHeaderAndList = os.path.join(curFolder, OutputFilenameByHeaderAndList)
  saveToCsvByHeaderAndList(OutputCsvHeader, DemoRowListList, fullFilePathByHeaderAndList)

  # Demo1: save by list of dict, not need assign header
  fullFilePathByDictList = os.path.join(curFolder, OutputFilenameByDictList)
  saveToCsvByDictList(DemoDictList, fullFilePathByDictList)

  """
  单词,重复频率,来源列表
  a,0.5,"['NewConcept', 'FamilyAndFriends']"
  about,0.75,"['NewConcept', 'YLE', 'EverybodyUp']"
  above,0.5,"['NewConcept', 'YLE']"
  abroad,0.25,['NewConcept']
  """

if __name__ == "__main__":
  demoCsvOutput()
