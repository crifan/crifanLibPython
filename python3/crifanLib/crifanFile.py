#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanFile.py
Function: crifanLib's file related functions.
Update: 20250428
Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/crifanFile.py
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20250428"
__copyright__ = "Copyright (c) 2025, Crifan Li"
__license__ = "GPL"

import os
import stat
import sys
import shutil
import codecs
import json
import re
import zipfile

try:
    import pysrt
except ImportError:
    print("need pysrt if using crifanFile functions: extractRawSubtitleList")

try:
    import chardet
except ImportError:
    print("need chardet if using crifanFile functions: extractRawSubtitleList")

# from . import crifanList
import crifanLib.crifanList

################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanFile"

################################################################################
# Global Variable
################################################################################
gVal = {
    'picSufChars': '',  # store the pic suffix char list
}

gConst = {
    # also belong to ContentTypes, more info can refer: http://kenya.bokee.com/3200033.html
    # here use Tuple to avoid unexpected change
    # note: for tuple, refer item use tuple[i], not tuple(i)
    'picSufList': ('bmp', 'gif', 'jpeg', 'jpg', 'jpe', 'png', 'tiff', 'tif'),
}

################################################################################
# Internal Function
################################################################################


def genSufList():
    """generate the suffix char list according to constant picSufList"""
    global gConst

    sufChrList = []
    for suffix in gConst['picSufList']:
        for c in suffix:
            sufChrList.append(c)

    sufChrList = crifanLib.crifanList.uniqueList(sufChrList)
    # sufChrList = uniqueList(sufChrList)
    sufChrList.sort()
    joinedSuf = ''.join(sufChrList)
    swappedSuf = joinedSuf.swapcase()
    wholeSuf = joinedSuf + swappedSuf

    return wholeSuf

################################################################################
# File Function
################################################################################

def isFileObject(fileObj):
    """"check is file like object or not"""
    if sys.version_info[0] == 2:
        return isinstance(fileObj, file)
    else:
        # for python 3:
        # has read() method for:
        # io.IOBase
        # io.BytesIO
        # io.StringIO
        # io.RawIOBase
        return hasattr(fileObj, 'read')

def saveJsonToFile(filePath, jsonValue, indent=2, fileEncoding="utf-8"):
    """
        save json dict into file
        for non-ascii string, output encoded string, without \\u xxxx
    """
    with codecs.open(filePath, 'w', encoding=fileEncoding) as jsonFp:
        json.dump(jsonValue, jsonFp, indent=indent, ensure_ascii=False)
        # logging.debug("Complete save json %s", filePath)

def loadJsonFromFile(filePath, fileEncoding="utf-8"):
    """load and parse json dict from file"""
    with codecs.open(filePath, 'r', encoding=fileEncoding) as jsonFp:
        jsonDict = json.load(jsonFp)
        # logging.debug("Complete load json from %s", filePath)
        return jsonDict

def saveTextToFile(filePath, text, fileEncoding="utf-8"):
    """save text content into file"""
    with codecs.open(filePath, 'w', encoding=fileEncoding) as fp:
        fp.write(text)
        fp.close()

def loadTextFromFile(filePath, fileEncoding="utf-8"):
    """load file text content from file"""
    with codecs.open(filePath, 'r', encoding=fileEncoding) as fp:
        allText = fp.read()
        # logging.debug("Complete load text from %s", filePath)
        return allText

def saveBytesToFile(filePath, dataBytes):
    """save bytes (binary data) into file"""
    saveOK = False
    try:
        # open a file, if not exist, create it
        savedBinFile = open(filePath, "wb")
        #print "savedBinFile=",savedBinFile
        savedBinFile.write(dataBytes)
        savedBinFile.close()
        saveOK = True
    except:
        saveOK = False
    return saveOK

def loadBytesFromFile(filePath):
    """Read binary data from file

    Args:
        filePath (str): file path
    Returns:
        bytes, file binary data
    Raises:
    """
    dataBytes = None
    try:
        readFp = open(filePath, "rb")
        dataBytes = readFp.read()
        readFp.close()
    except:
        dataBytes = None

    return dataBytes

def chmodAddX(someFile, isOnlySelf=True):
    """add file executable mode, like chmod +x

    Args:
        someFile (str): file full path
        isOnlySelf (bool): add executable permission, True for only for file owner, False for by everyone
    Returns:
        soup
    Raises:
    """
    if os.path.exists(someFile):
        if os.path.isfile(someFile):
            # add executable
            curState = os.stat(someFile)
            STAT_OWNER_EXECUTABLE = stat.S_IEXEC
            STAT_EVERYONE_EXECUTABLE = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            if isOnlySelf:
                executableMode = STAT_OWNER_EXECUTABLE
            else:
                executableMode = STAT_EVERYONE_EXECUTABLE
            newState = curState.st_mode | executableMode
            os.chmod(someFile, newState)

def isFileExistAndValid(filePath, fullFileSize=None):
    """Check file exist and valid or not

    Args:
        filePath (str): file path
        fullFileSize (int): full file size
    Returns:
        existed and valid (bool)
    Raises:
    Examples:
    """
    isExistFile = os.path.isfile(filePath)
    isValidFile = False
    if isExistFile:
        curFileSize = os.path.getsize(filePath) # 260900226
        if fullFileSize:
            isValidFile = curFileSize == fullFileSize
        else:
            isValidFile = curFileSize > 0
    isExistAndValid = isExistFile and isValidFile
    return isExistAndValid

def createEmptyFile(fullFilePath):
    """Create a empty file like touch

    Args:
        fullFilePath (str): full file path
    Returns:
        bool
    Raises:
    """
    folderPath = os.path.dirname(fullFilePath)
    # create folder if not exist
    if not os.path.exists(folderPath):
        # os.makedirs(folderPath, exist_ok=True)
        createFolder(folderPath)

    with open(fullFilePath, 'a'):
        # Note: not use 'w' for maybe conflict for others constantly writing to it
        os.utime(fullFilePath, None)

def updateFileTime(fileOrFolderPath, newAccessTime=None, newModificationTime=None, isAccessSameWithModif=True):
    """Update file access time and modification time

    Args:
        fileOrFolderPath (str): file or folder path
        newAccessTime (int): new file access time, float
        newModificationTime (int): new file modification time, float
        isAccessSameWithModif (bool): make access same with modification 
    Returns:
        None
    Raises:
    Examples:
        newModificationTime=1620549707.664307
    """
    if (not newAccessTime) and (not newModificationTime):
        return
    
    statInfo = os.stat(fileOrFolderPath)
    # print("statInfo=%s" % statInfo)
    # print("statInfo.st_info=%s" % statInfo.st_info)

    if not newAccessTime:
        oldAccessTime = statInfo.st_atime # 1619490904.6651974
        # print("oldAccessTime=%s" % oldAccessTime)
        newAccessTime = oldAccessTime

    if not newModificationTime:
        oldModificationTime = statInfo.st_mtime # 1617002149.62217
        # print("oldModificationTime=%s" % oldModificationTime)
        newModificationTime = oldModificationTime

    if isAccessSameWithModif:
        newAccessTime = newModificationTime

    os.utime(fileOrFolderPath, (newAccessTime, newModificationTime))

def unzipFile(zipFileFullPath, outputFolder):
    """
        unzip a zip file
    """
    with zipfile.ZipFile(zipFileFullPath, 'r') as zip_ref:
        zip_ref.extractall(outputFolder)

def zipFolder(toZipFolder, outputZipFile):
    """
        zip/compress a whole folder/directory to zip file
    """
    print("Zip for foler %s" % toZipFolder)
    with zipfile.ZipFile(outputZipFile, 'w', zipfile.ZIP_DEFLATED) as zipFp:
        for dirpath, dirnames, filenames in os.walk(toZipFolder):
            # print("%s" % ("-"*80))
            # print("dirpath=%s, dirnames=%s, filenames=%s" % (dirpath, dirnames, filenames))
            # print("Folder: %s, Files: %s" % (dirpath, filenames))
            for curFileName in filenames:
                # print("curFileName=%s" % curFileName)
                curFilePath = os.path.join(dirpath, curFileName)
                # print("curFilePath=%s" % curFilePath)
                fileRelativePath = os.path.relpath(curFilePath, toZipFolder)
                # print("fileRelativePath=%s" % fileRelativePath)
                # print("  %s" % fileRelativePath)
                zipFp.write(curFilePath, arcname=fileRelativePath)
    print("Completed zip file %s" % outputZipFile)

def removeFile(filePath):
  """remove file"""
  if os.path.exists(filePath):
    os.remove(filePath)

################################################################################
# Folder Function
################################################################################

def deleteFolder(folderFullPath):
    """
        delete folder
        Note:makesure folder is already existed
    """
    if os.path.exists(folderFullPath):
        shutil.rmtree(folderFullPath)

def createFolder(folderFullPath):
    """
        create folder, even if already existed
        Note: for Python 3.2+
    """
    os.makedirs(folderFullPath, exist_ok=True)

def listSubfolderFiles(subfolder, isIncludeFolder=True, isRecursive=False):
    """os.listdir recursively

    Args:
        subfolder (str): sub folder path
        isIncludeFolder (bool): whether is include folder. Default is True. If True, result contain folder
        isRecursive (bool): whether is recursive, means contain sub folder. Default is False
    Returns:
        list of str
    Raises:
    """
    allSubItemList = []
    curSubItemList = os.listdir(path=subfolder)
    for curSubItem in curSubItemList:
        curSubItemFullPath = os.path.join(subfolder, curSubItem)
        if os.path.isfile(curSubItemFullPath):
            allSubItemList.append(curSubItemFullPath)
        else:
            if isIncludeFolder:
                if os.path.isdir(curSubItemFullPath):
                    subSubItemList = listSubfolderFiles(curSubItemFullPath, isIncludeFolder, isRecursive)
                    allSubItemList.extend(subSubItemList)

    if isIncludeFolder:
        allSubItemList.append(subfolder)

    return allSubItemList

################################################################################
# File and Folder Function
################################################################################

def getFileFolderSize(fileOrFolderPath):
    """get size for file or folder"""
    totalSize = 0

    if not os.path.exists(fileOrFolderPath):
        return totalSize

    if os.path.isfile(fileOrFolderPath):
        totalSize = os.path.getsize(fileOrFolderPath) # 5041481
        return totalSize

    if os.path.isdir(fileOrFolderPath):
        with os.scandir(fileOrFolderPath) as dirEntryList:
            for curSubEntry in dirEntryList:
                curSubEntryFullPath = os.path.join(fileOrFolderPath, curSubEntry.name)
                if curSubEntry.is_dir():
                    curSubFolderSize = getFileFolderSize(curSubEntryFullPath) # 5800007
                    totalSize += curSubFolderSize
                elif curSubEntry.is_file():
                    curSubFileSize = os.path.getsize(curSubEntryFullPath) # 1891
                    totalSize += curSubFileSize

        return totalSize


def formatSize(sizeInBytes, decimalNum=1, isUnitWithI=False, sizeUnitSeperator=""):
    """Format size number to human readable string
        refer:
            https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size

    Args:
        sizeInBytes (int): size in bytes
        decimalNum (int): decimal part digit number
        isUnitWithI (bool): the unit suffix is include i or not, such as 'KB' or 'KiB'
        sizeUnitSeperator (str): seperator between size number part and uint part, such as '3.7KB' or '3.7 KB'
    Returns:
        str
    Raises:
    Examples:
        3746 -> 3.7KB
        87533 -> 85.5KiB
        98654 -> 96.3 KB
        352 -> 352.0B
        76383285 -> 72.84MB
        763832854988542 -> 694.70TB
        763832854988542665 -> 678.4199PB
    """
    # https://en.wikipedia.org/wiki/Binary_prefix#Specific_units_of_IEC_60027-2_A.2_and_ISO.2FIEC_80000
    # K=kilo, M=mega, G=giga, T=tera, P=peta, E=exa, Z=zetta, Y=yotta
    sizeUnitList = ['','K','M','G','T','P','E','Z']
    largestUnit = 'Y'

    if isUnitWithI:
        sizeUnitListWithI = []
        for curIdx, eachUnit in enumerate(sizeUnitList):
            unitWithI = eachUnit
            if curIdx >= 1:
                unitWithI += 'i'
            sizeUnitListWithI.append(unitWithI)

        # sizeUnitListWithI = ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']
        sizeUnitList = sizeUnitListWithI

        largestUnit += 'i'

    suffix = "B"
    decimalFormat = "." + str(decimalNum) + "f" # ".1f"
    finalFormat = "%" + decimalFormat + sizeUnitSeperator + "%s%s" # "%.1f%s%s"
    sizeNum = sizeInBytes
    for sizeUnit in sizeUnitList:
        if abs(sizeNum) < 1024.0:
            return finalFormat % (sizeNum, sizeUnit, suffix)
        sizeNum /= 1024.0
    return finalFormat % (sizeNum, largestUnit, suffix)


################################################################################
# Filename Function
################################################################################

def getPicSufList():
    """get supported picture suffix list"""
    return gConst['picSufList']


def getPicSufChars():
    """get supported picture suffix chars"""
    if not gVal['picSufChars']:
        gVal['picSufChars'] = genSufList()

    return gVal['picSufChars']

def getBasename(fullFilename):
    """
    get base filename

    Examples:
        xxx.exe          -> xxx.exe
        xxx              -> xxx
        Mac/Linux:
            your/path/xxx.py -> xxx.py
        Windows:
            your\path\\xxx.py -> xxx.py
    """

    return os.path.basename(fullFilename)

def getFilenameNoPointSuffix(curFilePath):
    """Get current filename without point and suffix

    Args:
        curFilePath (str): current file path. Normally can use __file__
    Returns:
        str, file name without .xxx
    Raises:
    Examples:
        input: /Users/xxx/pymitmdump/mitmdumpOtherApi.py 
        output: mitmdumpOtherApi
    """
    root, pointSuffix = os.path.splitext(curFilePath)
    curFilenameNoSuffix = root.split(os.path.sep)[-1]
    return curFilenameNoSuffix

def getPyFolder(inputPyFile):
    """Get input python file folder == current folder

    Usage:
      curFolder = getPyFolder(__file__)

    Example:
      /xxx/parseBrJumpOffset/parseBrJumpOffset.py -> /xxx/parseBrJumpOffset/
    """
    curPyFolder = os.path.dirname(inputPyFile)
    # print("curPyFolder=%s" % curPyFolder) # curPyFolder=/xxx/parseBrJumpOffset
    curPyFolderFullPath = os.path.abspath(curPyFolder)
    # print("curPyFolderFullPath=%s" % curPyFolderFullPath) # curPyFolderFullPath=/xxx/parseBrJumpOffset
    return curPyFolderFullPath

def getFileSuffix(filename):
    """
        get file suffix from file name
        no dot/period, no space/newline, makesure lower case

        "xxx.mp3" -> "mp3"
        "xxx.pdf" -> "pdf"
        "xxx.mp3 " -> "mp3"
        "xxx.JPg" -> "jpg"

    :param filename:
    :return:
    """
    fileSuffix = ""

    if filename:
        name, extension = os.path.splitext(filename)
        fileSuffix = extension # .mp3

    if fileSuffix:
        # remove leading dot/period
        fileSuffix = fileSuffix[1:] # mp3

    if fileSuffix:
        # remove ending newline or space
        fileSuffix = fileSuffix.strip()

    if fileSuffix:
        # convert JPg to jpg
        fileSuffix = fileSuffix.lower()

    return fileSuffix


def removeSuffix(fileBasename):
    """
    remove file suffix

    Examples:
        xxx.exe -> xxx
        xxx -> xxx
    """

    splitedTextArr = os.path.splitext(fileBasename)
    filenameRemovedSuffix = splitedTextArr[0]
    return filenameRemovedSuffix


def getInputFilename():
    """
    get input filename, from argv

    Examples:
        AutoOrder.py -> AutoOrder.py
        python AutoOrder.py -> AutoOrder.py
        python AutoOrder/AutoOrder.py -> AutoOrder/AutoOrder.py
    """

    argvList = sys.argv
    # print "argvList=%s"%(argvList)
    return argvList[0]


def getInputFileBasename(inputFilename = None):
    """
    get input file's base name

    Examples:
        AutoOrder.py -> AutoOrder.py
        AutoOrder/AutoOrder.py -> AutoOrder.py
    """

    curInputFilename = getInputFilename()

    if inputFilename :
        curInputFilename = inputFilename

    # print "curInputFilename=%s"%(curInputFilename)
    inputBasename = getBasename(curInputFilename)
    # print "inputBasename=%s"%(inputBasename)
    return inputBasename


def getInputFileBasenameNoSuffix():
    """
    get input file base name without suffix

    Examples:
        AutoOrder.py -> AutoOrder
        AutoOrder/AutoOrder.py -> AutoOrder
    """

    inputFileBasename = getInputFileBasename()
    basenameRemovedSuffix = removeSuffix(inputFileBasename)
    return basenameRemovedSuffix

def findNextNumberFilename(curFilename):
    """Find the next available filename from current name

    Args:
        curFilename (str): current filename
    Returns:
        next available (not existed) filename
    Raises:
    Examples:
        (1) 'crifanLib/demo/input/image/20201219_172616_drawRect_40x40.jpg'
            not exist -> 'crifanLib/demo/input/image/20201219_172616_drawRect_40x40.jpg'
        (2) 'crifanLib/demo/input/image/20191219_172616_drawRect_40x40.jpg'
            exsit -> next until not exist 'crifanLib/demo/input/image/20191219_172616_drawRect_40x40_3.jpg'
    """
    newFilename = curFilename

    newPathRootPart, pointSuffix = os.path.splitext(newFilename)
    # 'crifanLib/demo/input/image/20191219_172616_drawRect_40x40_1'
    filenamePrefix = newPathRootPart
    while os.path.exists(newFilename):
        newTailNumberInt = 1
        foundTailNumber = re.search("^(?P<filenamePrefix>.+)_(?P<tailNumber>\d+)$", newPathRootPart)
        if foundTailNumber:
            tailNumberStr = foundTailNumber.group("tailNumber") # '1'
            tailNumberInt = int(tailNumberStr)
            newTailNumberInt = tailNumberInt + 1 # 2
            filenamePrefix = foundTailNumber.group("filenamePrefix") # 'crifanLib/demo/input/image/20191219_172616_drawRect_40x40'
        # existed previously saved, change to new name
        newPathRootPart = "%s_%s" % (filenamePrefix, newTailNumberInt)
        # 'crifanLib/demo/input/image/20191219_172616_drawRect_40x40_2'
        newFilename = newPathRootPart + pointSuffix
        # 'crifanLib/demo/input/image/20191219_172616_drawRect_40x40_2.jpg'

    return newFilename

################################################################################
# SRT Subtitle Parsing
################################################################################

def extractRawSubtitleList(subtitleFullPath, srtEncodingConfidenceThreshold = 0.8, defaultEncoding="utf-8"):
    """
        extract subtitle text file to raw subtitle list of dict {start, end, text},
        and support auto detect srt file encoding
    """

    getSubOk = False
    rawSubtitleListOrErrMsg = "Unknown Error"

    with open(subtitleFullPath, 'rb') as subtitleFp:
        fileContentStr = subtitleFp.read()
        detectedResult = chardet.detect(fileContentStr)
        # logging.debug("detectedResult=%s", detectedResult)
        fileEncoding = defaultEncoding
        if detectedResult["confidence"] >= srtEncodingConfidenceThreshold:
            fileEncoding = detectedResult["encoding"] # 'UTF-8-SIG'
        # logging.debug("fileEncoding=%s", fileEncoding)

        try:
            rawSubtitleList = pysrt.open(subtitleFullPath, encoding=fileEncoding)
            rawSubtitleListOrErrMsg = rawSubtitleList
            getSubOk = True
        except Exception as openSrtException:
            rawSubtitleListOrErrMsg = str(openSrtException)
            # logging.debug("Error %s of pysrt.open %s", rawSubtitleListOrErrMsg, subtitleFullPath)

    return getSubOk, rawSubtitleListOrErrMsg


################################################################################
# Test
################################################################################


def testFile():
    filenameNoSuffix = getInputFileBasenameNoSuffix()
    print("filenameNoSuffix=%s" % filenameNoSuffix) #filenameNoSuffix=crifanFile


if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))

    testFile()