# -*- coding: utf-8 -*-

import pymongo
from bson import ObjectId
import config as cfg
import re
import traceback
import os

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

def gatherLogInfo(collector, dbConalog, cert) :

  # gather info for sysInfo
  sysInfo = {}
  collectorName = collector['name']
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
    print('-= vvv Func: gatherLogInfo Error vvv =-')
    print('Error Desc: cannot parse out system Abbr from collector name')
    print('collectorName: ', collectorName)
    print('traceback.print_exc():', traceback.print_exc())
    print('traceback.format_exc():\n%s' %traceback.format_exc())
    print('-= ^^^ END ^^^ =-')
    return -1

  logInfo = {}
  logInfo['logName'] = collectorName
  logInfo['logAbbr'] = collectorName
  logInfo['hostName'] = collectorName
  logInfo['hostIP'] = cert['host']
  logInfo['sshPort'] = cert['port']
  logInfo['logAccessUser'] = cert['user']
  logInfo['logAccessPassword'] = cert['pass']
  (logInfo['logDir'], logInfo['logFileFilterStr']) = os.path.split(collector['param'])
  logInfo['logFormatType'] = 'text'
  logInfo['logDescOfProduceMethod'] = 'Get from Conalog'
  logInfo['logTypeOfProduceMethod'] = 'getFromConalog'

  # data(sysInfo and logInfo) are ready, now save to db
  logManPyConn = mongoConn(cfg.logManPyMongo)
  tmpDBName = cfg.logManPyMongo['dbName']
  dbLogManPy = logManPyConn[tmpDBName]

  tmpCollName = cfg.logManPyMongo['sysInfoCollName']
  sysInfoColl = dbLogManPy[tmpCollName]

  # print(sysInfo)
  tmpDocID = sysInfoColl.insert_one(sysInfo)
  logInfo['sysID'] = tmpDocID.inserted_id

  tmpCollName = cfg.logManPyMongo['logInfoCollName']
  logInfoColl = dbLogManPy[tmpCollName]
  tmpDocID = logInfoColl.insert_one(logInfo)

  return 0

# gather LogInfo for system and host
def mainProc() :

  conn = mongoConn(cfg.conalogMongo)

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
      certs = certColl.find({'_id': ObjectId(collector['host'])})
      if certs :

        certInfo = {}
        for cert in certs :
          # certInfo['hostIP'] = cert['host']
          # certInfo['port'] = cert['port']
          # certInfo['user'] = cert['user']
          # certInfo['password'] = cert['pass']
          gatherLogInfo(collector, dbConalog, cert)
          break


      else :
        pass

  else :
    pass


if __name__=="__main__" :

  mainProc()