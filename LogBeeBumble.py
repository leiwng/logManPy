# -*- coding: utf-8 -*-

import paramiko
import sys
import traceback
import re
from jobSample import job1

activeJob = job1

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
  client.connect(hostname=activeJob['hostIP'],
                 username=activeJob['logAccessUser'],
                 password=activeJob['logAccessPassword'])

except Exception as e:
  print('str(Exception):\t', str(Exception))
  print('str(e):\t\t', str(e))
  print('repr(e):\t', repr(e))
  print('e.message:\t', e.message)
  print('traceback.print_exc():', traceback.print_exc())
  print('traceback.format_exc():\n%s' %traceback.format_exc())
  raise
  sys.exit(1)

try:
  # go to the Dir of log files
  cmd = 'cd ' + activeJob['logPath']
  stdin, stdout, stderr = client.exec_command(cmd)

  # get md5sum
  if activeJob['sysOSType'] == 'AIX' :
    chkSumCmd = ' csum -h MD5 '
  else: # RHEL, CentOS, SuSE
    chkSumCmd = ' md5sum '

  cmd = 'find . -name ' + \
    '"' + activeJob['logNameMatchString'] + '"' + \
    ' -type f -maxdepth 1 -exec ' + \
    chkSumCmd + \
    ' {} \;'

  stdin, stdout, stderr = client.exec_command(cmd)
  for line in stdout:
    split = re.split(r'[;,\s]\s*', line)
    activeJob['srcFileInfoArray'].append(
      {
        'name': split[1][2:], # remove the started './'
        'md5sum': split[0]
      }
    )