# Function: Evernote related functions
# Author: Crifan Li
# Update: 20210103
# Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/thirdParty/crifanEvernote.py

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
import evernote.edam.error.ttypes as EDAMUserException

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
            newContent = crifanEvernote.convertToClosedEnMediaTag(newContent)
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

    def moveToNoteBook(self, curNote, newNotebookGuid):
        """Move Note to new notebook

        Args:
            curNote (Note): Evernote Note
            newNotebookGuid (ste): new Notebook guid
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
            logging.warning("No tags for note %s", curNote.title)

        logging.info("curTagList=%s", curTagList)
        # curTagList=['Mac', '切换', 'GPU', 'pmset', '显卡模式']
        return curTagList

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
        noteHtml = re.sub('<\?xml version="1.0" encoding="UTF-8" standalone="no"\?>\s*', "", noteContent)

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
        noteHtml = re.sub('<en-note>(?P<contentBody>.+)</en-note>', replacedP, noteHtml, flags=re.S)

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
        noteContent = '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">\n' + noteContent

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
