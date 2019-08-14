#! python3
# -*- coding: utf-8 -*-
"""
  :Purpose: Get log config info from Conalog Mongo DB to save effort on log configuration of current host.
  :author: Lei.Wang,
  :copyright: Orientsoft Co., Ltd.
  :comments: ErrorCode -2xxx
"""


import pymongo
from bson import ObjectId
import re
import traceback
import os

import config as cfg
import commonAPI as cAPI

from commonLogging import Log
log = Log(__name__).getLogger()

# gather log info from Conalog Mongo DB
def gatherLogInfo(collector, dbConalog, cert) :

  # gather info for sysInfo
  sysInfo = {}
  collectorName = collector['name']

  # 系统名称的缩写取自Collector Name的开始的连续英文字母序列
  reExp = r'(^[A-Za-z]+)'
  sysAbbr = re.match(reExp, collectorName)
  if sysAbbr :

    sysInfo['sysAbbr'] = sysAbbr.group()
    sysInfo['sysName'] = sysAbbr.group()

    if collector['type'] == 'FileTail' or collector['cmd'].replace(' ', '') == 'tail-F' :
      sysInfo['sysOS'] = 'Linux'
    else :
      sysInfo['sysOS'] = 'AIX'

  else :
    log.error('[ErrorDesc:Cannot parse out system Abbr from collector name, which the name is %s]' % (collectorName))
    return -2011

  logInfo = {}
  logInfo['logName'] = collectorName
  logInfo['logAbbr'] = collectorName
  logInfo['hostName'] = collectorName
  (logInfo['logDir'], logInfo['logFileFilterStr']) = os.path.split(collector['param'])
  logInfo['logFormatType'] = 'text'
  # temporary set to 'getFromConalog' need configuration manually later
  logInfo['logDescOfProduceMethod'] = 'Get from Conalog'
  logInfo['logTypeOfProduceMethod'] = 'getFromConalog'
  # this log info is just created, need update later for above info
  logInfo['state'] = 'maintain'
  logInfo['logSaveZipPassword'] = 'welcome1'

  # data(sysInfo and logInfo) are ready, now save to db
  logManPyConn = cAPI.mongoConn(cfg.logManPyMongo)
  tmpDBName = cfg.logManPyMongo['dbName']
  dbLogManPy = logManPyConn[tmpDBName]

  tmpCollName = cfg.logManPyMongo['sysInfoCollName']
  sysInfoColl = dbLogManPy[tmpCollName]

  # save system info to DB
  tmpDocID = sysInfoColl.insert_one(sysInfo)
  # fill back sysID to Log Info
  logInfo['sysID'] = tmpDocID.inserted_id

  tmpCollName = cfg.logManPyMongo['certCollName']
  certColl = dbLogManPy[tmpCollName]
  # save cert info to DB
  tmpDocID = certColl.insert_one(cert)
  # fill back certID to Log Info
  logInfo['certID'] = tmpDocID.inserted_id

  tmpCollName = cfg.logManPyMongo['logInfoCollName']
  logInfoColl = dbLogManPy[tmpCollName]
  tmpDocID = logInfoColl.insert_one(logInfo)

  logManPyConn.close()

  return 0


# gather LogInfo for system and host
def mainProc() :

  conn = cAPI.mongoConn(cfg.conalogMongo)

  tmpDBName = cfg.conalogMongo['dbName']
  dbConalog = conn[tmpDBName]

  tmpCollName = cfg.conalogMongo['collectorCollName']
  collectorColl = dbConalog[tmpCollName]

  tmpCollName = cfg.conalogMongo['certCollName']
  certColl = dbConalog[tmpCollName]

  collectors = collectorColl.find({'category':'passive'})
  if collectors :

    for collector in collectors :

      # get find cert coll to get host, user, password
      cert = certColl.find_one({'_id': ObjectId(collector['host'])})
      if cert :
        gatherLogInfo(collector, dbConalog, cert)
      else :
        pass

  else :
    log.info('No collector config found in Conalog DB.')

  conn.close()


if __name__=="__main__" :

  mainProc()