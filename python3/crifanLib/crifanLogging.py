#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Filename: crifanLogging.py
Function: crifanLib's logging related functions.
Version: 20221201
Latest: https://github.com/crifan/crifanLibPython/blob/master/python3/crifanLib/crifanLogging.py
"""

__author__ = "Crifan Li (admin@crifan.com)"
__version__ = "20221201"
__copyright__ = "Copyright (c) 2022, Crifan Li"
__license__ = "GPL"

import logging
import os
import sys

try:
    import curses  # type: ignore
except ImportError:
    curses = None

################################################################################
# Config
################################################################################

LOG_FORMAT_FILE = "%(asctime)s %(filename)s:%(lineno)-4d %(levelname)-7s %(message)s"
# https://docs.python.org/3/library/time.html#time.strftime
LOG_FORMAT_FILE_DATETIME = "%Y/%m/%d %H:%M:%S"
LOG_LEVEL_FILE = logging.DEBUG
# LOG_FORMAT_CONSOLE = "%(asctime)s %(filename)s:%(lineno)-4d %(levelname)-7s %(message)s"
LOG_FORMAT_CONSOLE = "%(color)s%(asctime)s %(filename)s:%(lineno)-4d %(levelname)-7s%(end_color)s %(message)s"
LOG_FORMAT_CONSOLE_DATETIME = "%Y%m%d %H:%M:%S"
LOG_LEVEL_CONSOLE = logging.INFO
# LOG_LEVEL_CONSOLE = logging.DEBUG


################################################################################
# Constant
################################################################################
CURRENT_LIB_FILENAME = "crifanLogging"

# refered: 
#   logzero
#       https://github.com/metachris/logzero/blob/master/logzero/__init__.py
#       https://github.com/metachris/logzero/blob/master/logzero/colors.py
#   wiki
#       https://en.wikipedia.org/wiki/ANSI_escape_code#CSI_codes

# CSI = '\033['
# OSC = '\033]'

# CSI = '\e['
# OSC = '\e]'

# ESCAPE = '\033' # octal expression
ESCAPE = '\x1b' # hex expression
CSI = ESCAPE + '['
OSC = ESCAPE + ']'

# BEL = '\007'

def code_to_chars(code):
    return CSI + str(code) + 'm'

# def set_title(title):
#     return OSC + '2;' + title + BEL

# def clear_screen(mode=2):
#     return CSI + str(mode) + 'J'

# def clear_line(mode=2):
#     return CSI + str(mode) + 'K'

class AnsiCodes(object):
    def __init__(self):
        # the subclasses declare class attributes which are numbers.
        # Upon instantiation we define instance attributes, which are the same
        # as the class attributes but wrapped with the ANSI escape sequence
        for name in dir(self):
            if not name.startswith('_'):
                value = getattr(self, name)
                charValue = code_to_chars(value)
                setattr(self, name, charValue)


class AnsiCursor(object):
    def UP(self, n=1):
        return CSI + str(n) + 'A'

    def DOWN(self, n=1):
        return CSI + str(n) + 'B'

    def FORWARD(self, n=1):
        return CSI + str(n) + 'C'

    def BACK(self, n=1):
        return CSI + str(n) + 'D'

    def POS(self, x=1, y=1):
        return CSI + str(y) + ';' + str(x) + 'H'


class AnsiForeground(AnsiCodes):
    DEFAULT = 39

    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    LIGHT_GRAY = 37

    # These are fairly well supported, but not part of the standard.
    DARK_GRAY = 90
    LIGHT_RED = 91
    LIGHT_GREEN = 92
    LIGHT_YELLOW = 93
    LIGHT_BLUE = 94
    LIGHT_MAGENTA = 95
    LIGHT_CYAN = 96

    WHITE = 97

class AnsiBackground(AnsiCodes):
    DEFAULT = 49

    BLACK = 40
    RED = 41
    GREEN = 42
    YELLOW = 43
    BLUE = 44
    MAGENTA = 45
    CYAN = 46
    LIGHT_GRAY = 47

    # These are fairly well supported, but not part of the standard.
    DARK_GRAY = 100
    LIGHT_RED = 101
    LIGHT_GREEN = 102
    LIGHT_YELLOW = 103
    LIGHT_BLUE = 104
    LIGHT_MAGENTA = 105
    LIGHT_CYAN = 106

    WHITE = 107


class AnsiStyle(AnsiCodes):
    # Set
    SET_BOLD = 1 # Bold/Bright
    SET_DIM = 2
    SET_UNDERLINED = 4
    SET_BLINK = 5
    SET_REVERSE = 7 # Reverse (invert the foreground and background colors)
    SET_HIDDEN = 8 # Hidden (useful for passwords)

    # Reset
    RESET_ALL = 0 # Reset all attributes
    RESET_BOLD = 21
    RESET_DIM = 22
    RESET_UNDERLINED = 24
    RESET_BLINK = 25
    RESET_REVERSE = 27
    RESET_HIDDEN = 28


gForeground = AnsiForeground()
gBackground = AnsiBackground()
gStyle = AnsiStyle()
gCursor = AnsiCursor()

# LogLevelToColor = {
#     logging.DEBUG: gForeground.CYAN,
#     logging.INFO: gForeground.GREEN,
#     logging.WARNING: gForeground.YELLOW,
#     logging.ERROR: gForeground.RED
# }

# Python 2+3 compatibility settings for logger
bytes_type = bytes
if sys.version_info >= (3, ):
    unicode_type = str
    basestring_type = str
    xrange = range
else:
    # The names unicode and basestring don't exist in py3 so silence flake8.
    unicode_type = unicode  # noqa
    basestring_type = basestring  # noqa

_TO_UNICODE_TYPES = (unicode_type, type(None))

def to_unicode(value):
    """
    Converts a string argument to a unicode string.
    If the argument is already a unicode string or None, it is returned
    unchanged.  Otherwise it must be a byte string and is decoded as utf8.
    """
    if isinstance(value, _TO_UNICODE_TYPES):
        return value
    if not isinstance(value, bytes):
        raise TypeError(
            "Expected bytes, unicode, or None; got %r" % type(value))
    return value.decode("utf-8")


def _safe_unicode(s):
    try:
        return to_unicode(s)
    except UnicodeDecodeError:
        return repr(s)


def _stderr_supports_color():
    # Colors can be forced with an env variable
    if os.getenv('LOGZERO_FORCE_COLOR') == '1':
        return True

    # Windows supports colors with colorama
    if os.name == 'nt':
        return True

    # Detect color support of stderr with curses (Linux/macOS)
    if curses and hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
        try:
            curses.setupterm()
            if curses.tigetnum("colors") > 0:
                return True

        except Exception:
            pass

    return False

class LogFormatter(logging.Formatter):
    """
    Log formatter used in Tornado. Key features of this formatter are:
    * Color support when logging to a terminal that supports it.
    * Timestamps on every log line.
    * Robust against str/bytes encoding problems.
    """
    DEFAULT_FORMAT = '%(color)s[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s'
    DEFAULT_DATE_FORMAT = '%y%m%d %H:%M:%S'
    DEFAULT_COLORS = {
        logging.DEBUG: gForeground.CYAN,
        logging.INFO: gForeground.GREEN,
        logging.WARNING: gForeground.YELLOW,
        logging.ERROR: gForeground.RED,
        logging.FATAL: gBackground.RED,
    }

    def __init__(self,
                 color=True,
                 fmt=DEFAULT_FORMAT,
                 datefmt=DEFAULT_DATE_FORMAT,
                 colors=DEFAULT_COLORS):
        r"""
        :arg bool color: Enables color support.
        :arg string fmt: Log message format.
          It will be applied to the attributes dict of log records. The
          text between ``%(color)s`` and ``%(end_color)s`` will be colored
          depending on the level if color support is on.
        :arg dict colors: color mappings from logging level to terminal color
          code
        :arg string datefmt: Datetime format.
          Used for formatting ``(asctime)`` placeholder in ``prefix_fmt``.
        .. versionchanged:: 3.2
           Added ``fmt`` and ``datefmt`` arguments.
        """
        logging.Formatter.__init__(self, datefmt=datefmt)

        self._fmt = fmt
        self._colors = {}
        self._normal = ''

        if color and _stderr_supports_color():
            self._colors = colors
            self._normal = gForeground.DEFAULT

    def format(self, record):
        try:
            message = record.getMessage()
            assert isinstance(message,
                              basestring_type)  # guaranteed by logging
            # Encoding notes:  The logging module prefers to work with character
            # strings, but only enforces that log messages are instances of
            # basestring.  In python 2, non-ascii bytestrings will make
            # their way through the logging framework until they blow up with
            # an unhelpful decoding error (with this formatter it happens
            # when we attach the prefix, but there are other opportunities for
            # exceptions further along in the framework).
            #
            # If a byte string makes it this far, convert it to unicode to
            # ensure it will make it out to the logs.  Use repr() as a fallback
            # to ensure that all byte strings can be converted successfully,
            # but don't do it by default so we don't add extra quotes to ascii
            # bytestrings.  This is a bit of a hacky place to do this, but
            # it's worth it since the encoding errors that would otherwise
            # result are so useless (and tornado is fond of using utf8-encoded
            # byte strings wherever possible).
            record.message = _safe_unicode(message)
        except Exception as e:
            record.message = "Bad message (%r): %r" % (e, record.__dict__)

        record.asctime = self.formatTime(record, self.datefmt)

        if record.levelno in self._colors:
            record.color = self._colors[record.levelno]
            record.end_color = self._normal
        else:
            record.color = record.end_color = ''

        formatted = self._fmt % record.__dict__

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            # exc_text contains multiple lines.  We need to _safe_unicode
            # each line separately so that non-utf8 bytes don't cause
            # all the newlines to turn into '\n'.
            lines = [formatted.rstrip()]
            lines.extend(
                _safe_unicode(ln) for ln in record.exc_text.split('\n'))
            formatted = '\n'.join(lines)
        return formatted.replace("\n", "\n    ")

################################################################################
# Logging
################################################################################

def loggingInit(filename = None,
                fileLogLevel = LOG_LEVEL_FILE,
                fileLogFormat = LOG_FORMAT_FILE,
                fileLogDateFormat = LOG_FORMAT_FILE_DATETIME,
                enableConsole = True,
                consoleLogLevel = LOG_LEVEL_CONSOLE,
                consoleLogFormat = LOG_FORMAT_CONSOLE,
                consoleLogDateFormat = LOG_FORMAT_CONSOLE_DATETIME,
                ):
    """
    init logging for both log to file and console

    :param filename: input log file name
        if not passed, use current lib filename
    :return: none
    """
    logFilename = ""
    if filename:
        logFilename = filename
    else:
        # logFilename = __file__ + ".log"
        # '/Users/crifan/dev/dev_root/xxx/crifanLogging.py.log'
        logFilename = CURRENT_LIB_FILENAME + ".log"

    # logging.basicConfig(
    #                 level    = fileLogLevel,
    #                 format   = fileLogFormat,
    #                 datefmt  = fileLogDateFormat,
    #                 filename = logFilename,
    #                 encoding = "utf-8",
    #                 filemode = 'w')

    # rootLogger = logging.getLogger()
    rootLogger = logging.getLogger("")
    rootLogger.setLevel(fileLogLevel)
    fileHandler = logging.FileHandler(
        filename=logFilename,
        mode='w',
        encoding="utf-8")
    fileHandler.setLevel(fileLogLevel)
    # fileFormatter = logging.Formatter(
    #     fmt=fileLogFormat,
    #     datefmt=fileLogDateFormat
    # )
    fileFormatter = LogFormatter(fmt=fileLogFormat, datefmt=fileLogDateFormat)
    fileHandler.setFormatter(fileFormatter)
    rootLogger.addHandler(fileHandler)

    if enableConsole :
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(consoleLogLevel)
        # set a format which is simpler for console use
        # formatter = logging.Formatter(
        #     fmt=consoleLogFormat,
        #     datefmt=consoleLogDateFormat)
        consoleFormatter = LogFormatter(fmt=consoleLogFormat, datefmt=consoleLogDateFormat)
        # tell the handler to use this format
        console.setFormatter(consoleFormatter)
        rootLogger.addHandler(console)

def logSingleLine(curNum, itemStr, totalNum=0, indicatorChar="-", indicatorLength=10):
    """Log output info for single line

    Args:
        curNum (int): current number
        itemStr (str): current item string
        totalNum (int): total number. Default is 0
        indicatorChar (str): the indicator char. Default is '-'. Other common ones: '=', '*'
        indicatorLength (str): length of indicator char. Default is 10
    Returns:
    Raises:
    Examples:
        eg: 
    """
    curProgressStr = ""
    if totalNum > 0:
        curPercent = curNum / totalNum
        curPercentInt = (int)(curPercent * 100)
        curProgressStr = "%2d%% %s/%s" % (curPercentInt, curNum, totalNum)
    else:
        curProgressStr = "%s" % (curNum)
    
    indicatorStr = indicatorChar * indicatorLength

    logging.info("%s [%s] %s %s", indicatorStr, curProgressStr, itemStr, indicatorStr)

    return

################################################################################
# Test
################################################################################

def testLogging():
    loggingInit("testLogging.log")
    # loggingInit()

    logging.debug("log debug")
    logging.info("log info")
    logging.warning("log waring")
    logging.error("log error")
    logging.fatal("log fatal")


if __name__ == '__main__':
    # print("[crifanLib-%s] %s" % (__file__, __version__))
    print("[crifanLib-%s] %s" % (CURRENT_LIB_FILENAME, __version__))

    testLogging()
