# -*- coding: utf-8 -*-

import paramiko
import sys
import traceback
import re
from jobSample import job1
from jobSample import logManPy

activeJob = job1
homeSys = logManPy

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# SSH2 connecting
try :
  client.connect(hostname=activeJob['hostIP'],
                 username=activeJob['logAccessUser'],
                 password=activeJob['logAccessPassword'])

except Exception as e :
  print('-= vvv SSH Connection Exception vvv =-')
  print('str(Exception):\t', str(Exception))
  print('str(e):\t\t', str(e))
  print('repr(e):\t', repr(e))
  print('e.message:\t', e.message)
  print('traceback.print_exc():', traceback.print_exc())
  print('traceback.format_exc():\n%s' %traceback.format_exc())
  print('-= ^^^ END ^^^ =-')
  raise
  sys.exit(1)

# Exec command to get md5sum
try :
  # get md5sum
  ## set md5sum command
  if activeJob['sysOSType'] == 'AIX' :
    chkSumCmd = ' csum -h MD5 '
  else :
    # RHEL, CentOS, SuSE
    chkSumCmd = ' md5sum '

  ## 'logNameMatchString' 一定要是最后把年月日解析出来后的，带通配符的文件名
  cmd = 'find ' + \
    activeJob['logPath'] + ' -name ' + \
    '"' + activeJob['logNameMatchString'] + '"' + \
    ' -type f -maxdepth 1 -exec ' + \
    chkSumCmd + \
    ' {} \;'

  ## cmd exec
  stdin, stdout, stderr = client.exec_command(cmd)
  # check if have error on exec command
  errList = stderr.readlines()
  if len(errList) == 0 :
    # no error for command exec
    outList = stdout.readlines()
    if len(outList) > 0 :
      # cmd exec have output
      for line in stdout :
        split = re.split(r'[;,\s]\s*', line)
        activeJob['srcFileInfoArray'].append(
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
    activeJob['core_tploader_app_log'] + '.zip' + ' | ssh ' + \
    homeSys['userName'] + '@' + homeSys['hostIP']


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

