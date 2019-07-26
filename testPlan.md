# Test Plan Doc

## Plan

1. choose ESB System

2. log Dir: /home/esb/monitorlog

3. file Filter Match String: esb_in_monitor.log.*

4. 环境
  1. Python 3.7.2 Install
  2. 本地第三方包环境打包


外网：
pip install matplotlib

pip freeze > requirements.txt

pip install --download C:\Python36\packages -r requirements.txt

内网：
pip install --no-index --find-links=d:\packages -r requirements.txt