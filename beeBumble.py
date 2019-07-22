# -*- coding: utf-8 -*-
"""
  :Purpose: get log backup job and complete the job.
  :author: Lei.Wang,
  :copyright: Orientsoft Co., Ltd.
  :comments: ErrorCode -1xxx
"""


import paramiko
import sys
import os
import traceback
import re
import subprocess
from datetime import datetime
import pymongo
from bson import ObjectId

import config as cfg
import commonAPI as cAPI

from commonLogging import Log
log = Log(__name__).getLogger()


# exec shell command through ssh
def ssh_exec(hostIP, port, userName, password, cmd):

  rtnCode = 0

  try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hostIP, port=port, username=userName, password=password)
    ## cmd exec
    stdin, stdout, stderr = client.exec_command(cmd)
    outList = stdout.readlines()
    errList = stderr.readlines()

  except Exception as e:
    log.error('[ErrorDesc:Exception when exec ssh command] [hostIP:%s] [Cmd:%s] [str(e):%s] [repr(e):%s] [e.message:%s]' % (hostIP, cmd, str(e), repr(e), e.message))
    client.close()
    rtnCode = -1001
    return rtnCode, [], []

  client.close()

  return rtnCode, outList, errList


# shell command compose for getting md5sum
def cmd_md5sum(sysOS, logDir, logFilterStr):

  # different MD5 sum command on AIX and other OS
  if sysOS == 'AIX' :
    chkSumCmd = ' csum -h MD5 '
  else :
    # RHEL, CentOS, SuSE
    chkSumCmd = ' md5sum '

  ## 'logFileFilterStr' 一定要是最后把年月日解析出来后的，带通配符的文件名
  cmd = 'find ' + logDir + ' -name ' + '"' + logFilterStr + '"' + \
    ' -type f -maxdepth 1 -exec ' + chkSumCmd + ' {} \;'

  return cmd


# parse datetime info from result lines by exec stat command in shell, for output style refer to Sample.txt
def get_date_from_line(line) :

  reExpTime = r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}.\d{9}\s[+-]\d{4})'

  matched = re.search(reExpTime, line)
  if matched :
    # line contain datetime string
    lineDate = datetime.strptime(matched.group()[:26], '%Y-%m-%d %H:%M:%S.%f')
  else :
    lineDate = None

  return lineDate


# get remote file properties
def get_remote_file_size_date_Info(hostIP, port, userName, password, remoteDir, fileNameFilterStr) :

  fileBirthDate = None
  fileChgDate = None
  fileModifyDate = None
  fileAccessDate = None
  fileSize = 0
  rtnCode = 0
  fileInfoList = []
  fileInfo = {}

  cmd = 'cd ' + remoteDir + ';' + 'stat ' + fileNameFilterStr
  rltCode, outList, errList = ssh_exec(hostIP, port, userName, password, cmd)

  # command exec met exception
  if not rltCode:
    rtnCode = -1011
    log.error('[ErrorDesc:Cause func ssh_exec rltCode is not equal zero]')
    return rtnCode, []

  # command exec report error
  if len(errList) != 0:
    rtnCode = -1012
    log.error('[ErrorDesc:shell command - stat execute error] [hostIP:%s] [Cmd:%s] [ExecErrorList:%s]' % (hostIP, cmd, '|'.join(errList)))
    return rtnCode, []

  # command exec successfully, but output is empty - no file found in the dir
  if len(outList) == 0:
    rtnCode = -1013
    log.error('[ErrorDesc:stat command output is empty] [hostIP:%s] [Cmd:%s]' % (hostIP, cmd))
    return rtnCode, []

  # deal with the line one by one to get file Info
  for line in outList :

    if re.search(r'(File: )', line) :
      #find the start of file Info block
      fileInfo['name'] = line.strip()[ len('File: ') : ]

    if re.search(r'(Size: )', line) :
      #find size:
      shortLine = line.strip()
      shortLine = shortLine[ : shortLine.find('Blocks: ') ]
      fileInfo['size'] = int(shortLine.strip()[ len('Size: ') : ])

    if line.find('Access: (') >= 0 :
      continue

    if re.search(r'(Access: )', line) :
      # file aTime
      fileInfo['aTime'] = get_date_from_line(line)

    if re.search(r'(Modify: )', line) :
      # file mTime
      fileInfo['mTime'] = get_date_from_line(line)

    if re.search(r'(Change: )', line) :
      # file aTime
      fileInfo['cTime'] = get_date_from_line(line)

    if re.search(r'(Birth: )', line) :
      # file mTime
      fileInfo['bTime'] = get_date_from_line(line)
      fileInfoList.append(fileInfo)

  return rtnCode, fileInfoList


# Using sftp to transfer log files from remote to local
# fileInfolist: [{name, size, aTime, mTime, cTime, bTime, dir, path, md5sum}, ...]
def sftp_file_download(hostIP, port, user, password, remoteDir, localTmpDir, remoteFileInfoList) :

  rtnCode = 0

  try :
    t = paramiko.Transport(sock = (hostIP, port))
    t.connect(username=user, password=password)
    sftp = paramiko.SFTPClient.from_transport(t)

    if not os.path.exists(localTmpDir) :
      os.makedirs(localTmpDir)
    else :
      pass

    localFileList = os.listdir(localTmpDir)

    for rFile in remoteFileInfoList :
      # start to transfer files one by one

      if rFile['name'] in localFileList :

        # the file for transfer already in local dir
        localRxFilePath = localTmpDir + os.path.sep + rFile['name']
        localRxFileSize = os.path.getsize(localRxFilePath)

        if localRxFileSize < rFile['size'] :
          # file transfer halted before, now resume
          localRxFile = open(localRxFilePath, 'a')

          remoteTxFilePath = rFile['path']
          remoteTxFile = sftp.open(remoteTxFilePath, 'r')
          remoteTxFile.seek(localRxFileSize)

          tmpBuffer = remoteTxFile.read(1024 * 1024)
          while tmpBuffer :
            localRxFile.write(tmpBuffer)
            tmpBuffer = remoteTxFile.read(1024 * 1024)

          remoteTxFile.close()
          localRxFile.flush()
          localRxFile.close()
        else :
          pass

      else :
        # the file is new, not in local Rx folder
        localRxFilePath = localTmpDir + os.path.sep + rFile['name']
        localRxFile = open(localRxFilePath, 'w')

        remoteTxFilePath = rFile['path']
        remoteTxFile = sftp.open(remoteTxFilePath, 'r')

        tmpBuffer = remoteTxFile.read(1024 * 1024)
        while tmpBuffer :
          localRxFile.write(tmpBuffer)
          tmpBuffer = remoteTxFile.read(1024 * 1024)

        remoteTxFile.close()
        localRxFile.flush()
        localRxFile.close()

    sftp.close()
    t.close()

  except Exception as e :
    log.error('[ErrorDesc:Exception when create local dir for storing sftp files] [hostIP:%s] [localDownloadWait4ZipDir:%s] [str(e):%s] [repr(e):%s] [e.message:%s]' % (hostIP, localTmpDir, str(e), repr(e), e.message))
    sftp.close()
    t.close()
    rtnCode = -1031
    return rtnCode

  return rtnCode


# get md5sum of remote files
def get_remote_files_md5sum(sysOS, logDir, logNameFilterStr, hostIP, port, user, pwd) :


  rtnCode = 0

  # get a file Info dict for {fileName, fileDir, filePath, md5sum}
  cmd = cmd_md5sum(sysOS, logDir, logNameFilterStr)

  # exec command to get md5sum
  rltCode, outList, errList = ssh_exec(hostIP, port, user, pwd, cmd)

  # command exec met exception
  if not rltCode :
    rtnCode = -1021
    log.error('[ErrorDesc:Cause func ssh_exec rltCode is not equal zero]')
    return rtnCode, []

  # command exec report error
  if len(errList) != 0 :
    rtnCode = -1022
    log.error('[ErrorDesc:shell command - stat execute error] [hostIP:%s] [Cmd:%s] [ExecErrorList:%s]' % (hostIP, cmd, '|'.join(errList)))
    return rtnCode, []

  # command exec successfully, but output is empty - no file found in the dir
  if len(outList) == 0:
    rtnCode = -1023
    log.error('[ErrorDesc:stat command output is empty] [hostIP:%s] [Cmd:%s]' % (hostIP, cmd))
    return rtnCode, []

  fileMD5SumList = []
  # cmd exec have output
  for line in outList :
    split = re.split(r'[;,\s]\s*', line)
    fileFullPath = split[1]
    fileMD5Sum = split[0]
    fileName = os.path.basename(fileFullPath)
    fileDir = os.path.dirname(fileFullPath)
    fileMD5SumList.append(
      {
        'name': fileName,
        'dir' : fileDir,
        'path': fileFullPath,
        'md5sum': fileMD5Sum,
      }
    )

  return rtnCode, fileMD5SumList


# get downloaded local file md5sum
def get_local_files_md5sum(wait4ZipDir, fileNameFilterStr) :

  rtnCode = 0

  # exec md5sum command
  cmd = 'md5sum ' + wait4ZipDir + os.path.sep + fileNameFilterStr
  result = os.popen(cmd, 'r')
  resultList = result.readlines()

  # command exec output is empty
  if len(resultList) == 0 :
    rtnCode = -1041
    log.error('[ErrorDesc:exec md5sum for local dir got empty output, looks no file in local dir] [wait4ZipDir:%s] [fileNameFilterStr:%s] [Cmd:%s]' % (wait4ZipDir, fileNameFilterStr, cmd))
    return rtnCode, []

  fileMD5SumList = []
  for line in resultList :
    split = re.split(r'[;,\s]\s*', line)
    fileFullPath = split[1]
    fileMD5Sum = split[0]
    fileName = os.path.basename(fileFullPath)
    fileDir = os.path.dirname(fileFullPath)
    fileMD5SumList.append(
      {
        'name': fileName,
        'dir' : fileDir,
        'path': fileFullPath,
        'md5sum': fileMD5Sum,
      }
    )

  return rtnCode, fileMD5SumList


# save file property to local folder for job verification
def write_dict_array_to_local_file(dictArray, dictArrayName, fileFullPath) :

  # open file
  if os.path.exists(fileFullPath) :
    f = open(fileFullPath, 'a')
  else :
    localDir = os.path.dirname(fileFullPath)
    if not os.path.exists(localDir) :
      os.makedirs(localDir)
    else :
      pass
    f = open(fileFullPath, 'w')

  # write dict to file line by line
  f.writelines(os.linesep)
  f.writelines(' ###  ' + str(datetime.now()) + '  ###')
  f.writelines(' >>>  ' + dictArrayName + '  <<<')
  lineCnt = 1
  for aDict in dictArray :
    f.write(str(lineCnt) + ' : ')
    f.writelines(str(aDict))
  f.writelines(' ^^^  END  ^^^ ')

  # close file
  f.close


# zip downloaded local log file
def zip_local_file(localLogDir, zipPassword, zipFileName, wait4ZipDir) :

  # use os command to zip local file
  cmd = 'cd ' + localLogDir + ';' + 'zip -P ' + zipPassword + ' -r -m ' + zipFileName + ' ' + wait4ZipDir

  rtCode, cmdOutput = subprocess.getstatusoutput(cmd)

  if rtCode != 0 :
    # command exec fail
    print('-= vvv Func: zip_local_file Error vvv =-')
    print('Error Desc: zip local log file failure')
    print('cmd: ', cmd)
    print('Error Msg: ', cmdOutput)
    print('traceback.print_exc():', traceback.print_exc())
    print('traceback.format_exc():\n%s' %traceback.format_exc())
    print('-= ^^^ END ^^^ =-')
    sys.exit(100)
  else :
    pass


def updateJobStatus(job, jobColl, state) :

  # update job status to DB
  job['jobStatus']['startTime'] = datetime.now()
  job['jobStatus']['state'] = state
  condition = {'_id':ObjectId(job['_id'])}
  result = jobColl.update_one(condition, {'$set': job})

  return result

def updateJobSum(logDate, jobSumColl, state) :

  # update logJobSum in DB
  condition = {'logDate4BackupInStr': logDate}
  jobSum = jobSumColl.find_one(condition)
  result = None

  if jobSum :
    if state == 'started' :

      tmpCnt = jobSum['statInfo']['jobInReadyCnt']
      jobSum['statInfo']['jobInReadyCnt'] = tmpCnt - 1

      tmpCnt = jobSum['statInfo']['jobInStartedCnt']
      jobSum['statInfo']['jobInStartedCnt'] = tmpCnt + 1

    elif state == 'finish' :

      tmpCnt = jobSum['statInfo']['jobInFinishCnt']
      jobSum['statInfo']['jobInFinishCnt'] = tmpCnt + 1

    elif state == 'error' :

      tmpCnt = jobSum['statInfo']['jobInErrorCnt']
      jobSum['statInfo']['jobInErrorCnt'] = tmpCnt + 1

    result = jobSumColl.update_one(condition, {'$set': jobSum})
    # TODO: check result, if success, result.matched_count=1, result.modified_count=1

  else :
    # no logJobSum found of the day
    # TODO: report error, and exit.
    pass

  return result


def updateJobRunningSetting(jobRunningSettingColl, runningNum) :

  # update logJobRunning Setting in DB
  jobRunningSetting = jobRunningSettingColl.find_one()
  result = None
  if jobRunningSetting :
    tmpCnt = jobRunningSetting['jobRunningCnt']
    jobRunningSetting['jobRunningCnt'] = tmpCnt + runningNum
    result = jobRunningSettingColl.update_one({}, {'$set': jobRunningSetting})
    # TODO: check result, if success, result.matched_count=1, result.modified_count=1
  else:
    # no logJobRunningSetting found -> error
    # TODO: report error, and exit
    pass

  return result


# main process function for backup log from one single backup job
def main_proc(job, homeSys, jobColl, jobSumColl, jobRunningSettingColl) :

  # update job status to DB
  result = updateJobStatus(job, jobColl, 'started')
  # TODO: check result, if success, result.matched_count=1, result.modified_count=1

  # update logJobSum in DB
  result = updateJobSum(job['logDate4BackupInStr'], jobSumColl, 'started')
  # TODO: check result, if success, result.matched_count=1, result.modified_count=1

  # update logJobRunning Setting in DB
  result = updateJobRunningSetting(jobRunningSettingColl, 1)
  # TODO: check result, if success, result.matched_count=1, result.modified_count=1

  sysOS = job['sysInfo']['sysOS']
  logDir = job['logInfo']['logDir']
  logNameFilterStr = job['logInfo']['logFileFilterStr']
  hostIP = job['logInfo']['cert']['host']
  port = job['logInfo']['cert']['port']
  user = job['logInfo']['cert']['user']
  pwd = job['logInfo']['cert']['pass']
  logLocalDir = job['logBackupSaveInfo']['logSaveBaseDir']
  logLocalTmpDir = logLocalDir + os.path.sep + homeSys['wait4ZipDir']

  # get md5sum Info of files
  # [{name, dir, path, md5sum}, ... ]
  rltCode, remoteFileMD5SumList = get_remote_files_md5sum(sysOS, logDir, logNameFilterStr, hostIP, port, user, pwd)
  if not rltCode :
    log.error('[ErrorDesc:get_remote_files_md5sum func met error]')
    sys.exit(rltCode)

  # [{name, size, aTime, mTime, cTime, bTime}, ...]
  rltCode, remoteFileInfoList = get_remote_file_size_date_Info(hostIP, port, user, pwd, logDir, logNameFilterStr)
  if not rltCode :
    log.error('[ErrorDesc:get_remote_file_size_date_Info func met error]')
    sys.exit(rltCode)

  # [{name, size, aTime, mTime, cTime, bTime, dir, path, md5sum}, ...]
  remoteMergedFileInfoList = []
  # merge two list according to key = name
  for fileInfo in remoteFileInfoList :
    for fileMD5Sum in remoteFileMD5SumList :
      if fileInfo['name'] == fileMD5Sum['name'] :
        remoteMergedFileInfoList.append({**fileInfo, **fileMD5Sum})
        break

  # log file transfer to local
  rltCode = sftp_file_download(hostIP, port, user, pwd, logDir, logLocalTmpDir, remoteMergedFileInfoList)
  if not rltCode :
    log.error('[ErrorDesc:sftp_file_download func met error]')
    sys.exit(rltCode)

  # check Tx file md5sum
  rltCode, localFileMD5SumList = get_local_files_md5sum(logLocalTmpDir, logNameFilterStr)
  if not rltCode :
    log.error('[ErrorDesc:get_local_files_md5sum func met error]')
    sys.exit(rltCode)

  # save file property to file
  fileNameOfFileProperty = logLocalTmpDir + os.path.sep + homeSys['fileNameOfFileProperty']
  write_dict_array_to_local_file(remoteMergedFileInfoList, 'RemoteFiles', fileNameOfFileProperty)
  write_dict_array_to_local_file(localFileMD5SumList, 'Local Files', fileNameOfFileProperty)

  # check md5sum between remote and local
  for rFileInfo in remoteMergedFileInfoList :
    for lFileInfo in localFileMD5SumList :
      if rFileInfo['name'] == lFileInfo['name'] :
        if rFileInfo['md5sum'] != lFileInfo['md5sum'] :
          log.error('[ErrorDesc:MD5Sum not equal between remote file and downloaded local file] [hostIP:%s] [RemoteFile:%s] [RemoteFileMD5Sum:%s] [LocalFile:%s] [LocalFileMD5Sum:%s]' % (hostIP, rFileInfo['path'], rFileInfo['md5sum'], lFileInfo['path'], lFileInfo['md5sum']))
          sys.exit(-1091)
        else :
          # two md5sum are equal exit current loop for next loop
          pass

        break

  # Zip local files
  logStoreDir = job['logBackupSaveInfo']['logSaveBaseDir']
  zipPassword = job['logInfo']['logSaveZipPassword']
  zipFileName = homeSys['logZipFileName']
  wait4zipDirName = homeSys['wait4ZipDir']
  zip_local_file(logStoreDir, zipPassword, zipFileName, wait4zipDirName)

  # update job status to DB
  result = updateJobStatus(job, jobColl, 'finish')
  # TODO: check result, if success, result.matched_count=1, result.modified_count=1

  # update logJobSum in DB
  result = updateJobSum(job['logDate4BackupInStr'], jobSumColl, 'finish')
  # TODO: check result, if success, result.matched_count=1, result.modified_count=1

  # update logJobRunning Setting in DB
  result = updateJobRunningSetting(jobRunningSettingColl, -1)
  # TODO: check result, if success, result.matched_count=1, result.modified_count=1

  return 0


if __name__=="__main__" :

  rtnCode = 0
  rltCode = 0

  # newJob = cfg.job1
  homeSys = cfg.logManPy

  # contact DB, get new job
  conn = cAPI.mongoConn(cfg.logManPyMongo)
  tmpDBName = cfg.logManPyMongo['dbName']
  logManPyDB = conn[tmpDBName]

  tmpCollName = cfg.logManPyMongo['logJobInfoCollName']
  jobColl = logManPyDB[tmpCollName]

  tmpCollName = cfg.logManPyMongo['logJobSumCollName']
  jobSumColl = logManPyDB[tmpCollName]

  tmpCollName = cfg.logManPyMongo['logJobRunningSettingCollName']
  jobRunningSettingColl = logManPyDB[tmpCollName]

  date4BkpStr = cAPI.getDate4BackupStr()

  newJob = jobColl.find_one({'logDate4BackupInStr': date4BkpStr,
                             'jobStatus.state': 'ready'})

  if newJob :
    rltCode = main_proc(newJob, homeSys, jobColl, jobSumColl, jobRunningSettingColl)
  else :
    # no newJob ready
    log.info('[InfoDesc: no newJob found]')
    pass

  conn.close()
  sys.exit(rltCode)
