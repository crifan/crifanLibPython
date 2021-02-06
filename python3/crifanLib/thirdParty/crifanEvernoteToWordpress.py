# Function: Evernote to Wordpress related functions
# Author: Crifan Li
# Update: 20210204
# Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/thirdParty/crifanEvernoteToWordpress.py

import sys
import logging
import re

from bs4 import Tag, NavigableString

sys.path.append("lib")
from libs.crifan import utils
from libs.crifan.crifanEvernote import crifanEvernote
from libs.crifan.crifanWordpress import crifanWordpress

class crifanEvernoteToWordpress(object):
    """
        Upload Evernote(Yinxiang) note to WordPress and synchronize back to note via python
    """

    def __init__(self, curEvernote, curWordpress):
        self.evernote = curEvernote
        self.wordpress = curWordpress

    def uploadImageToWordpress(self, imgResource):
        """Upload image resource to wordpress

        Args:
            imgResource (Resouce): evernote image Resouce
        Returns:
            (bool, dict)
        Raises:
        """
        imgData = imgResource.data
        imgBytes = imgData.body
        imgDataSize = imgData.size
        # guid:'f6956c30-ef0b-475f-a2b9-9c2f49622e35'
        imgGuid = imgResource.guid
        logging.debug("imgGuid=%s, imgDataSize=%s", imgGuid, imgDataSize)

        curImg = utils.bytesToImage(imgBytes)
        logging.debug("curImg=%s", curImg)

        # # for debug
        # curImg.show()

        imgFormat = curImg.format # 'PNG'
        imgSuffix = utils.ImageFormatToSuffix[imgFormat] # 'png'
        imgMime = utils.ImageSuffixToMime[imgSuffix] # 'image/png'
        # curDatetimeStr = utils.getCurDatetimeStr() # '20200307_173141'
        processedGuid = imgGuid.replace("-", "") # 'f6956c30ef0b475fa2b99c2f49622e35'
        # imgeFilename = "%s.%s" % (curDatetimeStr, imgSuffix) # '20200307_173141.png'
        imgeFilename = "%s.%s" % (processedGuid, imgSuffix) # 'f6956c30ef0b475fa2b99c2f49622e35.png'

        isUploadImgOk, respInfo = self.wordpress.createMedia(imgMime, imgeFilename, imgBytes)
        logging.debug("%s to upload resource %s to wordpress", isUploadImgOk, imgGuid)
        return isUploadImgOk, respInfo

    def syncNoteImage(self, curNoteDetail, curResource, uploadedImgUrl, curResList=None):
        """Sync uploaded image url into Evernote Note content, replace en-media to img

        Args:
            curNoteDetail (Note): evernote Note
            curResource (Resource): evernote Note Resource
            uploadedImgUrl (str): uploaded imge url, previously is Evernote Resource
            curResList (list): evernote Note Resource list
        Returns:
            updated note detail
        Raises:
        """
        if not curResList:
            curResList = curNoteDetail.resources

        soup = crifanEvernote.noteContentToSoup(curNoteDetail)
        curEnMediaSoup = crifanEvernote.findResourceSoup(curResource, soup=soup)
        logging.debug("curEnMediaSoup=%s", curEnMediaSoup)
        # curEnMediaSoup=<en-media hash="0bbf1712d4e9afe725dd51e701c7fae6" style="width: 788px; height: auto;" type="image/jpeg"></en-media>

        if curEnMediaSoup:
            curImgSoup = curEnMediaSoup
            curImgSoup.name = "img"
            curImgSoup.attrs = {"src": uploadedImgUrl}
            logging.debug("curImgSoup=%s", curImgSoup)
            # curImgSoup=<img src="https://www.crifan.com/files/pic/uploads/2020/11/c8b16cafe6484131943d80267d390485.jpg"></img>
            # new content string
            updatedContent = crifanEvernote.soupToNoteContent(soup)
            logging.debug("updatedContent=%s", updatedContent)
            curNoteDetail.content = updatedContent
        else:
            logging.warning("Not found en-media node for guid=%s, mime=%s, fileName=%s", curResource.guid, curResource.mime, curResource.attributes.fileName)
            # here even not found, still consider as processed, later will remove it

        # remove resource from resource list
        # oldResList = curNoteDetail.resources
        # Note: avoid side-effect: alter pass in curNoteDetail object's resources list
        # which will cause caller curNoteDetail.resources loop terminated earlier than expected !
        # oldResList = copy.deepcopy(curNoteDetail.resources)
        # oldResList.remove(curResource) # workable
        # newResList = oldResList
        # Note 20201206: has update above loop, so should directly update curNoteDetail.resources
        # curNoteDetail.resources.remove(curResource)
        # newResList = curNoteDetail.resources

        curResList.remove(curResource)
        newResList = curResList

        # # for debug
        # if not newResList:
        #     logging.info("empty resources list")

        syncParamDict = {
            # mandatory
            "noteGuid": curNoteDetail.guid,
            "noteTitle": curNoteDetail.title,
            # optional
            "newContent": curNoteDetail.content,
            "newResList": newResList,
        }
        respNote = self.evernote.syncNote(**syncParamDict)
        # logging.info("Completed sync image %s to evernote note %s", uploadedImgUrl, curNoteDetail.title)
        logging.info("Completed sync image %s", uploadedImgUrl)

        return respNote

    def uploadNoteImageToWordpress(self, curNoteDetail, curResource, curResList=None):
        """Upload note single imges to wordpress, and sync to note (replace en-media to img) 

        Args:
            curNote (Note): evernote Note
            curResource (Resource): evernote Note Resource
            curResList (list): evernote Note Resource list
        Returns:
            upload image url(str)
        Raises:
        """
        if not curResList:
            curResList = curNoteDetail.resources

        uploadedImgUrl = ""

        curResInfoStr = crifanEvernote.genResourceInfoStr(curResource)

        isImg = self.evernote.isImageResource(curResource)
        if not isImg:
            logging.warning("Not upload resource for NOT image for %s", curResInfoStr)
            return uploadedImgUrl

        foundResEnMediaSoup = crifanEvernote.findResourceSoup(curResource, curNoteDetail=curNoteDetail)
        if not foundResEnMediaSoup:
            logging.warning("Not need upload for not found related <en-media> node for %s", curResInfoStr)
            return uploadedImgUrl

        isUploadOk, respInfo = self.uploadImageToWordpress(curResource)
        if isUploadOk:
            # {'id': 70491, 'url': 'https://www.crifan.com/files/pic/uploads/2020/11/c8b16cafe6484131943d80267d390485.jpg', 'slug': 'c8b16cafe6484131943d80267d390485', 'link': 'https://www.crifan.com/c8b16cafe6484131943d80267d390485/', 'title': 'c8b16cafe6484131943d80267d390485'}
            uploadedImgUrl = respInfo["url"]
            logging.info("Uploaded url %s", uploadedImgUrl)
            # "https://www.crifan.com/files/pic/uploads/2020/03/f6956c30ef0b475fa2b99c2f49622e35.png"
            # relace en-media to img
            respNote = self.syncNoteImage(curNoteDetail, curResource, uploadedImgUrl, curResList)
            # logging.info("Complete sync image %s to note %s", uploadedImgUrl, respNote.title)
        else:
            logging.warning("Failed to upload image resource %s to wordpress, respInfo=%s", curResInfoStr, respInfo)

        return uploadedImgUrl

    def generateCategoryList(self, tagNameList):
        """Generate category list from tag name list

        Args:
            tagNameList (list): tag name list
        Returns:
            category name list(list)
        Raises:
        """
        categoryNameList = []
        # if tagNameList:
        #     firstTag = tagNameList.pop(0) # 'Mac'
        #     categoryNameList.append(firstTag)
        firstExistedCategory = None
        for eachTagName in tagNameList:
            isSearhOk, existedCategory = self.wordpress.searchTaxonomy(eachTagName, "category")
            # True, {'_links': {'about': [...], 'collection': [...], 'curies': [...], 'self': [...], 'up': [...], 'wp:post_type': [...]}, 'count': 35, 'description': '', 'id': 3178, 'link': 'https://www.crifan.c...s_windows/', 'meta': [], 'name': 'Windows', 'parent': 4624, 'slug': 'os_windows', 'taxonomy': 'category'}
            if isSearhOk and existedCategory:
                firstExistedCategory = eachTagName
                break
    
        if not firstExistedCategory:
            firstExistedCategory = tagNameList[0]

        categoryNameList.append(firstExistedCategory)
        return categoryNameList

    def uploadNoteToWordpress(self, curNote, isNeedGetLatestDetail=True):
        """Upload note content new html to wordpress

        Args:
            curNote (Note): evernote Note
            isNeedGetLatestDetail (bool): need or not to get latest detailed note content
        Returns:
            (bool, dict)
        Raises:
        """
        if isNeedGetLatestDetail:
            logging.info("Starting get note detail for %s", curNote.title)
            curNote = self.evernote.getNoteDetail(curNote.guid)

        # # for debug
        # utils.dbgSaveContentToHtml(curNote)

        postTitle = curNote.title
        logging.debug("postTitle=%s", postTitle)
        # '【记录】Mac中用pmset设置GPU显卡切换模式'
        postSlug = curNote.attributes.sourceURL
        logging.debug("postSlug=%s", postSlug)
        # 'on_mac_pmset_is_used_set_gpu_graphics_card_switching_mode'

        # content html
        # contentHtml = curNote.content
        # '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">\n<en-note>\n <div>\n  折腾：\n </div>\n <div>\n  【已解决】Mac Pro 2018款发热量大很烫非常烫\n </div>。。。。。。high performance graphic cards\n    </li>\n   </ul>\n  </ul>\n </ul>\n <div>\n  <br/>\n </div>\n</en-note>'
        # contentHtml = crifanEvernote.getNoteContentHtml(curNote)
        # '<html>\n <div>\n  折腾：\n </div>\n <div>\n  【已解决】Mac Pro 2018款发热量大很烫非常烫\n </div>\n <div>\n  期间， ... graphic cards\n    </li>\n   </ul>\n  </ul>\n </ul>\n <div>\n  <br/>\n </div>\n</html>'
        contentHtml = crifanEvernote.getNoteContentHtml(curNote, isKeepTopHtml=False)
        logging.debug("contentHtml=%s", contentHtml)
        # '<div>\n  折腾：\n </div>\n <div>\n  【已解决】Mac Pro 2018款发热量大很烫非常烫\n </div>\n <div>\n  期间， ... graphic cards\n    </li>\n   </ul>\n  </ul>\n </ul>\n <div>\n  <br/>\n </div>'

        # # for debug
        # utils.dbgSaveHtml(contentHtml, "%s_处理后" % curNote.title)

        # created=1597630594000, updated=1606826719000,
        # dateTimestampInt = curNote.updated
        dateTimestampInt = curNote.created # 1597630594000
        logging.debug("dateTimestampInt=%s", dateTimestampInt)
        dateTimestampFloat = float(dateTimestampInt) / 1000.0 # 1597630594.0
        logging.debug("dateTimestampFloat=%s", dateTimestampFloat)
        datetimeObj = utils.timestampToDatetime(dateTimestampFloat) # datetime.datetime(2020, 8, 17, 10, 16, 34)
        logging.debug("datetimeObj=%s", datetimeObj)
        outputFormat = "%Y-%m-%dT%H:%M:%S"
        postDatetimeStr = datetimeObj.strftime(format=outputFormat) # '2020-08-17T10:16:34'
        logging.debug("postDatetimeStr=%s", postDatetimeStr)

        tagNameList = self.evernote.getTagNameList(curNote)
        # tagNameList=['Mac', '切换', 'GPU', 'pmset', '显卡模式']
        logging.info("origin tagNameList=%s", tagNameList)
        curCategoryList = self.generateCategoryList(tagNameList)
        logging.info("curCategoryList=%s", curCategoryList)
        # curCategoryList=['Mac']
        for eachCategoryName in curCategoryList:
            if eachCategoryName in tagNameList:
                tagNameList.remove(eachCategoryName)
        logging.info("filtered tagNameList=%s", tagNameList)
        # tagNameList=['切换', 'GPU', 'pmset', '显卡模式']

        logging.info("Uploading note %s to wordpress post", curNote.title)
        isUploadOk, respInfo = self.wordpress.createPost(
            title=postTitle, # '【记录】Mac中用pmset设置GPU显卡切换模式'
            content=contentHtml, # '<html>\n <div>\n  折腾：\n </div>\n <div>\n  【已解决】Mac Pro 2018款发热量大很烫非常烫\n </div>\n <div>\n  期间， ... graphic cards\n    </li>\n   </ul>\n  </ul>\n </ul>\n <div>\n  <br/>\n </div>\n</html>'
            dateStr=postDatetimeStr, # '2020-08-17T10:16:34'
            slug=postSlug, # 'on_mac_pmset_is_used_set_gpu_graphics_card_switching_mode'
            categoryNameList=curCategoryList, # ['Mac']
            tagNameList=tagNameList, # ['切换', 'GPU', 'pmset', '显卡模式']
        )
        logging.info("%s to upload note to post, respInfo=%s", isUploadOk, respInfo)
        # {'id': 70563, 'url': 'https://www.crifan.com/?p=70563', 'slug': 'try_mi_band_4', 'link': 'https://www.crifan.com/?p=70563', 'title': '【记录】试用小米手环4'}
        return isUploadOk, respInfo

    @staticmethod
    def processNoteSlug(curNote):
        """Process note slug
            if empty, generate from title
                translate zhcn title to en, then process it

        Args:
            curNote (Note): evernote Note
        Returns:
            Note
        Raises:
        """
        sourceURL = curNote.attributes.sourceURL
        logging.debug("sourceURL=%s", sourceURL)

        if sourceURL:
            foundInvalidChar = re.search("\W+", sourceURL)
            isUrlValid = not foundInvalidChar
            if isUrlValid:
                logging.info("not change for valid sourceURL=%s", sourceURL)
                return curNote

        curZhcnTitle = curNote.title
        logging.debug("curZhcnTitle=%s", curZhcnTitle)
        # filter special: 【xx解决】 【记录】
        filteredTitle = re.sub("^【.+?】", "", curZhcnTitle)
        # 【已解决】Mac中给pip更换源以加速下载 -> Mac中给pip更换源以加速下载
        logging.debug("filteredTitle=%s", filteredTitle)
        isOk, respInfo = utils.translateZhcnToEn(filteredTitle)
        logging.debug("isOk=%s, respInfo=%s", isOk, respInfo)
        if isOk:
            enTitle = respInfo
            slug = crifanWordpress.generateSlug(enTitle)
            # 'check_royalty_details_with_assistant_at_huachang_college'
            curNote.attributes.sourceURL = slug
        else:
            logging.warning("Fail to translate title: %s", respInfo)

        return curNote


    ########################################
    # Code Block
    ########################################

    @staticmethod
    def processPostCodeblock(noteSoup):
        """Process Evernote Note en-codeblock <div> to Wordpress Post <pre>

        Args:
            noteSoup (Soup):  BeautifulSoup Soup of Evernote Note
        Returns:
            processed noteSoup
        Raises:
        """
        codeblockSoupList = crifanEvernote.getCodeblockSoupList(noteSoup)
        if codeblockSoupList:
            codeblockSoupNum = len(codeblockSoupList)
            logging.info("Found %d en-codeblock", codeblockSoupNum)
            for curCodeblockIdx, enCodeblockSoup in enumerate(codeblockSoupList):
                curCodeblockNum = curCodeblockIdx + 1
                logging.info("%s %d/%d %s", "-"*15, curCodeblockNum, codeblockSoupNum,"-"*15)
                logging.debug("enCodeblockSoup.prettify()=%s", enCodeblockSoup.prettify())
                preSoup = crifanEvernoteToWordpress.convertEnCodeblockDivToPre(enCodeblockSoup)
        else:
            logging.info("No found codeblock")

        return noteSoup
    
    @staticmethod
    def convertEnCodeblockDivToPre(enCodeblockSoup):
        """Convert Evernote Note <div style='...;-en-codeblock:true;'>xxx</div> to <pre>xxx</pre>

        Args:
            enCodeblockSoup (Soup): BeautifulSoup Soup of Evernote Note en-codeblock div
        Returns:
            processed soup of <pre>
        Raises:
        """
        enCodeblockSoup = crifanEvernoteToWordpress.filterEnCodeblock(enCodeblockSoup)

        codeStr = utils.getAllContents(enCodeblockSoup)
        logging.debug("codeStr=%s", codeStr)
        # codeStrStripped = utils.getAllContents(enCodeblockSoup, isStripped=True)
        # logging.info("codeStrStripped=%s", codeStrStripped)
        codeStr = re.sub("\n\n\n+", "\n\n\n", codeStr)
        logging.debug("after remove multile newline: codeStr=%s", codeStr)

        possibleLanguage = utils.detectProgramLanguage(codeStr)

        # <pre class="brush: shell; gutter: true">
        # method 1: use clear
        enCodeblockSoup.clear()
        enCodeblockSoup.name = "pre"
        del enCodeblockSoup["style"]
        enCodeblockSoup["class"] = "brush: %s; gutter: true" % possibleLanguage
        enCodeblockSoup.string = codeStr

        # # method 2: use replace_with -> NOT WORK
        # preNode = soup.new_tag("pre")
        # preNode["class"] = "brush: %s; gutter: true" % possibleLanguage
        # preNode.string = codeStr
        # enCodeblockSoup.replace_with(preNode)

        # for debug
        logging.info("Converted code block to: %s", enCodeblockSoup.prettify())
        logging.info("possibleLanguage=%s", possibleLanguage)
        logging.debug("")

        return enCodeblockSoup

    @staticmethod
    def filterEnCodeblock(enCodeblockSoup):
        """Filter to remove and process special conditions for Evernoet Note en-codeblock
            convert <br> to newline
            remove redundant unuseful newline and spaces
            remove unuseful <div><div></div></div>

        Args:
            enCodeblockSoup (BeautifulSoup soup): soup of Evernote Note en-codeblock div
        Returns:
            processed soup
        Raises:
        """
        # # for debug
        # utils.dbgSaveSoupToHtml(enCodeblockSoup, filenamePrefix="beforeFilter")

        # convert <br> to newline
        enCodeblockSoup = crifanEvernoteToWordpress.convertDivBrToNewline(enCodeblockSoup)

        # # for debug
        # utils.dbgSaveSoupToHtml(enCodeblockSoup, filenamePrefix="afterBrToNewline")

        # remove unuseful redundant newline and space
        enCodeblockSoup = crifanEvernoteToWordpress.removeRedundantNewlineSpace(enCodeblockSoup)

        # # for debug
        # utils.dbgSaveSoupToHtml(enCodeblockSoup, filenamePrefix="afterRemoveRedundantNewLineSpace")

        # remove unuseful <div><div></div></div>, which generated redundant newline
        enCodeblockSoup = crifanEvernoteToWordpress.removeUnusefulEmbedEmptyDiv(enCodeblockSoup)

        # # # for debug
        # utils.dbgSaveSoupToHtml(enCodeblockSoup, filenamePrefix="after_removeUnusefulEmbedEmptyDiv")

        # remove unuseful \n, which generated redundant newline
        enCodeblockSoup = crifanEvernoteToWordpress.removeUnusefulNewline(enCodeblockSoup)

        # # # for debug
        # utils.dbgSaveSoupToHtml(enCodeblockSoup, filenamePrefix="after_removeUnusefulNewline")

        return enCodeblockSoup

    @staticmethod
    def convertDivBrToNewline(enCodeblockSoup):
        """Convert 

                <div>
                    <div><br /></div>
                </div>

                <div>
                    <div><br /></div>
                    <div><br /></div>
                </div>

            to:

                <div>
                    
                </div>

                <div>
                    
                    
                </div>

        Args:
            enCodeblockSoup (Soup): soup of evernote post en-codeblock
        Returns:
            processed soup
        Raises:
        """
        allBrSoupList = enCodeblockSoup.find_all("br")
        for eachBrSoup in allBrSoupList:
            isExpectedBr = False
            curBrParent = eachBrSoup.parent
            if curBrParent:
                curBrParentName = curBrParent.name
                isParentDiv = curBrParentName == "div"
                if isParentDiv:
                    curBrParentParent = curBrParent.parent
                    if curBrParentParent:
                        curBrParentParentName = curBrParentParent.name
                        if curBrParentParentName == "div":
                            isExpectedBr = True

            if isExpectedBr:
                # newlineStr = "\n"
                # newlineStr = enCodeblockSoup.new_string("\n")
                # curBrParentParent.div.replace_with(newlineStr)
                # curBrParent.insert_after(newlineStr)
                emptylineStr = ""
                curBrParent.insert_after(emptylineStr)
                curBrParent.decompose()

        return enCodeblockSoup

    @staticmethod
    def isEmbedEmptyDivSoup(curSoup):
        """Check whether is <div><div></div></div> soup
            used for later remove it

        Args:
            soup (Soup): BeautifulSoup soup
        Returns:
            True/False
        Raises:
        """
        isEmbedEmptyDiv = False

        isChildIsDiv = curSoup.name == "div"
        if isChildIsDiv:
            childChilren = curSoup.children
            childChilList = list(childChilren)
            childChilNum = len(childChilList)
            isChildOnlySingleChild = childChilNum == 1
            if isChildOnlySingleChild:
                childSingleChild = childChilList[0]
                isSingleChildIsDiv = childSingleChild.name == "div"
                if isSingleChildIsDiv:
                    childSingleChildString = childSingleChild.string
                    childSingleChildString = childSingleChildString.strip()
                    isChildSingleChildHasContent = bool(childSingleChildString)
                    isChildSingleChildEmpty = not isChildSingleChildHasContent
                    if isChildSingleChildEmpty:
                        isEmbedEmptyDiv = True
                    else:
                        # for debug
                        logging.warning("unexpected the single child's child is not empty: %s", childSingleChildString)
                else:
                    # for debug
                    logging.warning("unexpected the single child's child is not div: %s", childSingleChild)
            else:
                # for debug
                logging.warning("unexpected child has more than one child: %s", childChilList)
        # else:
        #     # for debug
        #     logging.warning("unexpected child is not div: %s", curSoup)

        return isEmbedEmptyDiv

    @staticmethod
    def removeUnusefulEmbedEmptyDiv(enCodeblockSoup):
        """Remove unuseful embed and empty div

            remove:
                <div>
                    <div>
                        <div></div>
                    </div>
                    <div>
                        <div></div>
                    </div>
                </div>
            
            to:
                <div>
                </div>

        Args:
            soup (BeautifulSoup soup): soup of evernote post en-codeblock
        Returns:
            processed soup
        Raises:
        """
        toDestroySoupList = []

        allDivSoupList = enCodeblockSoup.find_all("div", recursive=False)
        for eachDivSoup in allDivSoupList:
            for eachChildSoup in eachDivSoup.children:
                # if each is <div><div></div></div> then remove it
                if crifanEvernoteToWordpress.isEmbedEmptyDivSoup(eachChildSoup):
                    # Note: do NOT decompose it here, otherwise will affect current loop, cause later item not processed
                    toDestroySoupList.append(eachChildSoup)
                else:
                    # for debug
                    logging.debug("not embed empty div: %s", eachChildSoup)

            for eachToDestroySoup in toDestroySoupList:
                eachToDestroySoup.decompose()

        return enCodeblockSoup

    @staticmethod
    def removeRedundantNewlineSpace(enCodeblockSoup):
        """Remove duplicated newline in string of <div>, which is inside en-codeblock
            convert
                <div>
                    ➜  src git:(master) ll
                </div>
            to
                <div>➜  src git:(master) ll</div>

        Args:
            enCodeblockSoup (BeautifulSoup soup): soup of Evernote Note en-codeblock div
        Returns:
            processed soup
        Raises:
        """
        # allDivSoupList = enCodeblockSoup.find_all("div")
        allDivSoupList = enCodeblockSoup.find_all("div", recursive=False)
        for eachDivSoup in allDivSoupList:
            divChildren = eachDivSoup.children
            divChildList = list(divChildren)
            childNum = len(divChildList)
            isOnlySingleChind = childNum == 1
            if isOnlySingleChind:
                singleChild = divChildList[0]
                isChildIsStr = isinstance(singleChild, NavigableString)
                if isChildIsStr:
                    divString = singleChild.string
                    # '\n   ➜\xa0\xa0android_app_security_crack git:(master) cd src\n  '
                    isNewlineContentNewline = re.match("^\n\s*.+\n\s*$", divString)
                    if isNewlineContentNewline:
                        newStrValue = re.sub("^\n\s*(?P<divContent>.+)\n\s*$", "\g<divContent>", divString)
                        # '   ➜\xa0\xa0android_app_security_crack git:(master) cd src'
                        eachDivSoup.string = newStrValue
            #         else:
            #             # for debug
            #             logging.warning("unexpected div string not match rule: %s", eachDivSoup)
            #     else:
            #         # for debug
            #         logging.warning("unexpected child is not string: %s", eachDivSoup)
            # else:
            #     # for debug
            #     logging.warning("unexpected more child: %s", eachDivSoup)

        return enCodeblockSoup

    @staticmethod
    def removeUnusefulNewline(enCodeblockSoup):
        """Remove unuseful \n string inside en-codeblock

        Args:
            enCodeblockSoup (BeautifulSoup soup): soup of Evernote Note en-codeblock div
        Returns:
            processed soup
        Raises:
        """
        for curChild in enCodeblockSoup.children:
            isChildIsStr = isinstance(curChild, NavigableString)
            if isChildIsStr:
                isNewline = curChild == "\n"
                if isNewline:
                    # curChild.decompose()
                    curChild.extract()

        return enCodeblockSoup


    @staticmethod
    def removeDivInUlOl(curSoup):
        """Remove unuseful redundant div node inside ul->li or ol->li
        """
        curSoupType = type(curSoup)
        logging.debug("curSoupType=%s, curSoup=%s", curSoupType, curSoup)
        # curSoupType=<class 'bs4.element.Tag'>, curSoup=<ul><li><div>0 为集成显卡</div></li><li><div>1 为独立显卡</div></li><li><div>2 为自动切换</div></li></ul>

        if not isinstance(curSoup, Tag):
            # curSoupType=<class 'bs4.element.NavigableString'>, curSoup=0 为集成显卡
            return

        childSoupList = list(curSoup.children)

        if curSoup.name != "div":
            # self is not div, just process each child
            for eachChildSoup in childSoupList:
                crifanEvernoteToWordpress.removeDivInUlOl(eachChildSoup)
            return

        parentSoup = curSoup.parent
        logging.debug("parentSoup=%s", parentSoup)
        if parentSoup:
            if parentSoup.name != "li":
                # has parent, but no li
                return
        else:
            # no parent?
            logging.warning("to support")

        # isOnlyChildNotSoup = False
        # if childSoupList:
        #     childNum = len(childSoupList)
        #     if childNum == 1:
        #         onliyChildSoup = childSoupList[0]
        #         isOnlyChildIsSoup = isinstance(onliyChildSoup, Tag)
        #         if isOnlyChildIsSoup:
        #             # process it
        #             parentSoup.string = curSoup.string
        #             parentSoup.children = []
        #             logging.info("parentSoup=%s", parentSoup)
        #         else:
        #             logging.info("type(onliyChildSoup)=%s", type(onliyChildSoup))
        #             # type(onliyChildSoup)=<class 'bs4.element.NavigableString'>
        #             return
        #     else:
        #         for eachChildSoup in childSoupList:
        #             removeDivInUlOl(eachChildSoup)
        # else:
        #     # no child
        #     logging.warning("to support")

        # process it
        # parentSoup.contents = curSoup.contents
        # parentSoup.children = []

        # curSoup.name = "li"
        logging.debug("before replace: curSoup=%s", curSoup)
        logging.debug("before replace: parentSoup=%s", parentSoup)
        # curSoupCopy = copy.deepcopy(curSoup)
        # parentSoup.replace_with(curSoupCopy)
        # parentSoup.children = curSoup.children

        # Prerequisite: li only have one div child !
        parentSoup.div.unwrap()
        logging.debug("aftre  replace: parentSoup=%s", parentSoup)
        logging.debug("aftre  replace: curSoup=%s", curSoup)

        return

    @staticmethod
    def processSpanInUlOl(listSoup):
        """Process span inside ul/ol soup
            1. remove redundant empty span
                remove:
                        <span style="font-weight: bold;">
                    </span>

            2. remove redundant newline inside span string value
                convert:
                    <span style="font-weight: bold; color: rgb(255, 38, 0);">\n           约2万~3万\n</span>
                to:
                    <span style="font-weight: bold; color: rgb(255, 38, 0);">约2万~3万</span>

        Args:
            listSoup (soup): Evernote Note ul/ol soup
        Returns:
            processed soup
        Raises:
        """
        spanSoupList = listSoup.find_all("span")
        if spanSoupList:
            toDestroySpanList = []
            for eachSpanSoup in spanSoupList:
                childList = list(eachSpanSoup.children)
                childNum = len(childList)
                isOnlySingleChild = childNum == 1
                if isOnlySingleChild:
                    singleChild = childList[0]
                    # singleChild = None
                    # for eachChild in eachSpanSoup.children:
                    #     singleChild = eachChild
                    #     break
                    if isinstance(singleChild, NavigableString):
                        singleChildStr = str(singleChild)
                        if re.match("^\s*$", singleChildStr):
                            toDestroySpanList.append(eachSpanSoup)
                        elif re.match("^\s+.+\s+$", singleChildStr):
                            removedNewlineStr = re.sub("\s+(?P<content>.+)\s+", "\g<content>", singleChildStr)
                            # singleChild.string = removedNewlineStr
                            eachSpanSoup.string = removedNewlineStr

            for tDestroySpan in toDestroySpanList:
                tDestroySpan.decompose()

        # # for debug
        # utils.dbgSaveSoupToHtml(listSoup)

        return listSoup

    @staticmethod
    def processListIndent(curNote):
        """process list (ul/ol/...) indent

        Args:
            curNote (Note): evernote Note
        Returns:
            Note
        Raises:
        """
        # soup = utils.htmlToSoup(curNote.content)
        # enNoteSoup = soup.find("en-note")
        # soup = crifanEvernote.noteContentToSoup(curNote)
        # Note: makesure removed top html, then following can search out ul and ul list with recursive=False
        soup = crifanEvernote.noteContentToSoup(curNote, isKeepTopHtml=False)

        # allSubUlSoupList = soup.find_all("ul")
        # allSubUlSoupNum = len(allSubUlSoupList)
        # logging.info("Found %d all sub level ul list", allSubUlSoupNum)

        topUlSoupList = soup.find_all("ul", recursive=False)
        topOlSoupList = soup.find_all("ol", recursive=False)

        # for debug: need debug to make sure support ol
        if topOlSoupList:
            logging.info("Found ol list")

        topListSoupList = []
        topListSoupList.extend(topUlSoupList)
        topListSoupList.extend(topOlSoupList)

        if topListSoupList:
            directUlSoupNum = len(topListSoupList)
            logging.info("Found %d top level ul/ol list", directUlSoupNum)

            for curUlIdx, eachListSoup in enumerate(topListSoupList):
                logging.info("%s %s %s", "-"*20, curUlIdx, "-"*20)
                logging.debug("before eachListSoup=%s", eachListSoup)
                crifanEvernoteToWordpress.removeDivInUlOl(eachListSoup)
                crifanEvernoteToWordpress.processSpanInUlOl(eachListSoup)
                logging.debug("after  eachListSoup=%s", eachListSoup)

            # soup changed, write back to note content
            updatedNoteHtml = crifanEvernote.soupToNoteContent(soup)
            curNote.content = updatedNoteHtml
        else:
            logging.info("No ul/ol list for %s", curNote.title)

        return curNote
