# Function: Wordpress related functions
# Author: Crifan Li
# Update: 20201128
# Online: https://github.com/crifan/crifanLibPython/blob/master/crifanLib/crifanWordpress.py

# import sys
import logging

import requests

# from libs.crifan import utils

class crifanWordpress(object):
    """Use Python operate Wordpress via REST api

        Posts | REST API Handbook | WordPress Developer Resources
        https://developer.wordpress.org/rest-api/reference/posts/#schema-comment_status
    """

    def __init__(self, host, jwtToken, requestsProxies=None):
        self.host = host # 'https://www.crifan.com'
        self.authorization = "Bearer %s" % jwtToken # 'Bearer xxx'
        self.requestsProxies = requestsProxies # {'http': 'http://127.0.0.1:58591', 'https': 'http://127.0.0.1:58591'}

        self.apiMedia = self.host + "/wp-json/wp/v2/media" # 'https://www.crifan.com/wp-json/wp/v2/media'
        self.apiPosts = self.host + "/wp-json/wp/v2/posts" # 'https://www.crifan.com/wp-json/wp/v2/posts'

    @staticmethod
    def processCreateResponse(resp):
        """Process common wordpress POST response for 
            /wp-json/wp/v2/media
            /wp-json/wp/v2/posts

        Args:
            resp (Response): requests response
        Returns:
            (bool, dict)
                True, created item info
                False, error detail
        Raises:
        """
        isCreateOk, respInfo = False, {}

        if resp.ok:
            respJson = resp.json()
            logging.debug("respJson=%s", respJson)
            """
            for /wp-json/wp/v2/media
                {
                    "id": 70401,
                    "date": "2020-03-13T22:34:29",
                    "date_gmt": "2020-03-13T14:34:29",
                    "guid": {
                        "rendered": "https://www.crifan.com/files/pic/uploads/2020/03/f6956c30ef0b475fa2b99c2f49622e35.png",
                        "raw": "https://www.crifan.com/files/pic/uploads/2020/03/f6956c30ef0b475fa2b99c2f49622e35.png"
                    },
                    "modified": "2020-03-13T22:34:29",
                    ...
                    "slug": "f6956c30ef0b475fa2b99c2f49622e35",
                    "status": "inherit",
                    "type": "attachment",
                    "link": "https://www.crifan.com/f6956c30ef0b475fa2b99c2f49622e35/",
                    "title": {
                        "raw": "f6956c30ef0b475fa2b99c2f49622e35",
                        "rendered": "f6956c30ef0b475fa2b99c2f49622e35"
                    },
            
            for /wp-json/wp/v2/posts
                {
                    "id": 70410,
                    "date": "2020-02-27T21:11:49",
                    "date_gmt": "2020-02-27T13:11:49",
                    "guid": {
                        "rendered": "https://www.crifan.com/?p=70410",
                        "raw": "https://www.crifan.com/?p=70410"
                    },
                    "modified": "2020-02-27T21:11:49",
                    "modified_gmt": "2020-02-27T13:11:49",
                    "password": "",
                    "slug": "mac_pip_change_source_server_to_spped_up_download",
                    "status": "draft",
                    "type": "post",
                    "link": "https://www.crifan.com/?p=70410",
                    "title": {
                        'raw": "【已解决】Mac中给pip更换源以加速下载",
                        "rendered": "【已解决】Mac中给pip更换源以加速下载"
                    },
                    "content": {
                        ...

            """
            newId = respJson["id"]
            newUrl = respJson["guid"]["rendered"]
            newSlug = respJson["slug"]
            newLink = respJson["link"]
            newTitle = respJson["title"]["rendered"]
            logging.info("newId=%s, newUrl=%s, newSlug=%s, newLink=%s, newTitle=%s", newId, newUrl, newSlug, newLink, newTitle)
            isCreateOk = True
            respInfo = {
                "id": newId, # 70393
                "url": newUrl, # https://www.crifan.com/files/pic/uploads/2020/03/f6956c30ef0b475fa2b99c2f49622e35.png
                "slug": newSlug, # f6956c30ef0b475fa2b99c2f49622e35
                "link": newLink, # https://www.crifan.com/f6956c30ef0b475fa2b99c2f49622e35/
                "title": newTitle, # f6956c30ef0b475fa2b99c2f49622e35
            }
        else:
            isCreateOk = False
            # respInfo = resp.status_code, resp.text
            respInfo = {
                "errCode": resp.status_code,
                "errMsg": resp.text,
            }

        logging.info("isCreateOk=%s, respInfo=%s", isCreateOk, respInfo)
        return isCreateOk, respInfo

    def createMedia(self, contentType, filename, mediaBytes):
        """Create wordpress media (image)
            by call REST api: POST /wp-json/wp/v2/media

        Args:
            contentType (str): content type
            filename (str): attachment file name
            mediaBytes (bytes): media binary bytes
        Returns:
            (bool, dict)
                True, uploaded media info
                False, error detail
        Raises:
        """
        curHeaders = {
            "Authorization": self.authorization,
            "Content-Type": contentType,
            "Accept": "application/json",
            'Content-Disposition': 'attachment; filename=%s' % filename,
        }
        logging.debug("curHeaders=%s", curHeaders)
        # curHeaders={'Authorization': 'Bearer eyJ0xxxyyy.zzzB4', 'Content-Type': 'image/png', 'Content-Disposition': 'attachment; filename=f6956c30ef0b475fa2b99c2f49622e35.png'}
        createMediaUrl = self.apiMedia
        resp = requests.post(
            createMediaUrl,
            proxies=self.requestsProxies,
            headers=curHeaders,
            data=mediaBytes,
        )
        logging.info("resp=%s", resp)

        isUploadOk, respInfo = crifanWordpress.processCreateResponse(resp)
        return isUploadOk, respInfo

    def createPost(self,
            title,
            content,
            dateStr,
            slug,
            status="draft",
            postFormat="standard"
        ):
        """Create wordpress standard post
            by call REST api: POST /wp-json/wp/v2/posts

        Args:
            title (str): post title
            content (str): post content of html
            dateStr (str): date string
            slug (str): post slug url
            status (str): status, default to 'draft'
            postFormat (str): post format, default to 'standard'
        Returns:
            (bool, dict)
                True, uploaded post info
                False, error detail
        Raises:
        """
        curHeaders = {
            "Authorization": self.authorization,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        logging.info("curHeaders=%s", curHeaders)
        postDict = {
            "title": title,
            "content": content,
            # "date_gmt": dateStr,
            "date": dateStr,
            "slug": slug,
            "status": status,
            "format": postFormat,
            # TODO: featured_media, categories, tags, excerpt
        }
        logging.debug("postDict=%s", postDict)
        # postDict={'title': '【已解决】Mac中给pip更换源以加速下载', 'content': '<div>\n  折腾：\n </div>。。。。。。。。。</div>\n', 'date': '20200227T211149', 'slug': 'mac_pip_change_source_server_to_spped_up_download', 'status': 'draft', 'format': 'standard'}
        createPostUrl = self.apiPosts
        resp = requests.post(
            createPostUrl,
            proxies=self.requestsProxies,
            headers=curHeaders,
            # data=json.dumps(postDict),
            json=postDict, # internal auto do json.dumps
        )
        logging.info("resp=%s", resp)

        isUploadOk, respInfo = crifanWordpress.processCreateResponse(resp)
        return isUploadOk, respInfo
