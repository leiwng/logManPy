# -*- coding: utf-8 -*-
"""
  :Purpose: common API.
  :author: Lei.Wang,
  :copyright: Orientsoft Co., Ltd.
"""


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
