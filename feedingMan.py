# -*- coding: utf-8 -*-
"""
  :Purpose: Give job to Bumble Bee to complete log backup job.
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
import beeBumble as bee
import logManLog as log

from commonLogging import Log
log = Log(__name__).getLogger()


def mainProc() :

  homeSys = cfg.logManPy



  conn = cAPI.mongoConn(cfg.logManPyMongo)
  tmpDBName = cfg.logManPyMongo['dbName']
  logManPyDB = conn[tmpDBName]

  tmpCollName = cfg.logManPyMongo['logJobSumCollName']
  logJobSumColl = logManPyDB[tmpCollName]

  tmpCollName = cfg.logManPyMongo['logJobInfoCollName']
  logJobColl = logManPyDB[tmpCollName]

  tmpCollName = cfg.logManPyMongo['logJobRunningSettingCollName']
  logJobRunningSettingColl = logManPyDB[tmpCollName]

  date4Bkp = cAPI.getDate4Backup()
  date4BkpStr = cAPI.getDate4BackupStr()

  # check whether backup job already generated
  logJobSum = logJobSumColl.find_one({'logDate4BackupInStr': date4BkpStr,
                                      'allJobGenerated': True})

  if logJobSum :
    # log backup jobs generated already
    jobList = logJobColl.find({'logDate4BackupInStr': date4BkpStr,
                              'jobStatus.state': 'ready'})

    if jobList :
      # have job ready for processing
      for job in jobList :

        jobRunningSetting = logJobRunningSettingColl.find_one()
        if jobRunningSetting :

          # has running setting which used to check job running limit
          if jobRunningSetting['jobRunningCnt'] < jobRunningSetting['jobThreadCntLmt'] :

            # running job thread below limit, which can start new job
            # TODO: later chg to subprocess or use PM2 to start
            result = bee.main_proc(job, homeSys)

            if result == 0 :
              # start job successfully
              # update Running Setting of log job in MongoDB

              # update log Job summary in MongoDB

            else :
              # error on starting new job, continue to start next job
              pass

          else :

            # enough running jobs, no new job
            pass

        else :

          # Error: no job Running Setting found in mongoDB
          pass

    else :

      # no job ready for processing
      pass


  else :
    # log backup job has not been generated.
    pass


if __name__=="__main__" :

  mainProc()