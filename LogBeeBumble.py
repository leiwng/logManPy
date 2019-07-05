# -*- coding: utf-8 -*-
"""
  :Purpose: get log backup job and complete the job.
  :author: Lei.Wang,
  :copyright: Orientsoft Co., Ltd.
"""


import paramiko
import sys
import os
import traceback
import re
import subprocess
from datetime import datetime
import config as cfg


# exec shell command through ssh
def ssh_exec(hostIP, port, userName, password, cmd):

  try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hostIP, port=port, username=userName, password=password)
    ## cmd exec
    stdin, stdout, stderr = client.exec_command(cmd)
    outList = stdout.readlines()
    errList = stderr.readlines()

  except Exception as e:
    print('-= vvv Func: ssh_exec Exception vvv =-')
    print('Exception Desc: Exception when exec ssh command')
    print('hostIP: ', hostIP)
    print('cmd: ', cmd)
    print('str(Exception):\t', str(Exception))
    print('str(e):\t\t', str(e))
    print('repr(e):\t', repr(e))
    print('e.message:\t', e.message)
    print('traceback.print_exc():', traceback.print_exc())
    print('traceback.format_exc():\n%s' %traceback.format_exc())
    print('-= ^^^ END ^^^ =-')
    client.close()
    sys.exit(1)

  client.close()
  return outList, errList


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


# parse datetime info from result lines by exec stat command in shell, for output sytle refer to Sample.txt
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

  cmd = 'cd ' + remoteDir + ';' + 'stat ' + fileNameFilterStr
  outList, errList = ssh_exec(hostIP, port, userName, password, cmd)

  fileInfoList = []
  fileInfo = {}
  if len(errList) == 0 :
    #no error from command exec
    if len(outList) > 0 :

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

    else :
      print('-= vvv Func: get_file_time_Info Error vvv =-')
      print('Error Desc: stat command output is not excepted')
      print('hostIP: ', hostIP)
      print('cmd: ', cmd)
      print('traceback.print_exc():', traceback.print_exc())
      print('traceback.format_exc():\n%s' %traceback.format_exc())
      print('-= ^^^ END ^^^ =-')
      sys.exit(100)
  else :
    print('-= vvv get_file_time_Info Error vvv =-')
    print('Error Desc: stat command meet error')
    print('hostIP: ', hostIP)
    print('cmd: ', cmd)
    print('Exec Error:', errList)
    print('traceback.print_exc():', traceback.print_exc())
    print('traceback.format_exc():\n%s' %traceback.format_exc())
    print('-= ^^^ END ^^^ =-')
    sys.exit(101)

  return fileInfoList


# Using sftp to transfer log files from remote to local
# fileInfolist: [{name, size, aTime, mTime, cTime, bTime, dir, path, md5sum}, ...]
def sftp_file_download(hostIP, port, user, password, remoteDir, localTmpDir, remoteFileInfoList) :

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
    print('-= vvv Func: sftp_file_download Exception vvv =-')
    print('Exception Desc: Exception when create local dir for storing sftp files')
    print('hostIP: ', hostIP)
    print('localDownloadWait4ZipDir: ', localTmpDir)
    print('str(Exception):\t', str(Exception))
    print('str(e):\t\t', str(e))
    print('repr(e):\t', repr(e))
    print('e.message:\t', e.message)
    print('traceback.print_exc():', traceback.print_exc())
    print('traceback.format_exc():\n%s' %traceback.format_exc())
    print('-= ^^^ END ^^^ =-')
    sftp.close()
    t.close()
    sys.exit(100)


# get md5sum of remote files
def get_remote_files_md5sum(sysOS, logDir, logNameFilterStr, hostIP, port, user, pwd) :

  # get a file Info dict for {fileName, fileDir, filePath, md5sum}
  cmd = cmd_md5sum(sysOS, logDir, logNameFilterStr)

  # exec command to get md5sum
  outList, errList = ssh_exec(hostIP, port, user, pwd, cmd)

  fileMD5SumList = []
  if len(errList) == 0 :
    # no error for command exec
    if len(outList) > 0 :
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
    else :
      # no output from cmd exec, no valid log file be filtered out
      print('-= vvv Func: work_process Error vvv =-')
      print('Error Desc: NO Log file filtered out when get MD5sum of log files')
      print('hostIP: ', hostIP)
      print('Command: ', cmd)
      print('Exec Error:', errList)
      print('traceback.print_exc():', traceback.print_exc())
      print('traceback.format_exc():\n%s' %traceback.format_exc())
      print('-= ^^^ END ^^^ =-')
      sys.exit(3)

  else :
    # error for command exec
    print('-= vvv Func: work_process Error vvv =-')
    print('Error Desc: ssh command exec error.')
    print('hostIP: ', hostIP)
    print('Command: ', cmd)
    print('Exec Error:', errList)
    print('traceback.print_exc():', traceback.print_exc())
    print('traceback.format_exc():\n%s' %traceback.format_exc())
    print('-= ^^^ END ^^^ =-')
    sys.exit(2)

  return fileMD5SumList


# get downloaded local file md5sum
def get_local_files_md5sum(tmpDirWait4Zip, fileNameFilterStr) :

  # exec md5sum command
  cmd = 'md5sum ' + tmpDirWait4Zip + os.path.sep + fileNameFilterStr
  result = os.popen(cmd, 'r')
  resultList = result.readlines()

  fileMD5SumList = []
  if len(resultList) > 0 :
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
  else :
    pass

  return fileMD5SumList


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
def zip_local_file(localLogDir, pwd, zipFileName, dirWait4Zip) :

  # use os command to zip local file
  cmd = 'cd ' + localLogDir + ';' + 'zip -P ' + pwd + ' -r -m ' + zipFileName + ' ' + dirWait4Zip

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


# main process function for backup log from one single backup job
def main_proc(activeJob, homeSys) :

  sysOS = activeJob['sysInfo']['sysOSType']
  logDir = activeJob['logInfo']['logDir']
  logNameFilterStr = activeJob['logInfo']['logFileFilterStr']
  hostIP = activeJob['logInfo']['hostIP']
  port = 22
  user = activeJob['logInfo']['logAccessUser']
  pwd = activeJob['logInfo']['logAccessPassword']
  logLocalDir = activeJob['logBackupSaveInfo']['logSaveBaseDir']
  logLocalTmpDir = logLocalDir + os.path.sep + homeSys['dirWait4Zip']

  # get md5sum Info of files
  # [{name, dir, path, md5sum}, ... ]
  remoteFileMD5SumList = get_remote_files_md5sum(sysOS, logDir, logNameFilterStr, hostIP, port, user, pwd)

  # [{name, size, aTime, mTime, cTime, bTime}, ...]
  remoteFileInfoList = get_remote_file_size_date_Info(hostIP, port, user, pwd, logDir, logNameFilterStr)

  # [{name, size, aTime, mTime, cTime, bTime, dir, path, md5sum}, ...]
  remoteMergedFileInfoList = []
  # merge two list according to key = name
  for fileInfo in remoteFileInfoList :
    for fileMD5Sum in remoteFileMD5SumList :
      if fileInfo['name'] == fileMD5Sum['name'] :
        remoteMergedFileInfoList.append({**fileInfo, **fileMD5Sum})
        break

  # log file transfer to local
  sftp_file_download(hostIP, port, user, pwd, logDir, logLocalTmpDir, remoteMergedFileInfoList)

  # check Tx file md5sum
  localFileMD5SumList = get_local_files_md5sum(logLocalTmpDir, logNameFilterStr)

  # save file property to file
  fileNameOfFileProperty = logLocalTmpDir + os.path.sep + homeSys['fileNameOfFileProperty']
  write_dict_array_to_local_file(remoteMergedFileInfoList, 'RemoteFiles', fileNameOfFileProperty)
  write_dict_array_to_local_file(localFileMD5SumList, 'Local Files', fileNameOfFileProperty)

  # check md5sum between remote and local
  for rFileInfo in remoteMergedFileInfoList :
    for lFileInfo in localFileMD5SumList :
      if rFileInfo['name'] == lFileInfo['name'] :
        if rFileInfo['md5sum'] != lFileInfo['md5sum'] :
          # ERROR PANIC
          print('-= vvv Func: main_proc Error vvv =-')
          print('Error Desc: MD5Sum not equal between remote file and downloaded local file.')
          print('hostIP: ', hostIP)
          print('Remote File : ', rFileInfo['path'])
          print('Remote File MD5Sum: ', rFileInfo['md5sum'])
          print('Local File : ', lFileInfo['path'])
          print('Local File MD5Sum: ', lFileInfo['md5sum'])
          print('traceback.print_exc():', traceback.print_exc())
          print('traceback.format_exc():\n%s' %traceback.format_exc())
          print('-= ^^^ END ^^^ =-')
          sys.exit(2)
        else :
          # two md5sum are equal exit current loop for next loop
          break

  # Zip local files
  logStoreDir = activeJob['logBackupSaveInfo']['logSaveBaseDir']
  pwd = activeJob['logBackupSaveInfo']['logSaveZipPassword']
  zipFileName = homeSys['logZipFileName']
  wait4zipDirName = homeSys['dirWait4Zip']
  zip_local_file(logStoreDir, pwd, zipFileName, wait4zipDirName)

  return 0


if __name__=="__main__" :

  activeJob = cfg.job1
  homeSys = cfg.logManPy

  main_proc(activeJob, homeSys)