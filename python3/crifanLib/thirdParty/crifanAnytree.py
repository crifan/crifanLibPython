# Function: anytree related functions
# Author: Crifan Li
# Update: 20210626
# Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/thirdParty/crifanAnytree.py

import os
import json
import codecs

from anytree import Node, RenderTree
from anytree.exporter import DotExporter, JsonExporter


################################################################################
# Util Functions
################################################################################

def createFolder(folderFullPath):
    """
        create folder, even if already existed
        Note: for Python 3.2+
    """
    os.makedirs(folderFullPath, exist_ok=True)

def saveTextToFile(fullFilename, text, fileEncoding="utf-8"):
    """save text content into file"""
    with codecs.open(fullFilename, 'w', encoding=fileEncoding) as fp:
        fp.write(text)
        fp.close()

def saveJsonToFile(fullFilename, jsonValue, indent=2, fileEncoding="utf-8"):
    """
        save json dict into file
        for non-ascii string, output encoded string, without \\u xxxx
    """
    with codecs.open(fullFilename, 'w', encoding=fileEncoding) as jsonFp:
        json.dump(jsonValue, jsonFp, indent=indent, ensure_ascii=False)
        # logging.debug("Complete save json %s", fullFilename)

################################################################################
# Main
################################################################################

def dbgPrintTreeToText(curNode, rootFolder=None, subFolder=None, isPrintToConsole=True, isSaveToFile=False):
    """Debug: print current node to text structure, and save to text file

    Args:
        topNodeList (list): top node list
        rootFolder (str): output root folder. Default None. If None, use current folder from os.getcwd()
        subFolder (str): output sub folder
        isPrintToConsole (bool): whether print tree text structure to console
        isSaveToFile (bool): whether save tree text structure to text file
    Returns:
    Raises:
    """
    if isSaveToFile:
        allTreeStr = ""

    for pre, fill, node in RenderTree(curNode):
        # print("pre=%s,fill=%s,node=%s" % (pre, fill, node))
        curLineStr = "%s%s" % (pre, node.name)
        if isPrintToConsole:
            print(curLineStr)

        if isSaveToFile:
            allTreeStr += curLineStr + os.linesep

    if isSaveToFile:
        if not rootFolder:
            rootFolder = os.getcwd()

        if subFolder:
            outputFullPath = os.path.join(rootFolder, subFolder)
        else:
            outputFullPath = rootFolder
        createFolder(outputFullPath)

        outputTextFilename = "TreeText.txt"
        outputTextFullPath = os.path.join(outputFullPath, outputTextFilename)
        saveTextToFile(outputTextFullPath, allTreeStr)

def dbgPrintTreeToImage(inputNode, rootFolder=None, subFolder=None):
    """Debug: print tree relation to image
        for single (root) node: print to single relation image file
        for top node list: print each single top node to single relation image file

    Args:
        inputNode (Node/list): if Node, is single (noramlly root) tree node; if list, is tree top node list
        rootFolder (str): output root folder. Default None. If None, use current folder from os.getcwd()
        subFolder (str): output sub folder
    Returns:
    Raises:
    """
    if not rootFolder:
        rootFolder = os.getcwd()

    isTopNodeList = False
    if isinstance(inputNode, list):
        isTopNodeList = True
        topNodeList = inputNode
    else:
        currentNode = inputNode

    if subFolder:
        outputFolder = os.path.join(rootFolder, subFolder)
    else:
        outputFolder = rootFolder

    if isTopNodeList:
        topNodeSubFolder = "topNode"
        outputFolder = os.path.join(outputFolder, topNodeSubFolder)

    createFolder(outputFolder)

    if isTopNodeList:
        for curTopNode in topNodeList:
            curNodeRealtionFile = "TopNode_Relation_%s.png" % (curTopNode.name)
            curNodeRealtionImg = os.path.join(outputFolder, curNodeRealtionFile)
            # 'output/20210622/current/topNode/RelationTopNode_aaaaaaaa5522.png'
            print("Generating %s" % curNodeRealtionImg)
            DotExporter(curTopNode).to_picture(curNodeRealtionImg)
    else:
        allNodeOutputFilename = "AllNode_Relation.png"
        allNodeOutputFullPath = os.path.join(outputFolder, allNodeOutputFilename)
        print("Generating %s" % allNodeOutputFullPath)
        DotExporter(currentNode).to_picture(allNodeOutputFullPath)


def dbgPrintTreeToJson(curNode, outputFile=None, prevCallback=None, postCallback=None):
    """Debug: print tree relation to image
        for single (root) node: print to single relation image file
        for top node list: print each single top node to single relation image file

    Args:
        curNode (Node): current tree node
        outputFile (str): output file
        prevCallback (function): function to call before print to json. Such as convert Timestamp to str
        postCallback (function): function to call after print. Such as convert back str to Timestamp
    Returns:
    Raises:
    """
    if not outputFile:
        outputFile = "AllNode.json"

    if prevCallback:
        prevCallback(curNode)

    print("Output to json %s ..." % outputFile)

    # crete folder to avoid later export json failed
    curOutputFolder = os.path.dirname(outputFile)
    if curOutputFolder:
        createFolder(curOutputFolder)

    jsonExporter = JsonExporter(indent=2, sort_keys=True)
    treeJsonStr = jsonExporter.export(curNode)
    treeJson = json.loads(treeJsonStr)

    saveJsonToFile(outputFile, treeJson)

    if postCallback:
        postCallback(curNode)

def dbgPrintTree(curNode, subFolder=None):
    """Debug: print tree, to text + json + image

    Args:
        curNode (Node): current tree node
        subFolder (str): sub folder to save text/json/image file
    Returns:
    Raises:
    """
    dbgPrintTreeToText(curNode, subFolder=subFolder)
    dbgPrintTreeToImage(curNode, subFolder=subFolder)
    dbgPrintTreeToJson(curNode, subFolder=subFolder)
