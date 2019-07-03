# -*- coding: utf-8 -*-

import pymongo
import config as cfg
import re
from bson.objectid import ObjectId
import traceback

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

  connStr = 'mongodb://' + user + sepStr1 + pwd + sepStr2 + host + ':' + port + '/'
  conn = pymongo.MongoClient(connStr)

  return conn

def gatherLogInfo(collector, dbConalog, certInfo) :

  # gather info for sysInfo
  sysInfo = {}
  collectorName = collector['name']
  reExp = r'(^[A-Za-z]+)'
  sysAbbr = re.match(reExp, collectorName)
  if sysAbbr :

    sysInfo['sysAbbr'] = sysAbbr
    sysInfo['sysName'] = sysAbbr

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

  logoInfo = {}
  logoInfo['logName'] = collectorName
  logoInfo['logAbbr'] = collectorName
  logoInfo['hostName'] = collectorName
  logoInfo['hostIP'] = certInfo['']

  coll = dbConalog['']

  logoInfo['hostIP'] = collector['']



# gather LogInfo for system and host
def mainProc() :

  conn = mongoConn(cfg.conalogMongo)

  dbName = cfg.conalogMongo['dbName']
  dbConalog = conn[dbName]

  collName = cfg.conalogMongo['collectorCollName']
  collectorColl = dbConalog[collName]

  collName = cfg.conalogMongo['certCollName']
  certColl = dbConalog[collName]

  collectors = collectorColl.find({'category':'passive'})
  if collectors :

    for collector in collectors :

      # get find cert coll to get host, user, password
      certs = certColl.find({'_id': ObjectId(collector['host'])})
      if certs :

        certInfo = {}
        for cert in certs :
          certInfo['hostIP'] = cert['host']
          certInfo['port'] = cert['port']
          certInfo['user'] = cert['user']
          certInfo['password'] = cert['pass']
          break

        gatherLogInfo(collector, dbConalog, certInfo)

      else :
        pass

  else :
    pass

