#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanFfmpeg.py
Function: crifanLib's ffmpeg related functions
Version: 20210112
Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/thirdParty/crifanFfmpeg.py
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20210112"
__copyright__ = "Copyright (c) 2021, Crifan Li"
__license__ = "GPL"

import os
import re

from crifanLib.crifanSystem import runCommand, getCommandOutput


################################################################################
# Config
################################################################################

################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanFfmpeg"

################################################################################
# Global Variable
################################################################################

################################################################################
# Internal Function
################################################################################

#----------------------------------------
# Audio & Video
#----------------------------------------

def formatFfmpegTimeStr(timeValue, seperatorHms=":", seperatorMs="."):
    """
        (1) format time to 00:00:03.110, for pass into ffmpeg to use:
            ffmpeg -i show_65586_video.mp4 -ss 00:00:03.110 -to 00:00:06.110 -b:a 128k extracted_audio_segment.mp3
        (2) also use format to 000003110, used for normal file name:
            audio_000003110_000006110.mp3

        Note:
            timeValue is class of datetime.time, NOT time
    """
    millisecond = int(timeValue.microsecond / 1000)
    ffmpegTimeStr = "%02d%s%02d%s%02d%s%03d" % (
        timeValue.hour, seperatorHms,
        timeValue.minute, seperatorHms,
        timeValue.second, seperatorMs,
        millisecond)
    return ffmpegTimeStr

def extractAudioFromVideo(
        videoFullPath,
        startTime=None,
        endTime= None,
        audioFullPath="",
        audioType="mp3",
        isOutputLog=False,
        isAskOverwrite=False,
    ):
    """
        extract specified time duration(startTime - endTime) auido (default mp3) file from video(.mp4) file
        Note:
            if startTime and endTime not specified, will ouput whole file audio
            internal using ffmpeg do convertion from mp4 to audio

        params:
        * `videoFullPath`: /video/path/video_name.mp4
        * `startTime`: start time of type datetime.time
        * `endTime`: end time of type datetime.time
        * `audioFullPath`:
            * `""`: -> /video/path/ + generated_audio_name.mp3
            * `"/audio/path/audio_name.mp3"`: /audio/path/audio_name.mp3
        * `isOutputLog`: ffmpeg show console log or not
            if not, will redirect to null device to omit it
        * `isAskOverwrite`: when existed file, whether ask overwrite or not
            default Not ask, that is force overwrite

        return: (bool, str, str)
                    True/False, audio path, error message string
    """
    extractIsOk = False
    extractedAudioPath = ""
    errMsg = "Unknown Error"

    if not audioFullPath:
        videoPath = os.path.dirname(videoFullPath)
        videoName = os.path.basename(videoFullPath)
        videoNameNoSuffix, videoSuffix = os.path.splitext(videoName) # 'show_14322648_video', '.mp4'

        timeDurationStr = ""
        if startTime and endTime:
            startTimeStrForName = formatFfmpegTimeStr(startTime, "", "")
            endTimeStrForName = formatFfmpegTimeStr(endTime, "", "")
            timeDurationStr = "_" + startTimeStrForName + "_" + endTimeStrForName

        audioFilename = videoNameNoSuffix + timeDurationStr + "." + audioType # 'show_14322648_video.mp3'
        audioFullPath = os.path.join(videoPath, audioFilename)

    timeDurationPara = ""
    if startTime and endTime:
        startTimeStrFfmpeg = formatFfmpegTimeStr(startTime)
        endTimeStrFfmpeg = formatFfmpegTimeStr(endTime)
        timeDurationPara = "-ss %s -to %s" % (startTimeStrFfmpeg, endTimeStrFfmpeg)

    extraPara = ""
    if not isAskOverwrite:
        extraPara += "-y"

    redirectOutputPara = ""
    if not isOutputLog:
        redirectOutputPara += "2> /dev/null"

    ffmpegCmd = "ffmpeg %s -i %s %s -b:a 128k %s %s" % (
        extraPara, videoFullPath, timeDurationPara, audioFullPath, redirectOutputPara)
    # print("ffmpegCmd=%s" % ffmpegCmd)

    # Example:
    # ffmpeg -y -i show_65586_video.mp4 -ss 00:00:03.110 -to 00:00:06.110 -b:a 128k show_65586_audio_000003110_000006110.mp3 2> /dev/null
    # ffmpeg -y -i /xxx/show_13304984_video.mp4 -ss 00:00:00.104 -to 00:00:04.566 -b:a 128k /xxx/user/5253/show/13304984/show_13304984_audio_000000104_000004566.mp3 2> /dev/null
    # ffmpeg -y -i show_65586_video.mp4 -b:a 128k show_65586_audio.mp3 2> /dev/null

    extractIsOk, errMsg = runCommand(ffmpegCmd)
    if extractIsOk:
        extractedAudioPath = audioFullPath

    return extractIsOk, extractedAudioPath, errMsg

#----------------------------------------
# Video
#----------------------------------------

def detectVideoDimension(videoFullPath):
    """
        detect video dimention(width x height) using ffprobe
    """
    # print("detectVideoDimension: videoFullPath=%s" % videoFullPath)
    videoWidth = 0
    videoHeight = 0

    ffprobeCmd = 'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 %s' % videoFullPath
    # print("ffprobeCmd=%s" % ffprobeCmd)
    isRunCmdOk, consoleOutput = getCommandOutput(ffprobeCmd)
    # print("isRunCmdOk=%s, consoleOutput=%s" % (isRunCmdOk, consoleOutput))
    if isRunCmdOk:
        # extract width and height
        videoDimensionStr = consoleOutput # '640x360\n'
        foundDimension = re.search("(?P<videoWidth>\d+)x(?P<videoHeight>\d+)", videoDimensionStr)
        # print("foundDimension=%s" % foundDimension)
        if foundDimension:
            videoWidth = foundDimension.group("videoWidth")
            videoWidth = int(videoWidth)
            videoHeight = foundDimension.group("videoHeight")
            videoHeight = int(videoHeight)
            # print("videoWidth=%s, videoHeight=%s" % (videoWidth, videoHeight))

    return (videoWidth, videoHeight)

def removeVideoWatermark(inputVideoFullPath, outputVideoFullPath, watermarkPositionDict, isOverwrite=False, isVerbose=False):
    """
        remove video water mark using ffmpeg
    """
    # print("removeVideoWatermark: inputVideoFullPath=%s, outputVideoFullPath=%s, watermarkPositionDict=%s" % (inputVideoFullPath, outputVideoFullPath, watermarkPositionDict))
    # ffmpeg -i input_video.mp4 -vf "delogo=x=490:y=30:w=130:h=50" -c:a copy output_video.mp4
    # ffmpegCmd = 'ffmpeg -i %s -vf "delogo=x=490:y=30:w=130:h=50" -c:a copy %s' % (inputVideoFullPath, outputVideoFullPath)
    extraOptionList = []
    if isOverwrite:
        optionOverwrite = "-y"
        extraOptionList.append(optionOverwrite)
    if not isVerbose:
        optionLessOutput = "-hide_banner -loglevel error"
        extraOptionList.append(optionLessOutput)
    optionAvoidHang = "-nostdin"
    extraOptionList.append(optionAvoidHang)
    extraOptionStr = " ".join(extraOptionList)
    print("extraOptionStr=%s" % extraOptionStr)
    ffmpegCmd = 'ffmpeg %s -i %s -vf "delogo=x=%d:y=%d:w=%d:h=%d" -c:a copy %s' % \
        (extraOptionStr, inputVideoFullPath, watermarkPositionDict["x"], watermarkPositionDict["y"], watermarkPositionDict["w"], watermarkPositionDict["h"], outputVideoFullPath)
    print("ffmpegCmd=%s" % ffmpegCmd)
    # ffmpegCmd=ffmpeg -hide_banner -loglevel error -nostdin -i /xxx/video_normalWatermark_480w360h.mp4 -vf "delogo=x=324:y=28:w=140:h=53" -c:a copy /xxx/video_normalWatermark_480w360h_removedWatermark.mp4
    isRemovedWatermarkOk, errMsg = runCommand(ffmpegCmd)
    # print("isRemovedWatermarkOk=%s, errMsg=%s" % (isRemovedWatermarkOk, errMsg))
    return isRemovedWatermarkOk, errMsg

#----------------------------------------
# Audio
#----------------------------------------

def splitAudio(
        inputAudioFullPath,
        startTime,
        endTime,
        outputAudioFullPath="",
        isOutputLog=False,
        isAskOverwrite=False,
    ):
    """
        split specified time duration(startTime - endTime) auido (default mp3) file from input (whole) audio (normally .mp4) file
        Note:
            internal using ffmpeg, your system must installed ffmpeg

        params:
        * `inputAudioFullPath`: /whole/audio/path/input_audio_name.mp3
        * `startTime`: start time of type datetime.time
        * `endTime`: end time of type datetime.time
        * `outputAudioFullPath`:
            * `""`: -> /whole/audio/path/ + input_audio_name_{startTime}_{endTime}.mp3
            * `"/output/audio/path/output_audio_name.mp3"`: /output/audio/path/output_audio_name.mp3
        * `isOutputLog`: ffmpeg show console log or not
            if not, will redirect to null device to omit it
        * `isAskOverwrite`: when existed file, whether ask overwrite or not
            default Not ask, that is force overwrite

        return: (bool, str, str)
                    bool: extract OK or not
                    str: splitted audio full path
                    str: error message string
    """
    extractIsOk = False
    splittedAudioFullPath = ""
    errMsg = "Unknown Error"

    if not outputAudioFullPath:
        inputAudioPath = os.path.dirname(inputAudioFullPath)
        inputAudioName = os.path.basename(inputAudioFullPath)
        inputAudioNameNoSuffix, inputAudioSuffix = os.path.splitext(inputAudioName) # 'show_14322648_audio', '.mp3'

        startTimeStrForName = formatFfmpegTimeStr(startTime, "", "")
        endTimeStrForName = formatFfmpegTimeStr(endTime, "", "")
        timeDurationStr = "_" + startTimeStrForName + "_" + endTimeStrForName

        audioFilename = inputAudioNameNoSuffix + timeDurationStr + inputAudioSuffix # 'show_14322648_audio_000004237_000006336.mp3'
        outputAudioFullPath = os.path.join(inputAudioPath, audioFilename)

    startTimeStrFfmpeg = formatFfmpegTimeStr(startTime)
    endTimeStrFfmpeg = formatFfmpegTimeStr(endTime)
    timeDurationPara = "-ss %s -to %s" % (startTimeStrFfmpeg, endTimeStrFfmpeg) # '-ss 00:00:04.237 -to 00:00:06.336'

    extraPara = ""
    if not isAskOverwrite:
        extraPara += "-y"

    redirectOutputPara = ""
    if not isOutputLog:
        redirectOutputPara += "2> /dev/null"

    ffmpegCmd = "ffmpeg %s -i %s %s -b:a 128k %s %s" % (
        extraPara, inputAudioFullPath, timeDurationPara, outputAudioFullPath, redirectOutputPara)
    # print("ffmpegCmd=%s" % ffmpegCmd)

    # Example:
    # ffmpeg -y -i /xxx/show_14322648_audio.mp3 -ss 00:00:04.237 -to 00:00:06.336 -b:a 128k /xxx/show_14322648_audio_000004237_000006336.mp3 2> /dev/null

    extractIsOk, errMsg = runCommand(ffmpegCmd)
    if extractIsOk:
        splittedAudioFullPath = outputAudioFullPath

    return extractIsOk, splittedAudioFullPath, errMsg

################################################################################
# Test
################################################################################

if __name__ == '__main__':
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))