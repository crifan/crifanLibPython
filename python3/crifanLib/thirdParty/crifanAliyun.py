#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanAliyun.py
Function: crifanLib's Wechat related functions.
Version: v20190121
Note:
1. latest version and more can found here:
https://github.com/crifan/crifanLibPython
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "v20190121"
__copyright__ = "Copyright (c) 2019, Crifan Li"
__license__ = "GPL"

try:
    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcore.request import CommonRequest
except ImportError:
    print("crifanAliyun: please install `pip install aliyun-python-sdk-core-v3` before using aliyun")

import json

################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanAliyun"


ALIYUN_SDK_SMS_ACCESSKEYID = "LxxxE"
ALIYUN_SDK_SMS_ACCESSSECRET = "sxxxq"
ALIYUN_SDK_SMS_REGION_ID = "cn-hangzhou"

ALIYUN_SDK_SMS_SIGNNAME = "已审核后的签名"
ALIYUN_SDK_SMS_TEMPLATECODE = "SMS_1xxx0"

################################################################################
# Global Variable
################################################################################
gVal = {
}

gConst = {
}

################################################################################
# Internal Function
################################################################################



################################################################################
# Aliyun Function
################################################################################


def aliyunSendSmsCode(acsClient, phoneNumbers, smsCode):
    """
        call aliyun sms api to send sms code to phone number(s)
        more detail refer: 
            【已解决】通过阿里云短信服务SDK去用python实现发送验证码短信
            http://www.crifan.com/python_call_aliyun_sms_sdk_send_short_message_verify_code

    :param phoneNumbers: single or multiple(seperate by ',') phone number string, eg: '15011112222' / '15011112222,15233334444'
    :param smsCode: 6 digit string, eg: 123456
    :return: true if send ok, false if send failed
    """
    templateParam = '{"code":"%s"}' % smsCode

    commonReq = CommonRequest()
    commonReq.set_accept_format('json')
    commonReq.set_domain('dysmsapi.aliyuncs.com')
    commonReq.set_method('POST')
    commonReq.set_version('2017-05-25')
    commonReq.set_action_name('SendSms')

    commonReq.add_query_param('RegionId', ALIYUN_SDK_SMS_REGION_ID)
    commonReq.add_query_param('PhoneNumbers', phoneNumbers) #
    commonReq.add_query_param('SignName', ALIYUN_SDK_SMS_SIGNNAME)
    commonReq.add_query_param('TemplateCode', ALIYUN_SDK_SMS_TEMPLATECODE)
    commonReq.add_query_param('TemplateParam', templateParam)

    response = acsClient.do_action(commonReq) # ACS=Alibaba Cloud Service
    respStr = str(response, encoding='utf-8')
    # normal: '{"Message":"OK","RequestId":"A216483A-5E87-49A3-9142-276821F5E10E","BizId":"166810747624160111^0","Code":"OK"}'
    # abnormal:
    # '{"Message":"没有访问权限","RequestId":"4029409A-7460-4E1F-806A-A75B5778B167","Code":"isp.RAM_PERMISSION_DENY"}'
    # {"Recommend":"https://error-center.aliyun.com/status/search?Keyword=InvalidVersion&source=PopGw","Message":"Specified parameter Version is not valid.","RequestId":"6A6711BD-F18E-445C-9B6F-E7F9F6EEE9E0","HostId":"dysmsapi.aliyuncs.com","Code":"InvalidVersion"}
    # {'Message': '触发天级流控Permits:10', 'RequestId': '85AF2393-85E3-4A12-BD92-290851E9E8A4', 'Code': 'isv.BUSINESS_LIMIT_CONTROL'}
    respJson = json.loads(respStr)
    respMessage = respJson["Message"]
    respCode = respJson["Code"]
    if (respMessage == "OK") and (respCode == "OK"):
        isSentOk = True
        errCode = ""
        errMsg = ""
    else:
        isSentOk = False
        errCode = respCode
        errMsg = respMessage

    return isSentOk, errCode, errMsg

################################################################################
# Test
################################################################################

def testAcs():

    acsClient = AcsClient(
        ak=ALIYUN_SDK_SMS_ACCESSKEYID,
        secret=ALIYUN_SDK_SMS_ACCESSSECRET,
        region_id=ALIYUN_SDK_SMS_REGION_ID
    )
    smsCode = "123456"
    # phoneNumbers = "13800001111"
    phoneNumbers = "13800001111,15200001111"
    isSentOk, errCode, errMsg = aliyunSendSmsCode(acsClient, phoneNumbers, smsCode)
    print("second time: phoneNumbers=%s, smsCode=%s -> isSentOk=%s, errCode=%s, errMsg=%s" % (phoneNumbers, smsCode, isSentOk, errCode, errMsg))


if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))
    # testAcs()