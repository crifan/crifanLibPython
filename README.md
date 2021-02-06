# crifanLibPython

最后更新：`20210206`

## 目录结构

```bash
├── README.md
├── python2
│   └── crifanLib.py                          # Python2 旧版库文件，所有函数都在一个文件里
└── python3
    └── crifanLib                             # Python 3 新版库文件，根据功能，分成独立的多个库文件
        ├── __init__.py
        ├── crifanCookie.py                   # cookie
        ├── crifanCsv.py                      # csv
        ├── crifanDatetime.py                 # datetime
        ├── crifanDict.py                     # dict
        ├── crifanEmail.py                    # email
        ├── crifanFile.py                     # file, folder
        ├── crifanGeography.py                # geographic
        ├── crifanHtml.py                     # html
        ├── crifanHttp.py                     # http
        ├── crifanList.py                     # list
        ├── crifanLogging.py                  # logging
        ├── crifanMath.py                     # math
        ├── crifanMultimedia.py               # multimedia: audio, image, video
        ├── crifanString.py                   # string
        ├── crifanSystem.py                   # system
        ├── crifanTemplate.py                 # template，新增crifanXXX的参考模板
        ├── crifanUrl.py                      # url
        ├── demo                              # 不同的库函数的demo示例
        │   ├── __init__.py
        │   ├── crifanBaiduOcrDemo.py
        │   ├── crifanCsvDemo.py
        │   ├── crifanDatetimeDemo.py
        │   ├── crifanDetectCtrlChar.py
        │   ├── crifanDictDemo.py
        │   ├── crifanFileDemo.py
        │   ├── crifanLoggingDemo.py
        │   ├── crifanMultimediaDemo.py
        │   ├── input                         # demo的输入内容
        │   │   ├── audio
        │   │   │   ├── actual_aac_but_suffix_mp3.mp3
        │   │   │   ├── fake_audio_actual_image.wav
        │   │   │   └── real_mp3_format.mp3
        │   │   ├── image
        │   │   │   ├── 20191219_172616_drawRect_40x40.jpg
        │   │   │   └── 20191219_172616_drawRect_40x40_1.jpg
        │   │   └── video
        │   │       └── video_normalWatermark_480w360h.mp4
        │   ├── mac_show_control_char.txt
        │   └── output                        # demo的输出内容
        │       ├── OutputDemoData_ByDictList.csv
        │       ├── OutputDemoData_ByHeaderAndList.csv
        │       └── testLogging.log
        └── thirdParty                        # 第三方库的心得整理
            ├── crifanAliyun.py               # aliyuyn
            ├── crifanAndroid.py              # android: adb
            ├── crifanBaiduOcr.py             # baidu OCR
            ├── crifanBeautifulsoup.py        # beautifulsoup
            ├── crifanEvernote.py             # Evernote
            ├── crifanEvernoteToWordpress.py  # evernote to wordpress
            ├── crifanFlask.py                # flask
            ├── crifanMongodb.py              # MongoDB
            ├── crifanMysql.py                # mysql
            ├── crifanOpenpyxl.py             # openpyxl
            ├── crifanRequests.py             # requests
            ├── crifanWda.py                  # iOS automation: wda
            ├── crifanWechat.py               # wechat
            └── crifanWordpress.py            # wordpress
```

## 解释

主要包含：

* crifan的Python
  * `Python 2`的库函数
    * 文件位置：`python2/crifanLib.py`
    * 如何使用这些库函数
      * [详解crifan的Python库：crifanLib.py](https://www.crifan.com/files/doc/docbook/crifanlib_python/release/html/crifanlib_python.html)
  * `Python 3`的库函数
    * 文件位置：`python3/crifanLib`目录下的各个独立文件
    * 如何使用这些库函数
      * demo
        * 详见`python3/crifanLib/demo`下面对应的demo文件
      * 代码段
        * `python3/crifanLib/thirdParty/crifanBaiduOcr.py`
          * [百度OCR · Python常用代码段](https://book.crifan.com/books/python_common_code_snippet/website/common_code/multimedia/image/baidu_ocr.html)
        * `python3/crifanLib/thirdParty/crifanPillow.py`
          * [Pillow · Python常用代码段](https://book.crifan.com/books/python_common_code_snippet/website/common_code/multimedia/image/pillow.html)
