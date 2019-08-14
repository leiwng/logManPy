#! python3
# -*- coding: utf-8 -*-
"""
  :Purpose: logging service for logManPy system.
  :author: Lei.Wang,
  :copyright: Orientsoft Co., Ltd.
  :comments:
"""

import logging
from logging.handlers import RotatingFileHandler


class Log(object):

  def __init__(self, logger=None, log_cate='search'):

    # logger
    self.logger = logging.getLogger(logger)
    self.logger.setLevel(logging.INFO)

    # file handler
    logPath = './logManPy.log'
    maxSize = 1024 * 1024 * 100
    fHandler = RotatingFileHandler(logPath, 'a', maxBytes=maxSize, backupCount=50)
    fHandler.setLevel(logging.INFO)

    # stream handler output to console
    cHandler = logging.StreamHandler()
    cHandler.setLevel(logging.INFO)

    # Formatter
    fmt = '[%(asctime)s] [%(levelname)s] [%(filename)s-%(funcName)s-%(lineno)d] [%(message)s]'
    # dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(fmt)

    # set Formatter
    fHandler.setFormatter(formatter)
    cHandler.setFormatter(formatter)

    # add handler to logger
    self.logger.addHandler(fHandler)
    self.logger.addHandler(cHandler)


  def getLogger(self):

    return self.logger
