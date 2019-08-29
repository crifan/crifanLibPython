import sys
import os
curFolder = os.path.abspath(__file__)
parentFolder = os.path.dirname(curFolder)
parentParentFolder = os.path.dirname(parentFolder)
parentParentParentFolder = os.path.dirname(parentParentFolder)
sys.path.append(curFolder)
sys.path.append(parentFolder)
sys.path.append(parentParentFolder)
sys.path.append(parentParentParentFolder)

import datetime
from crifanMultimedia import resizeImage
from crifanMultimedia import detectAudioMetaInfo, removeVideoWatermark, detectVideoDimension

def testFilename():
  imageFilename = "/Users/crifan/dev/tmp/python/resize_image_demo/hot day.png"
  outputImageFilename = "/Users/crifan/dev/tmp/python/resize_image_demo/hot day_300x300.png"
  print("imageFilename=%s" % imageFilename)
  beforeTime = datetime.datetime.now()
  resizeImage(imageFilename, (300, 300), outputImageFile=outputImageFilename)
  afterTime = datetime.datetime.now()
  print("procesTime: %s" % (afterTime - beforeTime))

  outputImageFilename = "/Users/crifan/dev/tmp/python/resize_image_demo/hot day_800x800.png"
  beforeTime = datetime.datetime.now()
  resizeImage(imageFilename, (800, 800), outputImageFile=outputImageFilename)
  afterTime = datetime.datetime.now()
  print("procesTime: %s" % (afterTime - beforeTime))


def testFileObject():
  imageFilename = "/Users/crifan/dev/tmp/python/resize_image_demo/hot day.png"
  imageFileObj = open(imageFilename, "rb")
  outputImageFilename = "/Users/crifan/dev/tmp/python/resize_image_demo/hot day_600x600.png"
  beforeTime = datetime.datetime.now()
  resizeImage(imageFileObj, (600, 600), outputImageFile=outputImageFilename)
  afterTime = datetime.datetime.now()
  print("procesTime: %s" % (afterTime - beforeTime))


def testBinaryBytes():
  imageFilename = "/Users/crifan/dev/tmp/python/resize_image_demo/take tomato.png"
  imageFileObj = open(imageFilename, "rb")
  imageBytes = imageFileObj.read()
  # return binary bytes
  beforeTime = datetime.datetime.now()
  resizedImageBytes = resizeImage(imageBytes, (800, 800))
  afterTime = datetime.datetime.now()
  print("procesTime: %s" % (afterTime - beforeTime))
  print("len(resizedImageBytes)=%s" % len(resizedImageBytes))

  # save to file
  outputImageFilename = "/Users/crifan/dev/tmp/python/resize_image_demo/hot day_750x750.png"
  beforeTime = datetime.datetime.now()
  resizeImage(imageBytes, (750, 750), outputImageFile=outputImageFilename)
  afterTime = datetime.datetime.now()
  print("procesTime: %s" % (afterTime - beforeTime))

  imageFileObj.close()


def demoResizeImage():
  testFilename()
  testFileObject()
  testBinaryBytes()


def demoDetectAudioMeta():
  curPath = os.path.dirname(__file__)
  inputAudioList = [
    "input/audio/actual_aac_but_suffix_mp3.mp3",
    "input/audio/real_mp3_format.mp3",
    "not_exist_audio.wav",
    "input/audio/fake_audio_actual_image.wav",
  ]

  for eachAudioPath in inputAudioList:
    eachAudioFullPath = os.path.join(curPath, eachAudioPath)
    isOk, errOrInfo = detectAudioMetaInfo(eachAudioFullPath)
    print("isOk=%s, errOrInfo=%s" % (isOk, errOrInfo))

def demoRemoveVideoWatermark():
  curPath = os.path.dirname(__file__)
  inputVideoFilePath = "input/video/video_normalWatermark_480w360h.mp4"
  inputVideoFullPath = os.path.join(curPath, inputVideoFilePath)
  outputVideoFilePath = "output/video/video_normalWatermark_480w360h_removedWatermark.mp4"
  outputVideoFullPath = os.path.join(curPath, outputVideoFilePath)
  watermarkPostionDict = {
    "x": 324,
    "y": 28,
    "w": 140,
    "h": 53
  }
  # isRemovedWatermarkOk, errMsg = removeVideoWatermark(inputVideoFullPath, outputVideoFullPath, watermarkPostionDict)
  isRemovedWatermarkOk, errMsg = removeVideoWatermark(inputVideoFullPath, outputVideoFullPath, watermarkPostionDict, isOverwrite=True, isVerbose=True)
  print("isRemovedWatermarkOk=%s, errMsg=%s" % (isRemovedWatermarkOk, errMsg))

def demoDetectVideoDimension():
  curPath = os.path.dirname(__file__)
  inputVideoFilePath = "input/video/video_normalWatermark_480w360h.mp4"
  inputVideoFullPath = os.path.join(curPath, inputVideoFilePath)
  videoWidth, videoHeight = detectVideoDimension(inputVideoFullPath)
  print("videoWidth=%s, videoHeight=%s" % (videoWidth, videoHeight))

if __name__ == "__main__":
  # demoResizeImage()
  # imageFilename=/Users/crifan/dev/tmp/python/resize_image_demo/hot day.png
  # procesTime: 0:00:00.619377
  # procesTime: 0:00:00.745228
  # procesTime: 0:00:00.606060
  # 1146667 -> 753258, resize ratio: 65%
  # procesTime: 0:00:00.773289
  # len(resizedImageBytes)=753258
  # procesTime: 0:00:00.738237

  # demoDetectAudioMeta()
  # isOk=True, errOrInfo={'duration': 637.8, 'channels': 2, 'sampleRate': 44100}
  # isOk=True, errOrInfo={'duration': 2.3510204081632655, 'channels': 2, 'sampleRate': 44100}
  # isOk=False, errOrInfo=detect audio info error: [Errno 2] No such file or directory: '/Users/crifan/dev/dev_root/crifan/crifanLibPython/crifanLib/demo/not_exist_audio.wav'
  # isOk=False, errOrInfo=detect audio info error: 

  # demoRemoveVideoWatermark()
  # isRemovedWatermarkOk=True, errMsg=

  demoDetectVideoDimension()
  # videoWidth=480, videoHeight=360
