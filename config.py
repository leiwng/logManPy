# -*- coding: utf-8 -*-

conalogMongo = {
  'host': '192.168.0.148',
  'port': 27017,
  'user': '',
  'password': '',
  'dbName': 'conalog',
  'collectorCollName': 'collector',
  'certCollName': 'cert',
}

logmanpyMongo = {
  'host': '192.168.0.48',
  'port': 27017,
  'user': '',
  'password': '',
  'dbName': 'logmanpy',
  'sysInfoCollName': 'sysinfo',
  'logInfoCollName': 'loginfo',
  'logSaveInfoCollName': 'logsaveinfo',
  'logJobInfoCollName': 'logjobinfo'
}

collectorSample1 = {
	"_id" : ObjectId("5cc53a90443fdce17ca1867f"),
	"name" : "mbank_app",
	"host" : "5cc53a0d443fdce17ca1867e",
	"cmd" : "tail -F ",
	"type" : "LongScript",
	"param" : "/AIOpsDemo/AIOpsDemo/SimOutput.log",
	"encoding" : "UTF-8",
	"channel" : "Redis PubSub",
	"desc" : "mbank_app",
	"category" : "passive",
	"ts" : 1556430846132
}

collectorSample2 = {
  "_id" : ObjectId("5d1b20feaf08338627dd184c"),
  "name" : "netbank_app",
  "host" : "5cc53a0d443fdce17ca1867e",
  "cmd" : "",
  "type" : "FileTail",
  "param" : "/home/voyager/leiw/netbank_app.log",
  "encoding" : "UTF-8",
  "channel" : "Redis PubSub",
  "desc" : "netbak_app",
  "category" : "passive",
  "ts" : 1562059006922
}

certSample1 = {
	"_id" : ObjectId("5cc53a0d443fdce17ca1867e"),
	"host" : "127.0.0.1",
	"port" : "22",
	"user" : "voyager",
	"pass" : "aaa123",
	"ts" : "1556429325333"
}

nameSample1 = 'core_oracle_trace_13'
nameSample2 = 'tploader218'
nameSample3 = 'hxdb_load_log_11'