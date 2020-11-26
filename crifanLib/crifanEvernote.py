# Function: Evernote related functions
# Author: Crifan Li
# Update: 20201126
# Online: https://github.com/crifan/crifanLibPython/blob/master/crifanLib/crifanEvernote.py

import sys
import re
import logging
from bs4 import BeautifulSoup

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
    """

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

        self.noteStore = self.client.get_note_store()
        logging.info("self.noteStore=%s", self.noteStore)

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
        logging.info("curResMime=%s -> isImage=%s", curResMime, isImage)
        return isImage

    def initClient(self):
        client = EvernoteClient(
            token=self.authToken,
            # sandbox=self.isSandbox,
            # china=self.isChina,
            service_host=self.host
        )
        return client

    def listNotebooks(self):
        """List notebook list"""
        notebookList = self.noteStore.listNotebooks()
        return notebookList

    def findNotes(self, notebookId):
        """Fina all note of notebook

        Args:
            notebookId (str): notebook id
                eg： '9bf6cecf-d91e-4391-a034-199c744424db'
        Returns:
            Note list
        Raises:
        """
        logging.info("notebookId=%s", notebookId)
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
        logging.info("totalNotes=%s", totalNotes)
        foundNoteList = foundNoteResult.notes
        return foundNoteList

    def getNoteDetail(self, noteId):
        """get note detail

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
        ):
        """Update note with new content and/or new resource list

        Args:
            noteGuid (str): Note guid
            noteTitle (str): Note title
            notebookGuid (str): notebook guid
            newContent (str): new Note content
            newResList (list): new Note resource list
            newAttributes (list): new attribute list
        Returns:
            synchronized note
        Raises:
        """
        newNote = Types.Note()
        newNote.guid = noteGuid
        newNote.title = noteTitle

        # sync following
        if newContent:
            # special:
            # (1) </en-media> will cause error, so need process:
            #   <en-media hash="7c54d8d29cccfcfe2b48dd9f952b715b" type="image/png"></en-media>
            #   ->
            #   <en-media hash="7c54d8d29cccfcfe2b48dd9f952b715b" type="image/png" />
            newContent = re.sub("(?P<enMedia><en-media\s+[^<>]+)>\s*</en-media>", "\g<enMedia> />", newContent, flags=re.S)
            logging.debug("newContent=%s", newContent)
            newNote.content = newContent

        if notebookGuid:
            newNote.notebookGuid = notebookGuid

        if newResList:
            newNote.resources = newResList

        if newAttributes:
            newNote.attributes = newAttributes

        # updatedNote = self.noteStore.syncNote(newNote)
        updatedNote = self.noteStore.updateNote(newNote)
        return updatedNote

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
        for curIdx, eachResource in enumerate(originResList):
            if crifanEvernote.isImageResource(eachResource):
                imgFilename = eachResource.attributes.fileName
                logging.info("[%d] imgFilename=%s", curIdx, imgFilename)

                resBytes = eachResource.data.body
                resizedImgBytes, imgFormat = utils.resizeSingleImage(resBytes)

                resizedImgLen = len(resizedImgBytes) # 38578
                resizedImgLenStr = utils.formatSize(resizedImgLen) # '37.7KB'
                logging.info("resized to fmt=%s, len=%s", imgFormat, resizedImgLenStr)

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
        noteDetail = crifanEvernote.updateNoteResouces(noteDetail, newResList)
        return noteDetail

    @staticmethod
    def findResourceSoup(soup, curResource):
        """find related BeautifulSoup soup from Evernote Resource

        Args:
            soup (Soup): BeautifulSoup soup
            curResource (Resource): Evernote Resource
        Returns:
            soup node
        Raises:
        """
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
        originResList = noteDetail.resources
        originContent = noteDetail.content
        soup = BeautifulSoup(originContent, 'html.parser')
        for curIdx, curRes in enumerate(originResList):
            foundMediaNode = crifanEvernote.findResourceSoup(soup, curRes)
            if foundMediaNode:
                newRes = newResList[curIdx] # 'image/jpeg'
                newMime = newRes.mime
                # newHashBytes = newRes.data.bodyHash # b'\xb8\xe8\xbb\xcc\xca\xc1\xdf&J\xbeV\xe2`\xa6K\xb7'
                newResBytes = newRes.data.body
                newHashStr = utils.calcMd5(newResBytes) # '3da990710b87fcd56a84d644202b12c2'
                foundMediaNode["type"] = newMime
                foundMediaNode["hash"] = newHashStr

                noteAttrs = foundMediaNode.attrs
                # {'hash': '3da990710b87fcd56a84...44202b12c2', 'type': 'image/jpeg'}
                # {'hash': 'f9fc018211046ccc0eb6...5f67d0c8d6', 'type': 'image/jpeg', 'width': '385'}
                hasWidthAttr = "width" in noteAttrs
                hasHeightAttr = "height" in noteAttrs
                if hasWidthAttr or hasHeightAttr:
                    newImg = utils.bytesToImage(newResBytes)
                    # newImgWidth = newImg.width
                    # newImgHeight = newImg.height
                    newImgWidth, newImgHeight = newImg.size
                    if hasWidthAttr:
                        curWidth = int(noteAttrs["width"])
                        if curWidth >= newImgWidth:
                            # old size is bigger than resized image size, so need remove old size
                            del foundMediaNode["width"]

                    if hasHeightAttr:
                        curHeight = int(noteAttrs["height"])
                        if curHeight >= newImgHeight:
                            # old size is bigger than resized image size, so need remove old size
                            del foundMediaNode["height"]
            else:
                # logging.warning("Not found resource: type=%s, hash=%s", curMime, curHashStr)
                logging.warning("Not found resource %s", curRes)

        # newContent = soup.prettify()
        newContent = str(soup)
        noteDetail.content = newContent

        noteDetail.resources = newResList

        return noteDetail
