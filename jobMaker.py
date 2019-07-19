# -*- coding: utf-8 -*-
"""
  :Purpose: Generate log backup job periodically(usually daily).
  :author: Lei.Wang,
  :copyright: Orientsoft Co., Ltd.
  :comments:
    1) Run daily thru crontab to generate backup job according to logInfo collection.
    2) Critical factor is 'logDate4Backup' and 'jobStatus.state' in job. The 1st factor is to decide which log for which date need to be backup; the 2nd factor is to decide whether this job can work.
        'ready': job is there need to finish
        'started': job is started
        'finish': job is finish
        'error': met error when doing the job
"""

import pymongo
from bson import ObjectId
import re
import traceback
import os
from datetime import datetime, timedelta

import config as cfg
import commonAPI as cAPI

from commonLogging import Log
log = Log(__name__).getLogger()


# visit all doc of LogInfo collection to generate job
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

  tmpCollName = cfg.logManPyMongo['logJobSumCollName']
  jobSumColl = logManPyDB[tmpCollName]

  # which day's log will backup, today backup yesterday's logs
  date4Bkp = cAPI.getDate4Backup()
  date4BkpStr = cAPI.getDate4BackupStr()

  # check whether the backup jobs have been generated
  jobSum = jobSumColl.find_one({'logDate4BackupInStr': date4BkpStr})
  if not jobSum :

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

        # log backup save info
        logJob['logBackupSaveInfo']['logSaveType'] = 'normal'

        # which day's log will backup, today backup yesterday's logs
        logJob['logDate4Backup'] = date4Bkp
        logJob['logDate4BackupInStr'] = date4BkpStr

        # 日志备份路径  *
        # backupRootDir + backupDirName + abbr + YYYY + MM + DD + hostIP + logAbbr
        logJob['logBackupSaveInfo']['logSaveBaseDir'] = homeSys['backupRootDir'] + os.sep + homeSys['backupDirName'] + os.sep + sysInfo['sysAbbr'] + os.sep + str(date4Bkp.year) + os.sep + str(date4Bkp.month).zfill(2) + os.sep + str(date4Bkp.day).zfill(2) + os.sep + certInfo['host'] + os.sep + logInfo['logAbbr'] # TODO: 'os.sep' is surpose logManPy System and target user system are all use Linux, a safe way is to check the 'sysOS' field in sysInfo dict.

        # job status
        logJob['jobStatus']['createTime'] = datetime.now()
        logJob['jobStatus']['state'] = 'ready'

        # save job to DB
        tmpDocId = logJobColl.insert_one(logJob)

      # record summary info to log job
      jobSum = {}
      jobSum['logDate4BackupInStr'] = date4BkpStr
      jobSum['allJobGenerated'] = True
      jobSum['allJobDone'] = False
      itemCnt = logInfoList.count()
      jobSum['statInfo']['jobTotalCnt'] = itemCnt
      jobSum['statInfo']['jobInReadyCnt'] = itemCnt
      jobSum['statInfo']['jobInStartedCnt'] = 0
      jobSum['statInfo']['jobInFinishCnt'] = 0
      jobSum['statInfo']['jobInErrorCnt'] = 0

      # save to DB
      tmpDocId = jobSumColl.insert_one(jobSum)

    else :
      # no available logInfo item for generating job.
      pass

  else :
    # today's backup jobs have already been generated.
    pass

  conn.close()
  return 0


if __name__=="__main__" :

  homeSys = cfg.logManPy

  mainProc(homeSys) # TODO: In production system, the homeSys need from MongoDB not from config file