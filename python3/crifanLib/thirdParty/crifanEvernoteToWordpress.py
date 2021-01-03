# Function: Evernote to Wordpress related functions
# Author: Crifan Li
# Update: 20210103
# Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/thirdParty/crifanEvernoteToWordpress.py

import sys
import logging
import copy
import re
from bs4 import BeautifulSoup

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
        logging.info("%s to upload resource %s to wordpress", isUploadImgOk, imgGuid)
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
        logging.info("Complete sync image %s to evernote note %s", uploadedImgUrl, curNoteDetail.title)

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
            logging.info("uploaded url %s", uploadedImgUrl)
            # "https://www.crifan.com/files/pic/uploads/2020/03/f6956c30ef0b475fa2b99c2f49622e35.png"
            # relace en-media to img
            respNote = self.syncNoteImage(curNoteDetail, curResource, uploadedImgUrl, curResList)
            # logging.info("Complete sync image %s to note %s", uploadedImgUrl, respNote.title)
        else:
            logging.warning("Failed to upload image resource %s to wordpress", curResource)

        return uploadedImgUrl

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

        curCategoryList = []
        if tagNameList:
            firstTag = tagNameList.pop(0) # 'Mac'
            curCategoryList.append(firstTag)
        logging.info("curCategoryList=%s", curCategoryList)
        # curCategoryList=['Mac']
        logging.info("tagNameList=%s", tagNameList)
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