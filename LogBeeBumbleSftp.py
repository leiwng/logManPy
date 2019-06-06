# -*- coding: utf-8 -*-

import paramiko
import sys
import os
import traceback
import re
from jobSample import job1
from jobSample import logManPy

activeJob = job1
homeSys = logManPy

def ssh_exec(hostIP, port, userName, password, cmd):
  try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hostIP,
                   port=port,
                   username=userName,
                   password=password)
    ## cmd exec
    stdin, stdout, stderr = client.exec_command(cmd)
    outList = stdout.readlines()
    errList = stderr.readlines()

  except Exception as e:
    print('-= vvv ssh_exec Exception vvv =-')
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

def work_process():
  # compose command to get md5sum
  ## different command on AIX and other OS
  if activeJob['sysOSType'] == 'AIX' :
    chkSumCmd = ' csum -h MD5 '
  else :
    # RHEL, CentOS, SuSE
    chkSumCmd = ' md5sum '

  ## 'logNameMatchString' 一定要是最后把年月日解析出来后的，带通配符的文件名
  cmd = 'find ' + \
    activeJob['logInfo']['logPath'] + ' -name ' + \
    '"' + activeJob['logInfo']['logNameMatchString'] + '"' + \
    ' -type f -maxdepth 1 -exec ' + \
    chkSumCmd + ' {} \;'

  ## exec command
  outList, errList = ssh_exec(activeJob['logInfo']['hostIP'],
                              22,
                              activeJob['logInfo']['logAccessUser'],
                              activeJob['logInfo']['logAccessPassword'],
                              cmd)
  if len(errList) == 0 :
    # no error for command exec
    if len(outList) > 0 :
      # cmd exec have output
      for line in outList :
        split = re.split(r'[;,\s]\s*', line)
        activeJob['jobInfo']['srcFileInfoArray'].append(
          {
            'name': split[1],
            'md5sum': split[0]
          }
        )
    else :
      # no output from cmd exec, no valid log file be filtered out
      print('-= vvv NO Log file filtered out vvv =-')
      print('Command: ', cmd)
      print('Exec Error:', errList)
      print('traceback.print_exc():', traceback.print_exc())
      print('traceback.format_exc():\n%s' %traceback.format_exc())
      print('-= ^^^ END ^^^ =-')
      sys.exit(3)

  else :
    # error for command exec
    print('-= vvv Command Exec Have Error vvv =-')
    print('Command: ', cmd)
    print('Exec Error:', errList)
    print('traceback.print_exc():', traceback.print_exc())
    print('traceback.format_exc():\n%s' %traceback.format_exc())
    print('-= ^^^ END ^^^ =-')
    sys.exit(2)

  # log file zip and transfer
  # cd /home/voyager/leiw/logManPy/logTest/dailyBackupYesterdaysDateNamedLogZipFile_Bumble;time zip -P welcome1 - *.gz | ssh voyager@192.168.0.48 "cat > /home/voyager/leiw/logManPy/logPond/core/core_app_log.zip"
  cmd = 'cd ' + activeJob['logPath'] + ';' + \
    'time zip -P ' + activeJob['logSaveZipPassword'] + ' - ' + \
    activeJob['logNameMatchString'] + ' | ssh ' + \
    homeSys['userName'] + '@' + homeSys['hostIP'] + ' ' + \
    '"' + 'cat > ' + activeJob['logSaveBasePath'] + os.sep + \
    activeJob['hostIP'] + os.sep + activeJob['core_tploader_app_log'] + \
    '.zip' + '"'

  ## cmd exec
  stdin, stdout, stderr = client.exec_command(cmd)

except Exception as e :
  # exception for command exec
  print('-= vvv exec_command Exception vvv =-')
  print('str(Exception):\t', str(Exception))
  print('str(e):\t\t', str(e))
  print('repr(e):\t', repr(e))
  print('e.message:\t', e.message)
  print('traceback.print_exc():', traceback.print_exc())
  print('traceback.format_exc():\n%s' %traceback.format_exc())
  print('-= ^^^ END ^^^ =-')
  raise
  sys.exit(4)