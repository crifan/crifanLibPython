# Function: Evernote related functions
# Author: Crifan Li
# Update: 20210114
# Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/thirdParty/crifanEvernote.py

import sys
import re
import logging
# from bs4 import BeautifulSoup

sys.path.append("lib")
sys.path.append("libs/evernote-sdk-python3/lib")
from libs.crifan import utils

# import evernote.edam.userstore.constants as UserStoreConstants
# import evernote.edam.noteStore as NoteStore
# import evernote.edam.type.ttypes as Types

# from evernote.edam import *
from evernote import *
from evernote.api import *
from evernote.edam.limits import *
from evernote.edam.type import *
from evernote.edam.notestore.NoteStore import *
from evernote.edam.userstore import *

import evernote.edam.type.ttypes as Types
from evernote.edam.error.ttypes import EDAMUserException, EDAMNotFoundException

# from evernote.edam.notestore.ttypes import *
from evernote.edam.notestore.ttypes import NotesMetadataResultSpec

# from evernote.api.client import *
from evernote.api.client import EvernoteClient

# from evernote.edam.notestore import *
from evernote.edam.notestore import NoteStore

# from evernote.edam.type.ttypes import *
from evernote.edam.type.ttypes import NoteSortOrder


# from evernote.edam.userstore.constants import *
from evernote.edam.userstore.constants import EDAM_VERSION_MAJOR, EDAM_VERSION_MINOR


class crifanEvernote(object):
    """Operate Evernote Yinxiang note via python

        (0) most refer
            Thrift module: NoteStore
            https://dev.evernote.com/doc/reference/NoteStore.html

            Evernote API: All declarations
            https://dev.yinxiang.com/doc/reference/

            Evernote API: Module: Types
            https://dev.yinxiang.com/doc/reference/Types.html

        (1) get token

            Developer Tokens - 印象笔记开发者
            https://dev.yinxiang.com/doc/articles/dev_tokens.php

            首页
            http://sandbox.yinxiang.com

            登录
            https://sandbox.yinxiang.com/Login.action?offer=www_menu

            Web版 主页
            https://sandbox.yinxiang.com/Home.action?_sourcePage=q4oOUtrE7iDiMUD9T65RG_YvRLZ-1eYO3fqfqRu0fynRL_1nukNa4gH1t86pc1SP&__fp=RRdnsZFJxJY3yWPvuidLz-TPR6I9Jhx8&hpts=1576292029828&showSwitchService=true&usernameImmutable=false&login=&login=登录&login=true&username=green-waste%40163.com&hptsh=10h%2BVHVzIGiSBhmRcxjMg47ZqdQ%3D#n=5b863474-107d-43e0-8087-b566329b24ab&s=s1&ses=4&sh=2&sds=5&

            获取token
            https://sandbox.yinxiang.com/api/DeveloperToken.action
            ->
            NoteStore URL: https://sandbox.yinxiang.com/shard/s1/notestore

        (2) official doc

            yinxiang:
                核心概念 - 印象笔记开发者
                https://dev.yinxiang.com/doc/articles/core_concepts.php

                数据模型 - 印象笔记开发者
                https://dev.yinxiang.com/doc/articles/data_structure.php

                错误处理 - 印象笔记开发者
                https://dev.yinxiang.com/doc/articles/error_handling.php

                在沙盒中做测试 - 印象笔记开发者
                https://dev.yinxiang.com/doc/articles/testing.php

                API 调用频率限制 - 印象笔记开发者
                https://dev.yinxiang.com/doc/articles/rate_limits.php

                文档 - 印象笔记开发者
                https://dev.yinxiang.com/doc/#reference

                印象笔记云 API — Python 快速入门指南 - 印象笔记开发者
                https://dev.yinxiang.com/doc/start/python.php

                创建笔记 - 印象笔记开发者
                https://dev.yinxiang.com/doc/articles/creating_notes.php

                资源 - 印象笔记开发者
                https://dev.yinxiang.com/doc/articles/resources.php

                术语表 - 印象笔记开发者
                https://dev.yinxiang.com/support/glossary.php

                开发规范和建议 - 印象笔记开发者
                https://dev.yinxiang.com/trunk/guideline.php#sourceURL

        (3) official github
            evernote:
                evernote/evernote-sdk-python: Evernote SDK for Python
                https://github.com/evernote/evernote-sdk-python

                evernote/evernote-sdk-python3: Testing the Evernote Cloud API for Python 3
                https://github.com/evernote/evernote-sdk-python3
            
            yinxiang:
                yinxiang-dev/evernote-sdk-python: Evernote SDK for Python
                https://github.com/yinxiang-dev/evernote-sdk-python

                yinxiang-dev/evernote-sdk-python3: Testing the Evernote Cloud API for Python 3
                https://github.com/yinxiang-dev/evernote-sdk-python3
    """

    XmlHeader = """<?xml version="1.0" encoding="UTF-8"?>"""
    DoctypeEnNote = """<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">"""

    ################################################################################
    # Class Method
    ################################################################################

    def __init__(self, authToken, isSandbox=False, isChina=True):
        self.searchPageSize = 5000

        self.authToken = authToken
        self.isSandbox = isSandbox
        self.isChina = isChina
        # logging.debug("self.isSandbox=%s, self.isChina=%s", self.isSandbox, self.isChina)
        self.host = crifanEvernote.getHost(self.isSandbox, self.isChina)

        self.client = self.initClient()
        logging.info("self.client=%s", self.client)

        self.userStore = self.client.get_user_store()
        logging.info("self.userStore=%s", self.userStore)

        self.isSdkLatest = self.userStore.checkVersion(
            "Evernote EDAMTest (Python)",
            EDAM_VERSION_MAJOR, # UserStoreConstants.EDAM_VERSION_MAJOR,
            EDAM_VERSION_MINOR, # UserStoreConstants.EDAM_VERSION_MINOR
        )
        if self.isSdkLatest:
            logging.info("Evernote API version is latest")
        else:
            logging.warning("Evernote API version is NOT latest -> need update")

        try:
            self.noteStore = self.client.get_note_store()
            logging.info("self.noteStore=%s", self.noteStore)
        except BaseException as curException:
            logging.error("init noteStore exception: %s -> possible reason is token expired -> need refresh Evernote token", curException)

    def initClient(self):
        client = EvernoteClient(
            token=self.authToken,
            # sandbox=self.isSandbox,
            # china=self.isChina,
            service_host=self.host
        )
        return client

    def listNotebooks(self):
        """Get all notebook
        
        Args:
        Returns:
        Raises:
        """
        notebookList = self.noteStore.listNotebooks()
        return notebookList

    def findNotes(self, notebookId):
        """Fina all notes of a notebook

        Args:
            notebookId (str): notebook id
                eg： '9bf6cecf-d91e-4391-a034-199c744424db'
        Returns:
            Note list
        Raises:
        """
        logging.debug("notebookId=%s", notebookId)
        # find all notes in notebook
        searchOffset = 0
        # searchPageSize = 1000
        # searchPageSize = 5000
        searchPageSize = self.searchPageSize
        searchFilter = NoteStore.NoteFilter()
        searchFilter.order = NoteSortOrder.UPDATED
        searchFilter.ascending = False
        searchFilter.notebookGuid = notebookId
        logging.debug("searchFilter=%s", searchFilter)
        resultSpec = NotesMetadataResultSpec()
        resultSpec.includeTitle = True
        resultSpec.includeContentLength = True
        resultSpec.includeCreated = True
        resultSpec.includeUpdated = True
        resultSpec.includeDeleted = True
        resultSpec.includeNotebookGuid = True
        resultSpec.includeTagGuids = True
        resultSpec.includeAttributes = True
        resultSpec.includeLargestResourceMime = True
        resultSpec.includeLargestResourceSize = True
        logging.debug("resultSpec=%s", resultSpec)

        # foundNoteResult = self.noteStore.findNotesMetadata(
        #     authenticationToken=self.authToken,
        #     filter=searchFilter,
        #     offset=searchOffset,
        #     maxNotes=pageSize,
        #     resultSpec=resultSpec
        # )
        foundNoteResult = self.noteStore.findNotesMetadata(
            self.authToken, searchFilter, searchOffset, searchPageSize, resultSpec
        )
        logging.debug("foundNoteResult=%s", foundNoteResult)
        totalNotes = foundNoteResult.totalNotes
        logging.info("Total %d notes for notebook of guid=%s", totalNotes, notebookId)
        foundNoteList = foundNoteResult.notes
        return foundNoteList
    
    def createNote(self, noteTitle, noteBody="", notebookId=None):
        """get note detail

        Args:
            noteTitle (str): note title
            noteContent (str): note content
            notebookId (str): parent notebook id, detault: None
        Returns:
            note
        Raises:
        Examples:
        """
        createdNote = None

        noteContent = "%s%s<en-note>%s</en-note>" % (crifanEvernote.XmlHeader, crifanEvernote.DoctypeEnNote, noteBody)
        # '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd"><en-note></en-note>'
        newNote = Types.Note()
        newNote.title = noteTitle
        newNote.content = noteContent
        if notebookId:
            newNote.notebookGuid = notebookId

        try:
            createdNote = self.noteStore.createNote(self.authToken, newNote)
        except EDAMUserException as userErr:
            logging.error("Fail to create new note for user error %s", userErr)
        except  EDAMNotFoundException as notFoundErr:
            logging.error("Fail to create new note for not found error %s", notFoundErr)

        return createdNote

    def getNoteDetail(self, noteId):
        """Get note detail

        Args:
            noteId (str): Evernote note id
        Returns:
            Note with detail
        Raises:
        Examples:
            '9bf6cecf-d91e-4391-a034-199c744424db'
        """
        # noteDetail = self.noteStore.getNote(self.authToken, noteId, True, True, True, True)
        # noteDetail = self.noteStore.getNote(
        #     authenticationToken=self.authToken,
        #     guid=noteId,
        #     withContent=True,
        #     withResourcesData=True,
        #     # withResourcesRecognition=True,
        #     withResourcesRecognition=False,
        #     # withResourcesAlternateData=True,
        #     withResourcesAlternateData=False,
        # )
        noteDetail = self.noteStore.getNote(self.authToken, noteId, True, True, False, False)
        return noteDetail

    def syncNote(self,
            noteGuid,
            noteTitle,
            notebookGuid=None,
            newContent=None,
            newResList=None,
            newAttributes=None,
            newTagGuidList=None,
        ):
        """Update note with new content and/or new resource list

        Args:
            noteGuid (str): Note guid
            noteTitle (str): Note title
            notebookGuid (str): notebook guid
            newContent (str): new Note content
            newResList (list): new Note resource list
            newAttributes (list): new attribute list
            newTagGuidList (list): new tag list
        Returns:
            synchronized note
        Raises:
        """
        newNote = Types.Note()
        newNote.guid = noteGuid
        newNote.title = noteTitle

        # sync following
        if newContent:
            newContent = crifanEvernote.convertToClosedEnMediaTag(newContent)
            logging.debug("newContent=%s", newContent)
            newNote.content = newContent

        if notebookGuid:
            newNote.notebookGuid = notebookGuid

        if newResList:
            newNote.resources = newResList

        if newAttributes:
            newNote.attributes = newAttributes

        if newTagGuidList:
            newNote.tagGuids = newTagGuidList

        # updatedNote = self.noteStore.syncNote(newNote)
        updatedNote = self.noteStore.updateNote(newNote)
        return updatedNote

    def moveToNoteBook(self, curNote, newNotebookGuid):
        """Move Note to new notebook

        Args:
            curNote (Note): Evernote Note
            newNotebookGuid (str): new Notebook guid
        Returns:
            moved ok (bool)
        Raises:
        """
        isMoveOk = False

        curNotebookGuid = curNote.notebookGuid
        if curNotebookGuid == newNotebookGuid:
            isMoveOk = True
            logging.info("Already in notebook %s for note %s", curNotebookGuid, curNote.title)
            return isMoveOk

        # Sync to Evernote
        syncParamDict = {
            # mandatory
            "noteGuid": curNote.guid,
            "noteTitle": curNote.title,
            # optional
            "notebookGuid": newNotebookGuid,
        }

        respNote = self.syncNote(**syncParamDict)
        logging.debug("respNote=%s", respNote)
        isMoveOk = True
        return isMoveOk

    def getTagNameList(self, curNote):
        """get note tag name list

            TODO: can change/update to getNoteTagNames ?
                https://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_getNoteTagNames

        Args:
            curNote (Note): Evernote Note
        Returns:
            tag name list(list)
        Raises:
        """
        curTagList = []
        tagGuidList = curNote.tagGuids
        logging.debug("tagGuidList=%s", tagGuidList)
        
        if tagGuidList:
            # tagGuidList=['1dda873b-310e-46be-b59e-02a1f8c95720', '6ff65876-aab4-406b-b52b-4c1105638450', '38f11450-1a7a-4f54-ba17-b78889c1567a', '46258420-3d2e-443c-b63d-c5431e061aab', '52b7babc-d6ea-4390-b405-79c21da5188e']
            for eachTagGuid in tagGuidList:
                tagInfo = self.noteStore.getTag(eachTagGuid)
                logging.debug("tagInfo=%s", tagInfo)
                curTagStr = tagInfo.name
                curTagList.append(curTagStr)
        else:
            logging.debug("No tags for note %s", curNote.title)

        logging.debug("curTagList=%s", curTagList)
        # curTagList=['Mac', '切换', 'GPU', 'pmset', '显卡模式']
        return curTagList

    def listTags(self):
        """Get all tags
        
        Args:
        Returns:
        Raises:
        """
        tagList = self.noteStore.listTags()
        return tagList

    def findTag(self, tagName):
        """Find existed tag from tag name

        Args:
            tagName (str): tag name
        Returns:
            Tag or None
        Raises:
        Examples:
            '微信' -> Tag(guid='fdb373fa-8382-48da-96d4-6d8111ec32f5', name='微信', parentGuid=None, updateSequenceNum=218537)
        """
        existedTag = None
        tagNameLowecase = tagName.lower() # '夜神'
        allTagList = self.listTags()
        for eachTag in allTagList:
            eachTagName = eachTag.name
            eachTagNameLower = eachTagName.lower()
            if tagNameLowecase == eachTagNameLower:
                existedTag = eachTag
                break
        return existedTag

    def createTag(self, tagName):
        """Create new tag from tag name

        Args:
            tagName (str): tag name
        Returns:
            Tag
        Raises:
        Examples:
            '夜神' -> Tag(guid='209e70eb-34a7-44c9-9f6d-ddd4da91054b', name='夜神', parentGuid=None, updateSequenceNum=5781064)
        """
        existedTag = self.findTag(tagName)
        if existedTag:
            return existedTag

        newTag = Types.Tag()
        newTag.name = tagName
        createdTag = self.noteStore.createTag(newTag)
        return createdTag

    def updateTags(self, curNote, tagNameList):
        """Update Note tags from tag name list

        Args:
            curNote (Note): Evernote Note
            tagNameList (list): tag name list
        Returns:
            updated Note
        Raises:
        """
        tagGuidList = []
        for eachTagName in tagNameList:
            createdTag = self.createTag(eachTagName)
            createdTagGuid = createdTag.guid
            tagGuidList.append(createdTagGuid)
        
        logging.info("tagNameList=%s -> tagGuidList=%s", tagNameList, tagGuidList)
        # tagNameList=['夜神', '微信', '模拟器', '安卓'] -> tagGuidList=['209e70eb-34a7-44c9-9f6d-ddd4da91054b', 'fdb373fa-8382-48da-96d4-6d8111ec32f5', 'abf548e2-c110-4b92-b1fb-84d5c2052aa3', 'f9ea2006-dba8-41de-8f57-0f0f0fac6a32']

        # Sync to Evernote
        syncParamDict = {
            # mandatory
            "noteGuid": curNote.guid,
            "noteTitle": curNote.title,
            # optional
            "newTagGuidList": tagGuidList,
        }

        respNote = self.syncNote(**syncParamDict)
        logging.debug("respNote=%s", respNote)

        return respNote

    ################################################################################
    # Static Method
    ################################################################################

    @staticmethod
    def getHost(isSandbox=False, isChina=True):
        # logging.debug("isSandbox=%s, isChina=%s", isSandbox, isChina)
        evernoteHost = ""
        if isChina:
            if isSandbox:
                evernoteHost = "sandbox.yinxiang.com"
            else:
                evernoteHost = "app.yinxiang.com"
        else:
            if isSandbox:
                evernoteHost = "sandbox.evernote.com"
            else:
                evernoteHost = "app.evernote.com"

        return evernoteHost

    @staticmethod
    def genResourceInfoStr(curResource):
        """Generate resource info str, use for debug print

        Args:
            curResource (Resource): Evernote Resouce
        Returns:
            resource info(str)
        Raises:
        Examples:
            output: 'Resource(name=1E4CC2E2-581D-4B18-B0EB-E016B2245A1C.png,mime=image/jpeg,guid=27e8b7d0-3fc5-4b05-8b1a-ab8c09423a96)'
        """
        resInfoStr = "Resource(name=%s,mime=%s,guid=%s)" % (curResource.attributes.fileName, curResource.mime, curResource.guid)
        return resInfoStr

    @staticmethod
    def isImageResource(curResource):
        """check is image media or not

        Args:
            curMedia (Resource): Evernote Resouce instance
        Returns:
            bool
        Raises:
        """
        isImage = False
        curResMime = curResource.mime # 'image/png' 'image/jpeg'
        # libs/evernote-sdk-python3/lib/evernote/edam/limits/constants.py
        matchImage = re.match("^image/", curResMime)
        logging.debug("matchImage=%s", matchImage)
        if matchImage:
            """
                image/gif
                image/jpeg
                image/png
            """
            isImage = True
        logging.debug("curResMime=%s -> isImage=%s", curResMime, isImage)
        return isImage

    @staticmethod
    def resizeNoteImage(noteDetail):
        """Resize note each media image and update note content

        Args:
            noteDetail (Note): evernote note
        Returns:
            new resouce list with resized imgage resource
        Raises:
        """
        newResList = []
        originResList = noteDetail.resources
        if not originResList:
            # is None
            return newResList

        originResNum = len(originResList)
        for curResIdx, eachResource in enumerate(originResList):
            curResNum = curResIdx + 1
            if crifanEvernote.isImageResource(eachResource):
                imgFilename = eachResource.attributes.fileName
                logging.info("[%d/%d] imgFilename=%s", curResNum, originResNum, imgFilename)

                resBytes = eachResource.data.body
                resizedImgBytes, imgFormat, newSize = utils.resizeSingleImage(resBytes)

                resizedImgLen = len(resizedImgBytes) # 38578
                resizedImgLenStr = utils.formatSize(resizedImgLen) # '37.7KB'
                logging.info("resized to fmt=%s, len=%s, size=%sx%s", imgFormat, resizedImgLenStr, newSize[0], newSize[1])

                resizedImgMd5Bytes = utils.calcMd5(resizedImgBytes, isRespBytes=True) # '3110e1e7994dc119ff92439c5758e465'
                newMime = utils.ImageFormatToMime[imgFormat] # 'image/jpeg'

                newData = Types.Data()
                # newData = ttypes.Data()
                newData.size = resizedImgLen
                newData.bodyHash = resizedImgMd5Bytes
                newData.body = resizedImgBytes

                newRes = Types.Resource()
                # newRes = ttypes.Resource()
                newRes.mime = newMime
                newRes.data = newData
                newRes.attributes = eachResource.attributes

                newResList.append(newRes)
            else:
                """
                    audio/wav
                    audio/mpeg
                    audio/amr
                    application/pdf
                    ...
                """
                newResList.append(eachResource)

        return newResList

    @staticmethod
    def resizeAndUpdateNoteImage(noteDetail):
        """Resize evernote note image media, then update note content

            Args:
                noteDetail (Note): Evernote note with details
            Returns:
                updated note detail
            Raises:
        """
        newResList = crifanEvernote.resizeNoteImage(noteDetail)
        if newResList:
            noteDetail = crifanEvernote.updateNoteResouces(noteDetail, newResList)
        return noteDetail

    @staticmethod
    def findResourceSoup(curResource, soup=None, curNoteDetail=None):
        """Find related <en-media> BeautifulSoup soup from Evernote Resource

        Args:
            curResource (Resource): Evernote Resource
            soup (Soup): BeautifulSoup soup of note content
            curNoteDetail (Note): Evernote note, with detail content
        Returns:
            soup node
        Raises:
        """
        if not soup:
            soup = crifanEvernote.noteContentToSoup(curNoteDetail)

        curMime = curResource.mime # 'image/png'
        logging.debug("curMime=%s", curMime)
        # # method 1: calc again
        # curResBytes = curResource.data.body
        # curHashStr1 = utils.calcMd5(curResBytes) # 'dc355da030cafe976d816e99a32b6f51'

        # method 2: convert from body hash bytes
        curHashStr = utils.bytesToStr(curResource.data.bodyHash)
        logging.debug("curHashStr=%s", curHashStr)
        # b'\xae\xe1G\xdb\xcdh\x16\xca+@IF"\xff\xfa\xa3' -> 'aee147dbcd6816ca2b40494622fffaa3'

        # imgeTypeP = re.compile("image/\w+")
        curResSoup = soup.find("en-media", attrs={"type": curMime, "hash": curHashStr})
        logging.debug("curResSoup=%s", curResSoup)
        # <en-media hash="aee147dbcd6816ca2b40494622fffaa3" type="image/png" width="370"></en-media>
        return curResSoup

    @staticmethod
    def updateNoteResouces(noteDetail, newResList):
        """Update note resources with new resource

        Args:
            noteDetail (Note): Evernote note with details
        Returns:
            updated note detail
        Raises:
        """
        validNewResList = []
        originResList = noteDetail.resources

        # originContent = noteDetail.content
        # soup = BeautifulSoup(originContent, 'html.parser')
        soup = crifanEvernote.noteContentToSoup(noteDetail)

        for curIdx, curRes in enumerate(originResList):
            foundMediaNode = crifanEvernote.findResourceSoup(curRes, soup=soup)
            if foundMediaNode:
                newRes = newResList[curIdx] # 'image/jpeg'
                validNewResList.append(newRes)
                newMime = newRes.mime
                # newHashBytes = newRes.data.bodyHash # b'\xb8\xe8\xbb\xcc\xca\xc1\xdf&J\xbeV\xe2`\xa6K\xb7'
                newResBytes = newRes.data.body
                newHashStr = utils.calcMd5(newResBytes) # '3da990710b87fcd56a84d644202b12c2'
                foundMediaNode["type"] = newMime
                foundMediaNode["hash"] = newHashStr

                noteAttrs = foundMediaNode.attrs
                # {'hash': '3da990710b87fcd56a84...44202b12c2', 'type': 'image/jpeg'}
                # {'hash': 'f9fc018211046ccc0eb6...5f67d0c8d6', 'type': 'image/jpeg', 'width': '385'}
                # special: 
                #   <en-media hash="0bbf1712d4e9afe725dd51e701c7fae6" style="width: 788px; height: auto;" type="image/jpeg"></en-media>
                #   ->
                #   {'hash': '0bbf1712d4e9afe725dd51e701c7fae6', 'type': 'image/jpeg', 'width': '788', 'height': 'auto'} ?
                hasWidthAttr = "width" in noteAttrs
                hasHeightAttr = "height" in noteAttrs
                if hasWidthAttr or hasHeightAttr:
                    newImg = utils.bytesToImage(newResBytes)
                    # newImgWidth = newImg.width
                    # newImgHeight = newImg.height
                    newImgWidth, newImgHeight = newImg.size
                    if hasWidthAttr:
                        attrWidthStr = noteAttrs["width"]
                        if attrWidthStr.isdigit():
                            curWidth = int(attrWidthStr)
                            if curWidth >= newImgWidth:
                                # old size is bigger than resized image size, so need remove old size
                                del foundMediaNode["width"]
                        else:
                            # is 'auto' ? -> keep not changed ?
                            logging.warning("not support ? img width value: %s", attrWidthStr)

                    if hasHeightAttr:
                        attrHeightStr = noteAttrs["height"]
                        if attrHeightStr.isdigit():
                            curHeight = int(attrHeightStr)
                            if curHeight >= newImgHeight:
                                # old size is bigger than resized image size, so need remove old size
                                del foundMediaNode["height"]
                        else:
                            # is 'auto' ? -> keep not changed ?
                            logging.warning("not support ? img height value: %s", attrHeightStr)
            else:
                # logging.warning("Not found resource: type=%s, hash=%s", curMime, curHashStr)
                logging.warning("Not found resource: guid=%s, mime=%s", curRes.guid, curRes.mime)
                # not add to validNewResList

        # newContent = soup.prettify()
        # newContent = str(soup)
        newContent = crifanEvernote.soupToNoteContent(soup)
        noteDetail.content = newContent

        # noteDetail.resources = newResList
        noteDetail.resources = validNewResList

        return noteDetail
    
    @staticmethod
    def noteContentToHtml(noteContent, isKeepTopHtml=True):
        """convert Evernote Note content to pure html

        Args:
            isKeepTopHtml (bookl): whether keep top html. Ture to <html>xxx<html>, False to xxx
        Returns:
            html (str)
        Raises:
        """
        # Special:
        # '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">\n<en-note>
        # -> remove: <?xml version="1.0" encoding="UTF-8" standalone="no"?>
        # noteHtml = re.sub('<\?xml version="1.0" encoding="UTF-8" standalone="no"\?>\s*', "", noteContent)
        noteHtml = re.sub('<\?xml version="1.0" encoding="UTF-8"(\s+standalone="no")?\?>\s*', "", noteContent)

        # remove fisrt line
        # <!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
        # '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">\n
        # <!DOCTYPE en-note SYSTEM 'http://xml.evernote.com/pub/enml2.dtd'>
        noteHtml = re.sub("""<!DOCTYPE en-note SYSTEM ((")|('))http://xml\.evernote\.com/pub/enml2\.dtd((")|('))>\s*""", "", noteHtml)

        if isKeepTopHtml:
            # convert <en-note>...</en-note> to <html>...</html>
            replacedP = "<html>\g<contentBody></html>"
        else:
            # convert <en-note>...</en-note> to ...
            replacedP = "\g<contentBody>"
        # noteHtml = re.sub('<en-note>(?P<contentBody>.+)</en-note>', replacedP, noteHtml, flags=re.S)
        withEnNoteHtml = noteHtml
        withoutEnNoteHtml = re.sub('<en-note>(?P<contentBody>.*)</en-note>', replacedP, withEnNoteHtml, flags=re.S)
        if withoutEnNoteHtml == withEnNoteHtml:
            logging.warning("Maybe en-note remove not work for %s", withEnNoteHtml)
        noteHtml = withoutEnNoteHtml

        noteHtml = noteHtml.strip()
        return noteHtml

    @staticmethod
    def getNoteContentHtml(curNote, isKeepTopHtml=True):
        """Get evernote Note content html

        Args:
            curNote (Note): evernote Note
            isKeepTopHtml (bookl): whether keep top html. Ture to <html>xxx<html>, False to xxx
        Returns:
            html (str)
        Raises:
        """
        noteHtml = crifanEvernote.noteContentToHtml(curNote.content, isKeepTopHtml)
        return noteHtml

    @staticmethod
    def noteContentToSoup(curNote, isKeepTopHtml=True):
        """Convert Evernote Note content to BeautifulSoup Soup

        Args:
            curNote (Note): Evernote Note
            isKeepTopHtml (bookl): whether keep top html. Ture to <html>xxx<html>, False to xxx
        Returns:
            Soup
        Raises:
        """
        noteHtml = crifanEvernote.getNoteContentHtml(curNote, isKeepTopHtml)

        soup = utils.htmlToSoup(noteHtml)
        # Note: now top node is <html>, not <en-note>
        #       but top node name is '[document]' not 'html'

        # for debug
        # if soup.name != "html":
        if soup.name != "[document]":
            logging.info("soup.name=%s", soup.name)

        return soup

    @staticmethod
    def htmlToNoteContent(noteHtml):
        """Convert html (with or without <html>) to Evernote Note content

        Args:
            html (str): current html
        Returns:
            Evernote Note content html(str)
        Raises:
        """
        # convert <html>...</html> back to <en-note>...</en-note>
        # noteContent = re.sub('<html>(?P<contentBody>.+)</html>', "<en-note>\g<contentBody></en-note>", noteHtml, flags=re.S)
        # Special: some time, here is removed top html -> so need add top <html>...</html> back
        # noteContent = re.sub('(<html>)?(?P<contentBody>.+)(</html>)?', "<en-note>\g<contentBody></en-note>", noteHtml, flags=re.S)
        # support both xxx and <html>xxx</html>
        pureHtmlBody = re.sub('<html>(?P<contentBody>.+)</html>', "\g<contentBody>", noteHtml, flags=re.S)
        noteContent = "<en-note>%s</en-note>" % pureHtmlBody

        noteContent = crifanEvernote.convertToClosedEnMediaTag(noteContent)

        # add first line
        # <!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
        # noteContent = '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">\n' + noteContent
        noteContent = "%s\n%s" % (crifanEvernote.DoctypeEnNote, noteContent)

        return noteContent

    @staticmethod
    def soupToNoteContent(soup):
        """Convert BeautifulSoup Soup to Evernote Note content

        Args:
            soup (Soup): BeautifulSoup Soup
        Returns:
            Evernote Note content html(str)
        Raises:
        """

        # for debug
        # if soup.name != "html":
        if soup.name != "[document]":
            logging.info("soup.name=%s", soup.name)

        # soup.name = "en-note" # not work
        noteContent = utils.soupToHtml(soup, isFormat=False)
        # Note: here not use formated html, to avoid
        # speical case:
        # some special part title is url, then format will split part url and title
        # so here not use format

        noteHtml = crifanEvernote.htmlToNoteContent(noteContent)
        return noteHtml

    @staticmethod
    def convertToClosedEnMediaTag(noteHtml):
        """Process note content html, for special </en-media> will cause error, so need convert:
                <en-media hash="7c54d8d29cccfcfe2b48dd9f952b715b" type="image/png"></en-media>
            to closed en-media tag:
                <en-media hash="7c54d8d29cccfcfe2b48dd9f952b715b" type="image/png" />
        Args:
            noteHtml (str): Note content html
        Returns:
            note content html with closed en-media tag (str)
        Raises:
        """
        noteHtml = re.sub("(?P<enMedia><en-media\s+[^<>]+)>\s*</en-media>", "\g<enMedia> />", noteHtml, flags=re.S)
        return noteHtml

    @staticmethod
    def generateTags(curNote, maxTagNum=6):
        """Generate tags from note (title and content)

        Args:
            curNote (Note): evernote Note
            maxTagNum (int): max number of tags
        Returns:
            tag list(list)
        Raises:
        Examples:
            ['模拟器', 'Charles', '安卓']
            ['MuMu', '安卓', '网易', '安装', 'JustTrustMe', 'Mac']
        """
        # generate tags from content if no tags
        curNoteTitle = curNote.title
        logging.debug("curNoteTitle=%s", curNoteTitle)
        # remove 【未解决】 【已解决】 【记录】 【无需解决】
        titleStr = re.sub("^【\S{2,5}】(?P<titleStr>.+)", "\g<titleStr>", curNoteTitle)
        # '【未解决】夜神安卓模拟器安装新版微信并正常打开和使用微信' -> '夜神安卓模拟器安装新版微信并正常打开和使用微信'
        logging.debug("titleStr=%s", titleStr)
        # titleTagList = utils.extractTags(titleStr, withWeight=True)
        titleTagList = utils.extractTags(titleStr)
        logging.debug("titleTagList=%s", titleTagList)

        noteSoup = crifanEvernote.noteContentToSoup(curNote)
        noteContentStr = utils.getAllContents(noteSoup, isStripped=True)
        # contentTagList = utils.extractTags(noteContentStr, withWeight=True)
        contentTagList = utils.extractTags(noteContentStr)
        logging.debug("contentTagList=%s", contentTagList)

        # merge title and content tags for same one
        mergedTagList = []
        for eachContentTag in contentTagList:
            for eachTitleTag in titleTagList:
                if eachContentTag in eachTitleTag:
                    if eachContentTag not in mergedTagList:
                        mergedTagList.append(eachContentTag)
                    break
        logging.debug("mergedTagList=%s", mergedTagList)

        # after merge, if too little tags, then add some from content tags
        MinSameTagNum = 3
        mergedTagNum = len(mergedTagList)
        # if mergedTagNum <= MinSameTagNum:
        if mergedTagNum < MinSameTagNum:
            for eachContentTag in contentTagList:
                if eachContentTag not in mergedTagList:
                    mergedTagList.append(eachContentTag)
                    # if len(mergedTagList) >= maxTagNum:
                    #     break

            for eachTitleTag in titleTagList:
                if eachTitleTag not in mergedTagList:
                    mergedTagList.append(eachTitleTag)

        # filter out invalid tags
        validTagList = []
        InvalidTagRuleList = [
            "^\d+([\d\.]+)?$",
            "^解决$",
            "^com$",
            "^crifan$",
            "^drwx$",
            "^drwxr$",
            "^mnt$",
            "^Users?$",
            "^share$",
            "^shared$",
            "^staff$",
            "^xr$",
        ]
        for eachTag in mergedTagList:
            isTagValid = True
            for eachInvalidRule in InvalidTagRuleList:
                isInvalid = re.search(eachInvalidRule, eachTag, re.I)
                if isInvalid:
                    logging.warning("Omit invalid tag %s for rule %s", eachTag, eachInvalidRule)

                    isTagValid = False
                    break

            if isTagValid:
                if eachTag not in validTagList:
                    validTagList.append(eachTag)

        logging.debug("validTagList=%s", validTagList)

        validTagNum = len(validTagList)
        if validTagNum > maxTagNum:
            validTagList = validTagList[0:maxTagNum]
        logging.debug("validTagList=%s", validTagList)

        return validTagList
