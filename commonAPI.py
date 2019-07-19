# -*- coding: utf-8 -*-
"""
  :Purpose: common API.
  :author: Lei.Wang,
  :copyright: Orientsoft Co., Ltd.
"""


import pymongo
from bson import ObjectId
from datetime import datetime, timedelta

from commonLogging import Log
log = Log(__name__).getLogger()


# connect to mongodb
def mongoConn(connCfg) :

  user = connCfg['user']
  pwd = connCfg['password']
  host = connCfg['host']
  port = connCfg['port']

  if user :
    sepStr1 = ':'
    sepStr2 = '@'
  else :
    sepStr1 = ''
    sepStr2 = ''

  connStr = 'mongodb://' + user + sepStr1 + pwd + sepStr2 + host + ':' + str(port) + '/'
  conn = pymongo.MongoClient(connStr)

  return conn


# get which day's log need backup
def getDate4Backup() :

  return datetime.now() - timedelta(days=1)


# get date string (YYYY-MM-DD) of the day which log need backup
def getDate4BackupStr() :

  date4Bkp = getDate4Backup()
  date4BkpStr = str(date4Bkp.year) + '-' + str(date4Bkp.month).zfill(2) + '-' + str(date4Bkp.day).zfill(2)

  return date4BkpStr