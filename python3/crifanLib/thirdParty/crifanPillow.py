#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanPillow.py
Function: crifanLib's pillow/PIL related functions
Version: 20210312
Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/thirdParty/crifanPillow.py
Usage: https://book.crifan.com/books/python_common_code_snippet/website/common_code/multimedia/image/pillow.html
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20210312"
__copyright__ = "Copyright (c) 2021, Crifan Li"
__license__ = "GPL"

import re
import io
import os
import copy

from PIL import Image
from PIL import ImageDraw

# cfgDefaultImageResample = None
cfgDefaultImageResample = Image.BICUBIC # Image.LANCZOS

from crifanLib.crifanFile import isFileObject, findNextNumberFilename, formatSize
from crifanLib.crifanDatetime  import getCurDatetimeStr

################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanPillow"

################################################################################
# Global Variable
################################################################################

################################################################################
# Internal Function
################################################################################

def saveImage(pillowImage, outputImageFile):
    """Save pillow/PIL Image to file, while convert image mode to avoid exception

    Args:
        pillowImage (Image): pillow(PIL) Image
        outputImageFile (str): output image filename
    Returns:
    Raises:
    """
    foundJpeg = re.search("\.jpe?g$", outputImageFile, re.I) # <re.Match object; span=(66, 70), match='.jpg'>
    isSaveJpeg = bool(foundJpeg) # True
    if isSaveJpeg:
        if pillowImage.mode in ("RGBA", "P"): # 'RGBA'
            # JPEG not support 'Alpha' transparency, so need convert to RGB, before save RGBA/P to jpeg
            pillowImage = pillowImage.convert("RGB")
            # <PIL.Image.Image image mode=RGB size=1600x720 at 0x107E5DAF0>
    # 'debug/Android/app/游戏app/screenshot/20201208_142621_drawRect_154x42.jpg'
    pillowImage.save(outputImageFile)

def resizeImage(inputImage,
                newSize,
                resample=cfgDefaultImageResample,
                outputFormat=None,
                outputImageFile=None
                ):
    """
        resize input image
        resize normally means become smaller, reduce size
    :param inputImage: image file object(fp) / filename / binary bytes
    :param newSize: (width, height)
    :param resample: PIL.Image.NEAREST, PIL.Image.BILINEAR, PIL.Image.BICUBIC, or PIL.Image.LANCZOS
        https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.thumbnail
    :param outputFormat: PNG/JPEG/BMP/GIF/TIFF/WebP/..., more refer:
        https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html
        if input image is filename with suffix, can omit this -> will infer from filename suffix
    :param outputImageFile: output image file filename
    :return:
        input image file filename: output resized image to outputImageFile
        input image binary bytes: resized image binary bytes
    """
    openableImage = None
    if isinstance(inputImage, str):
        openableImage = inputImage
    elif isFileObject(inputImage):
        openableImage = inputImage
    elif isinstance(inputImage, bytes):
        inputImageLen = len(inputImage)
        openableImage = io.BytesIO(inputImage)

    if openableImage:
        imageFile = Image.open(openableImage)
    elif isinstance(inputImage, Image.Image):
        imageFile = inputImage
    # <PIL.PngImagePlugin.PngImageFile image mode=RGBA size=3543x3543 at 0x1065F7A20>
    imageFile.thumbnail(newSize, resample)
    if outputImageFile:
        # save to file
        # imageFile.save(outputImageFile)
        saveImage(imageFile, outputImageFile)
        imageFile.close()
    else:
        # save and return binary byte
        imageOutput = io.BytesIO()
        # imageFile.save(imageOutput)
        outputImageFormat = None
        if outputFormat:
            outputImageFormat = outputFormat
        elif imageFile.format:
            outputImageFormat = imageFile.format
        imageFile.save(imageOutput, outputImageFormat)
        imageFile.close()
        compressedImageBytes = imageOutput.getvalue()
        compressedImageLen = len(compressedImageBytes)
        compressRatio = float(compressedImageLen)/float(inputImageLen)
        print("%s -> %s, resize ratio: %d%%" % (inputImageLen, compressedImageLen, int(compressRatio * 100)))
        return compressedImageBytes

def imageDrawRectangle(inputImgOrImgPath,
    rectLocation,
    outlineColor="green",
    outlineWidth=0,
    isShow=False,
    isAutoSave=True,
    saveTail="_drawRect_%wx%h",
    isDrawClickedPosCircle=True,
    clickedPos=None,
):
    """Draw a rectangle for image (and a small circle), and show it,

    Args:
        inputImgOrImgPath (Image/str): a pillow(PIL) Image instance or image file path
        rectLocation (tuple/list/Rect): the rectangle location, (x, y, width, height)
        outlineColor (str): Color name
        outlineWidth (int): rectangle outline width
        isShow (bool): True to call image.show() for debug
        isAutoSave (bool): True to auto save the image file with drawed rectangle
        saveTail(str): save filename tail part. support format %x/%y/%w/%h use only when isAutoSave=True
        clickedPos (tuple): x,y of clicked postion; default None; if None, use the center point
        isDrawClickedPosCircle (bool): draw small circle in clicked point
    Returns:
        modified image
    Raises:
    """
    inputImg = inputImgOrImgPath
    if isinstance(inputImgOrImgPath, str):
        inputImg = Image.open(inputImgOrImgPath)
    draw = ImageDraw.Draw(inputImg)

    isRectObj = False
    hasX = hasattr(rectLocation, "x")
    hasY = hasattr(rectLocation, "y")
    hasWidth = hasattr(rectLocation, "width")
    hasHeight = hasattr(rectLocation, "height")
    isRectObj = hasX and hasY and hasWidth and hasHeight
    if isinstance(rectLocation, tuple):
        x, y, w, h = rectLocation
    if isinstance(rectLocation, list):
        x = rectLocation[0]
        y = rectLocation[1]
        w = rectLocation[2]
        h = rectLocation[3]
    elif isRectObj:
        x = rectLocation.x
        y = rectLocation.y
        w = rectLocation.width
        h = rectLocation.height

    w = int(w)
    h = int(h)
    x0 = x
    y0 = y
    x1 = x0 + w
    y1 = y0 + h
    draw.rectangle(
        [x0, y0, x1, y1],
        # fill="yellow",
        # outline="yellow",
        outline=outlineColor,
        width=outlineWidth,
    )

    if isDrawClickedPosCircle:
        # radius = 3
        # radius = 2
        radius = 4
        # circleOutline = "yellow"
        circleOutline = "red"
        circleLineWidthInt = 1
        # circleLineWidthInt = 3

        if clickedPos:
            clickedX, clickedY = clickedPos
        else:
            clickedX = x + w/2
            clickedY = y + h/2
        startPointInt = (int(clickedX - radius), int(clickedY - radius))
        endPointInt = (int(clickedX + radius), int(clickedY + radius))
        draw.ellipse([startPointInt, endPointInt], outline=circleOutline, width=circleLineWidthInt)

    if isShow:
        inputImg.show()

    if isAutoSave:
        saveTail = saveTail.replace("%x", str(x))
        saveTail = saveTail.replace("%y", str(y))
        saveTail = saveTail.replace("%w", str(w))
        saveTail = saveTail.replace("%h", str(h))

        inputImgPath = None
        if isinstance(inputImgOrImgPath, str):
            inputImgPath = str(inputImgOrImgPath)
        elif inputImg.filename:
            inputImgPath = str(inputImg.filename)

        if inputImgPath:
            imgFolderAndName, pointSuffix = os.path.splitext(inputImgPath)
            imgFolderAndName = imgFolderAndName + saveTail
            newImgPath = imgFolderAndName + pointSuffix
            newImgPath = findNextNumberFilename(newImgPath)
        else:
            curDatetimeStr = getCurDatetimeStr() # '20191219_143400'
            suffix = str(inputImg.format).lower() # 'jpeg'
            newImgFilename = "%s%s.%s" % (curDatetimeStr, saveTail, suffix)
            imgPathRoot = os.getcwd()
            newImgPath = os.path.join(imgPathRoot, newImgFilename)

        # inputImg.save(newImgPath)
        saveImage(inputImg, newImgPath)

    return inputImg

def bytesToImage(imgBytes):
    """generate Pillow Image from binary bytes

    Args:
        imgBytes (bytes): image binary bytes
    Returns:
        pillow(PIL) Image
    Raises:
    """
    imgBytesIO = io.BytesIO(imgBytes)
    curImg = Image.open(imgBytesIO)
    return curImg

def imageToBytes(imgObj, isUseOriginObj=False):
    """Get binary data bytes from Image.Image instance

    Args:
        imgObj (Image): the Pillow Image instance
        isUseOriginObj (bool): use orgin Image object (call save() will modify orgin object) or copy out temp Image object
    Returns:
        bytes, binary data of Image
    Raises:
    """
    if isUseOriginObj:
        curImgObj = imgObj
    else:
        curImgObj = copy.deepcopy(imgObj)
    imgBytesIO = io.BytesIO()
    curImgObj.save(imgBytesIO, curImgObj.format) # 'TiffImageFile' object has no attribute 'use_load_libtiff'

    imgBytes = imgBytesIO.getvalue()
    imgBytesIO.close()
    return imgBytes


# def getImageBytes(curImg):
#     """get bytes from Pillow Image

#     Args:
#         pillowImg (Image): a pillow(PIL) Image instance
#     Returns:
#         image binary bytes
#     Raises:
#     """
#     imageIO = io.BytesIO()
#     curImg.save(imageIO, curImg.format)
#     imgBytes = imageIO.getvalue()
#     return imgBytes

def convertImageFormat(imgObj, outputFormat=None, isOptimize=False, isKeepPrevValues=True):
    """Convert image format

    Args:
        imgObj (Image): the Pillow Image instance
        outputFormat (str): Image format, eg: "JPEG"/"PNG"/"BMP"/"TIFF"/...
            more refer: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html
        isOptimize (bool): do optimize when using save to convert format
        isKeepPrevValues (bool): keep previous property values, such as: filename
    Returns:
        bytes, binary data of Image
    Raises:
    """
    newImgObj = imgObj
    if outputFormat and (imgObj.format != outputFormat):
        imgBytesIO = io.BytesIO()

        jpegNotSupportFormatList = ["RGBA", "P"]
        if (outputFormat == "JPEG") and (imgObj.mode in jpegNotSupportFormatList):
            imgObj = imgObj.convert("RGB")

        if isOptimize:
            imgObj.save(imgBytesIO, outputFormat, optimize=True)
        else:
            imgObj.save(imgBytesIO, outputFormat)
        newImgObj = Image.open(imgBytesIO)
        if isKeepPrevValues:
            if hasattr(imgObj, "filename") and imgObj.filename:
                newImgObj.filename = imgObj.filename

    return newImgObj

def resizeSingleImage(imgBytes, newSize=None):
    """Draw a rectangle for image (and a small circle), and show it,

    Args:
        imgBytes (bytes): input image binary bytes
        newSize (tuple): resized to max size (width, height)
    Returns:
        minResizedImgBytes(bytes), resizedImgFormat(str), newSize(tuple)
    Raises:
    """
    defaulMaxWidth = 1024
    # defaultMaxHeight = 768
    defaultMaxHeight = 1024

    # for some fixed size, resize to smaller fixed size
    fixedSizeDict = {
        # Xiaomi9 screenshot size
        (1080, 2340): (360, 780),
        (2340, 1080): (780, 360),
        # Xiaomi9 camera orgin size
        (4000, 3000): (1024, 768),
        (3000, 4000): (768, 1024),
        # Smartisian M1L screenshot size
        (1080, 1920): (360, 640),
        (1920, 1080): (640, 360),
        # other phone
        (576, 1024): (360, 640),
        (1024, 576): (640, 360),
    }

    curImg = bytesToImage(imgBytes)
    curImgFormat = curImg.format
    curSize = (curImg.width, curImg.height) # 1080, 2340

    # # for debug
    # curImg.show()

    if not newSize:
        if curSize in fixedSizeDict.keys():
            newSize = fixedSizeDict[curSize]
        else:
            newSize = defaulMaxWidth, defaultMaxHeight

    if curImgFormat == "PNG":
        anotherImgFormat = "JPEG"
    elif curImgFormat == "JPEG":
        anotherImgFormat = "PNG"
    else:
        # anotherImgFormat = "PNG"
        anotherImgFormat = "JPEG"

    resizedCurImgBytes = resizeImage(imgBytes, newSize, outputFormat=curImgFormat)
    curResizeRatio = calcResizeRatio(resizedCurImgBytes, curImg)

    resizedAnotherImgBytes = resizeImage(imgBytes, newSize, outputFormat=anotherImgFormat)
    anotherResizeRatio = calcResizeRatio(resizedAnotherImgBytes, curImg)

    minResizedImgBytes = None
    resizedImgFormat = None
    if curResizeRatio < anotherResizeRatio:
        minResizedImgBytes = resizedCurImgBytes
        resizedImgFormat = curImgFormat
    else:
        minResizedImgBytes = resizedAnotherImgBytes
        resizedImgFormat = anotherImgFormat

    return minResizedImgBytes, resizedImgFormat, newSize

def calcResizeRatio(resizedImgBytes, originImg):
    """Calculate imgage resize ratio

    Args:
        resizedImgBytes (bytes): resized image binary bytes
        originImg (Image): original image Object
    Returns:
        resize ratio (float)
    Raises:
    """
    originSize = originImg.width, originImg.height
    originBytes = imageToBytes(originImg)

    resizedImg = bytesToImage(resizedImgBytes)
    resizedSize = resizedImg.width, resizedImg.height

    originLen = len(originBytes)
    resizedLen = len(resizedImgBytes)
    resizeRatio = float(resizedLen) / float(originLen)
    resizeRatioPercent = int(resizeRatio * 100)
    printStr = "\t-> Compress ratio=%d%%, from [fmt=%s, size=%sx%s, len=%s] to [fmt=%s, size=%sx%s, len=%s]" %  (
        resizeRatioPercent, 
            originImg.format, originSize[0], originSize[1], formatSize(originLen),
            resizedImg.format, resizedSize[0], resizedSize[1], formatSize(resizedLen)
    )
    print(printStr)
    # logging.debug(printStr)
    return resizeRatio

################################################################################
# Test
################################################################################

if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))