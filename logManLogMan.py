# -*- coding: utf-8 -*-
"""
  :Purpose: logging service for logManPy system.
  :author: Lei.Wang,
  :copyright: Orientsoft Co., Ltd.
  :comments:
"""

import logging

logName = 'logManPyLogMan'
logger = logging.getLogger(logName)
logger.setLevel(logging.INFO)

logPath = './logManPy.log'
logFH = logging.FileHandler(logPath)