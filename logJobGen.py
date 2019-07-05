# -*- coding: utf-8 -*-
"""
  :Purpose: Generate log backup job periodically.
  :author: Lei.Wang,
  :copyright: Orientsoft Co., Ltd.
"""

import pymongo
from bson import ObjectId
import re
import traceback
import os
from datetime import datetime, timedelta

import config as cfg
import commonAPI as cAPI


# visite all doc of LogInfo collection to generate job
def mainProc(homeSys) :

  conn = cAPI.mongoConn(cfg.logManPyMongo)
  tmpDBName = cfg.logManPyMongo['dbName']
  logManPyDB = conn[tmpDBName]

  tmpCollName = cfg.logManPyMongo['sysInfoCollName']
  sysInfoColl = logManPyDB[tmpCollName]

  tmpCollName = cfg.logManPyMongo['logInfoCollName']
  logInfoColl = logManPyDB[tmpCollName]

  tmpCollName = cfg.logManPyMongo['logJobInfoCollName']
  logJobColl = logManPyDB[tmpCollName]

  tmpCollName = cfg.logManPyMongo['certCollName']
  certColl = logManPyDB[tmpCollName]

  # get all available logInfo, and check one by one  to generate backup job
  logInfoList = logInfoColl.find({'state':'available'})
  if logInfoList :

    logJob = {}
    sysInfo = {}
    logInfo = {}
    certInfo = {}
    # go through all the logInfo
    for logInfo in logInfoList :

      #get SysInfo
      sysInfo = sysInfoColl.find_one({'_id': ObjectId(logInfo['sysID'])})

      #get certInfo
      certInfo = certColl.find_one({'_id': ObjectId(logInfo['certID'])})

      # compose log backup job
      logJob['sysInfo'] = sysInfo
      logJob['logInfo'] = logInfo
      logJob['logInfo']['cert'] = certInfo

      # which day's log will backup, today backup yesterday's logs
      date4Bkp = datetime.now() - timedelta(days=1)
      logJob['logDate4Backup'] = date4Bkp

      # log backup save info
      logJob['logBackupSaveInfo']['logSaveType'] = 'normal'

      # 日志备份路径  *
      # backupRootDir + backupDirName + abbr + YYYY + MM + DD + hostIP + logAbbr
      logJob['logBackupSaveInfo']['logSaveBaseDir'] = homeSys['backupRootDir'] + os.sep + homeSys['backupDirName'] + os.sep + sysInfo['sysAbbr'] + os.sep + str(date4Bkp.year) + os.sep + str(date4Bkp.month).zfill(2) + os.sep + str(date4Bkp.day).zfill(2) + os.sep + certInfo['host'] + os.sep + logInfo['logAbbr']

      # job status
      logJob['jobStatus']['createTime'] = datetime.now()
      logJob['jobStatus']['state'] = 'ready'

      # save job to DB
      tmpDocId = logJobColl.insert_one(logJob)


  else :
    pass

  return 0


if __name__=="__main__" :

  homeSys = cfg.logManPy

  mainProc(homeSys)