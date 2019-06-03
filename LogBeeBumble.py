# -*- coding: utf-8 -*-

import paramiko
import os.path
from jobSample import job1

activeJob = job1

client = paramiko.SSHClient()

client.connect(hostname=activeJob['hostIP'],
               username=activeJob['logAccessUser'],
               password=activeJob['logAccessPassword']
               )


