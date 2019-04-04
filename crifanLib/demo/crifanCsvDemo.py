# Function: Demo how use python output list/dict to csv file
# Version: 20190404
# Author: Crifan Li

import os
import csv
import codecs

OutputFilename = "OutputDemoData.csv"
OutputFilename_utf8 = "OutputDemoData_utf8.csv"

OutputCsvHeader = ["Word", "DuplicatedRatio", "SourceList"]
OutputCsvHeader_utf8 = ["单词", "重复频率", "来源列表"]

curFile = os.path.abspath(__file__)
curFolder = os.path.dirname(curFile)

DemoDataList = [
  ["a", 0.5, ['NewConcept', 'FamilyAndFriends']],
  ["about", 0.75, ['NewConcept', 'YLE', 'EverybodyUp']],
  ["above", 0.5, ['NewConcept', 'YLE']],
  ["abroad", 0.25, ['NewConcept']]
]

def demoCsvOutput():
  fullOutputFilePath = os.path.join(curFolder, OutputFilename)

  # Demo1: write by row or allrows, of list, all ASCII
  with open(fullOutputFilePath, "w") as outCsvFp:
    csvWriter = csv.writer(outCsvFp)
    # write header from list
    csvWriter.writerow(OutputCsvHeader)

    # type1: write each row
    # for eachRowList in DemoDataList:
    #   csvWriter.writerow(eachRowList)

    # type2: write all rows
    csvWriter.writerows(DemoDataList)

    """
    Word,DuplicatedRatio,SourceList
    a,0.5,"['NewConcept', 'FamilyAndFriends']"
    about,0.75,"['NewConcept', 'YLE', 'EverybodyUp']"
    above,0.5,"['NewConcept', 'YLE']"
    abroad,0.25,['NewConcept']

    """

  # Demo2: write by row of dict, using utf-8 encoding to support non-ASCII
  fullOutputFilePath_utf8 = os.path.join(curFolder, OutputFilename_utf8)
  with codecs.open(fullOutputFilePath_utf8, "w", "UTF-8") as outCsvUtf8Fp:
    csvDictWriter = csv.DictWriter(outCsvUtf8Fp, fieldnames=OutputCsvHeader_utf8)

    # write header by inner function from fieldnames
    csvDictWriter.writeheader()

    for eachRowList in DemoDataList:
      eachRowDict = {
        "单词": eachRowList[0],
        "重复频率": eachRowList[1],
        "来源列表": eachRowList[2],
      }
      csvDictWriter.writerow(eachRowDict)

    """
    单词,重复频率,来源列表
    a,0.5,"['NewConcept', 'FamilyAndFriends']"
    about,0.75,"['NewConcept', 'YLE', 'EverybodyUp']"
    above,0.5,"['NewConcept', 'YLE']"
    abroad,0.25,['NewConcept']

    """

if __name__ == "__main__":
  demoCsvOutput()
