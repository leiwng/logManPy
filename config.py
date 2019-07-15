# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
  :Purpose: config file for logManPy system.
  :author: Lei.Wang,
  :copyright: Orientsoft Co., Ltd.
"""


from bson.objectid import ObjectId
from datetime import datetime


logJobRunningSetting = {
  # How many backup job can be run
  'jobThreadCntLmt': 5,

  # how many jobs in running
  'jobRunningCnt': 0,
}


logJobSum = {

  # the date of logs which need backup
  'logDate4BackupInStr': '',

  # all job generated
  'allJobGenerated': False,

  # all today's job done
  'allJobDone': False,

  #statistics
  'statInfo': {
    'jobTotalCnt': 0,
    'jobInReadyCnt': 0,
    'jobInStartedCnt': 0,
    'jobInFinishCnt': 0,
    'jobInErrorCnt': 0,
  }
}

# TODO: store into MongoDB, and Can be configured by user
logManPy = {
  # host info
  'hostIP': '192.168.0.48',
  'userName': 'voyager',
  'passWord': 'welcome1',

  # logManPy System Info
  'backupRootDir': '/home/voyager/leiw', # Log Backup Root Dir
  'backupDirName': 'logPond', # Dir name for backup log file storage

  # system const
  'wait4ZipDir': 'wait4zip',

  # file name for MD5Sum check file
  'fileNameOfFileProperty': 'ort_file_property.txt',

  # log zip file name
  'logZipFileName': 'logBackup.zip',

  # zip file common password if the password is not specified for single zip file
  'logSaveCommonZipPassword': 'welcome1'
}

# system info
# TODO: store into MongoDB, and Can be configured by user
sysInfoColl = {
  'sysName': '核心系统', #系统中文名称
  'sysAbbr': 'core', # 系统名称英文缩写
  'sysOS': 'AIX', # AIX, Linux (RHEL, CentOS)
}

# logInfo
# TODO: store into MongoDB, and Can be configured by user
logInfoColl = {
  'state': 'maintain', # 当前logInfo的状态： 'maintain' 'available'
  'sysID': 'system object id',
  'certID': 'ObjectID of cert',
  'logName': '核心tploader应用日志', # 日志中文名称
  'logAbbr': 'core_tploader_app_log', # 日志名称英文缩写 *
  'hostName': '核心系统tploader主机01', # 主机中文名称
  'logDir': '/home/voyager/leiw/logManPy/logTest/dailyBackupYesterdaysDateNamedLogZipFile_Bumble', # 日志目录 *
  'logFileFilterStr': 'lz-bank3-2019-06-02-*.log.gz', # 日志文件通配符字串 *
  'logFormatType': 'text', # 日志格式类型：text， binary *
  'logDescOfProduceMethod': '在日志归档目录下，日志文件每天进行归档，归档后的文件以年月日命名。',  # 日志文件生成方式描述（中文）
  'logTypeOfProduceMethod': 'dailyBackupNamedByDate', # 日志文件生成方式编码 *
  'logSaveZipPassword': 'welcome1', # log zip file password
}

# cert info collection
# TODO: store into MongoDB, and Can be configured by user
certColl = {
  "host" : "127.0.0.1",
  "port" : "22",
  "user" : "voyager",
  "pass" : "aaa123",
}

# TODO: store into MongoDB, and Can be configured by user
job1 = {

  # logs completed in which day to backup
  # The Rule is to backup yesterday's logs in today
  'logDate4Backup': '',
  'logDate4BackupInStr': '2019-07-12',

  # system info
  'sysInfo': {
    'sysName': '核心系统', #系统中文名称
    'sysAbbr': 'core', # 系统名称英文缩写
    'sysOS': 'AIX', # AIX, Linux (RHEL, CentOS)
  },

  # logInfo
  'logInfo': {
    'state': 'maintain', # 当前logInfo的状态： 'maintain' 'available'
    'sysID': 'system object id',
    'logName': '核心tploader应用日志', # 日志中文名称
    'logAbbr': 'core_tploader_app_log', # 日志名称英文缩写 *
    'hostName': '核心系统tploader主机01', # 主机中文名称

    'cert': {
      "host" : "127.0.0.1",
      "port" : "22",
      "user" : "voyager",
      "pass" : "aaa123",
    },

    'logDir': '/home/voyager/leiw/logManPy/logTest/dailyBackupYesterdaysDateNamedLogZipFile_Bumble', # 日志目录 *
    'logFileFilterStr': 'lz-bank3-2019-06-02-*.log.gz', # 日志文件通配符字串 *
    'logFormatType': 'text', # 日志格式类型：text， binary *
    'logDescOfProduceMethod': '在日志归档目录下，日志文件每天进行归档，归档后的文件以年月日命名。',  # 日志文件生成方式描述（中文）
    'logTypeOfProduceMethod': 'dailyBackupNamedByDate', # 日志文件生成方式编码 *
    'logSaveZipPassword': 'welcome1', # log zip file password
  },

  # logBackupSaveInfo
  'logBackupSaveInfo': {
    'logSaveType': 'normal', # 日志备份后，存储方式编码，预留，现在还不明确*
    # 日志备份路径  *
    # backupRootDir + backupDirName + abbr + YYYY + MM + DD + hostIP + logAbbr
    'logSaveBaseDir': '/home/voyager/leiw/logPond/core/2019/06/05',
    # 'latestBackupFinishDate': datetime.today() + datetime.timedelta(days=-1), # 最近备份完成时间 *
  },

  # job status
  'jobStatus': {
    # job date
    'createTime': None,
    'startTime': None,
    'finishTime': None,
    'errorTime': None,

    # job status
    'state': 'started', # 'ready', 'started', 'finish', 'error'

    # Error Info
    'errors': [
      {
        'errCode': '',
        'errDesc': '',
        'errFileInfo': '',
      }
    ],

    # file info in backup operation
    # info of files which need backup
    # {
    #   'name': None,
    #   'md5sum': None
    # }
    'srcFileInfoArray': [],
  },
}

# Basic Config
conalogMongo = {
  'host': '192.168.0.149',
  'port': 27017,
  'user': '',
  'password': '',
  'dbName': 'conalog',
  'collectorCollName': 'collector',
  'certCollName': 'cert',
}

# Basic Config
logManPyMongo = {
  'host': '192.168.0.149',
  'port': 27017,
  'user': '',
  'password': '',
  'dbName': 'logManPy',
  'sysInfoCollName': 'sysInfo',
  'logInfoCollName': 'logInfo',
  'logJobInfoCollName': 'logJobInfo',
  'certCollName': 'cert',
  'logJobSumCollName': 'logJobSum',
  'logJobRunningSettingCollName': 'logJobRunningSetting',
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