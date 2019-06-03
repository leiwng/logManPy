# -*- coding: utf-8 -*-

import datetime

job1 = {
  # ID
  'id': '001',

  # system info
  'sysCName': '核心系统', #系统中文名称
  'sysAbbr': 'core', # 系统名称英文缩写
  'sysOSType': 'AIX', # AIX, RHEL, CentOS

  # logManPy System Info
  'backupRootDir': '/home/voyager/leiw', # Log Backup Root Dir
  'backupDirName': 'logPond', # Dir name for backup log file storage

  # logInfo
  'logCName': '核心toloader应用日志', # 日志中文名称
  'logAbbr': 'core_tploader_app_log', # 日志名称英文缩写 *
  'hostCName': '核心系统tploader主机01', # 主机中文名称
  'hostIP': '192.168.0.20', # 主机IP *
  'logAccessUser': 'voyager', # 用户名 *
  'logAccessPassword': 'welcome1', # 密码 *
  'logPath': '/home/voyager/leiw/logManPy/logTest/dailyBackupYesterdaysDateNamedLogZipFile_Bumble', # 日志目录 *
  'logNameMatchString': 'lz-bank3-2019-06-02-*.log.gz', # 日志文件通配符字串 *
  'logFormatType': 'text', # 日志格式类型：text， binary *
  'logDescOfProduceMethod': '在日志归档目录下，日志文件每天进行归档，归档后的文件以年月日命名。',  # 日志文件生成方式描述（中文）
  'logTypeOfProduceMethod': 'dailyBackupNamedByDate', # 日志文件生成方式编码 *

  # logBackupSaveInfo
  'logSaveType': 'Normal', # 日志备份后，存储方式编码，预留，现在还不明确*
  # 日志备份路径  *
  # backupRootDir + backupDirName + sysAbbr + YYYY + MM + DD + hostIP + logAbbr
  'logSavePath': '/leiw/logManPy/logPond/core/2019/06/02/192.168.0.20/core_tploader_app_log',
  # 'latestBackupFinishDate': datetime.datetime.today() + datetime.timedelta(days=-1), # 最近备份完成时间 *


  # job date
  'createDate': datetime.datetime.now(),
  'startDate': None,
  'finishDate': None,

  # job status
  'isStarted': False,
  'isFinish': False,
  'isError': False,

  # Error Info
  'errorDesc': [{
    'errCode': None,
    'errDesc': None,
    'errFile': None
  }],

  # file info in backup operation
  # info of files which need backup
  'srcFileInfoArray': [{
    'name': None,
    'path': None,
    'size': None,
    'createDate': None,
    'modifyDate': None,
    'md5sum': None
  }],

}