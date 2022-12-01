import sys
import os
curFolder = os.path.abspath(__file__)
parentFolder = os.path.dirname(curFolder)
parentParentFolder = os.path.dirname(parentFolder)
# parentParentParentFolder = os.path.dirname(parentParentFolder)
sys.path.append(curFolder)
sys.path.append(parentFolder)
sys.path.append(parentParentFolder)
# sys.path.append(parentParentParentFolder)

from crifanLogging import loggingInit

import logging

def demoLoggingInit():
  # ---------- New demo ----------
  # 1. generate file name
  # copy getFilenameNoPointSuffix from python3\crifanLib\crifanFile.py
  # copy getCurDatetimeStr from python3\crifanLib\crifanDatetime.py
  curLogFile = "%s_%s.log" % (getFilenameNoPointSuffix(__file__), getCurDatetimeStr())
  # 'TIAutoOrder_20221201_174058.log'
  curLogFullFile = os.path.join("debug", "log", curLogFile)
  # 'debug\\log\\TIAutoOrder_20221201_174112.log'

  # 2. call loggingInit then call loggging self 
  crifanLogging.loggingInit(filename=curLogFullFile)
  # or set format
  # crifanLogging.loggingInit(filename=curLogFullFile, consoleLogFormat="%(asctime)s %(lineno)-4d %(levelname)-7s %(message)s")
  logging.debug("log debug")
  logging.info("log info")
  logging.warning("log waring")
  logging.error("log error")
  logging.fatal("log fatal")

  # or direct call for test testLogging
  # crifanLogging.testLogging()

  # Note： NOT call loggingInit twice/more than once
  #   -> otherwise will output multiple repeated log

  # ---------- Old demo ----------
  # loggingInit(
  #   "crifanLoggingDemo.log",
  #   # consoleLogFormat="%(asctime)s %(lineno)-4d %(levelname)-7s %(message)s"
  # )
  # logging.info("you can see this info in File and Console")
  # # File crifanLoggingDemo.log:
  # # 2018/12/01 09:55:01 crifanLoggingDemo.py:21   INFO    you can see this info in File and Console
  # # Console:
  # # 20181201 09:49:38 21   INFO    you can see this info in File and Console

if __name__ == "__main__":
  demoLoggingInit()
