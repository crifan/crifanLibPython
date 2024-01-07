# Function: iOS related functions
# Author: Crifan Li
# Update: 20240107
# Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/thirdParty/crifaniOS.py

import re

def isObjcFunctionName(funcName):
  """
  check is ObjC function name or not
  eg:
    "+[WAAvatarStringsActions editAvatar]" -> True
    "-[ParentGroupInfoViewController initWithParentGroupChatSession:userContext:recentlyLinkedGroupJIDs:]" -> True
    "-[OKEvolveSegmentationVC proCard]_116" -> True
    "-[WAAvatarStickerUpSellSupplementaryView .cxx_destruct]" -> True
    "sub_10004C6D8" -> False
    "protocol witness for RawRepresentable.init(rawValue:) in conformance UIFont.FontWeight" -> True
  """
  isMatchObjcFuncName = re.match("^[\-\+]\[\w+ [\w\.\:]+\]\w*$", funcName)
  isObjcFuncName = bool(isMatchObjcFuncName)
  # print("funcName=%s -> isObjcFuncName=%s" % (funcName, isObjcFuncName))
  return isObjcFuncName

def isObjcMsgSendFuncName(funcName):
  """
  check function name is _objc_msgSend$xxx or not
  eg:
    "_objc_msgSend$arrayByAddingObjectsFromArray:" -> True, "arrayByAddingObjectsFromArray:"
    "_objc_msgSend$addObject:_AB00" -> True, "addObject:_AB00"
    "objc_msgSend$initWithKeyValueStore_namespace_binaryCoders_X22toX0_X23toX2_X24toX4" -> True, "initWithKeyValueStore_namespace_binaryCoders_X22toX0_X23toX2_X24toX4"
  """
  isOjbcMsgSend = False
  selectorStr = None
  # _objc_msgSend$arrangedSubviews
  # _objc_msgSend$arrayByAddingObjectsFromArray:
  # _objc_msgSend$arrangeFromView:toView:progress:forwardDirection:
  # objcMsgSendMatch = re.match("^_*objc_msgSend\$(?P<selectorStr>[\w\:]+¸)$", funcName)
  # objcMsgSendMatch = re.match("^_*objc_msgSend\$(?P<selectorStr>[\w\:]+)(?P<renamedAddrSuffix>_[A-Za-z0-9]+)?$", funcName)
  objcMsgSendMatch = re.match("^_*objc_msgSend\$(?P<selectorStr>[\w\:]+)$", funcName)
  # print("objcMsgSendMatch=%s" % objcMsgSendMatch)
  if objcMsgSendMatch:
    selectorStr = objcMsgSendMatch.group("selectorStr")
    # print("selectorStr=%s" % selectorStr)
    isOjbcMsgSend = True
  # print("isOjbcMsgSend=%s, selectorStr=%s" % (isOjbcMsgSend, selectorStr))
  return isOjbcMsgSend, selectorStr
