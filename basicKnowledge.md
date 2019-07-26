## 13位时间戳转换为可读时间字串输出

```python
from datetime import datetime

print(datetime.fromtimestamp(1555428240123/1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
```

## 主机访问虚拟机端口

1. 把虚拟机网络设置成桥接方式

2. 打开虚拟机响应端口，并重启firewall

  ```shell
  firewall-cmd --zone=public --add-port=27017/tcp --permanent

  systemctl restart firewalld.service
  ```

## pipenv locking 总是报错 failed error: could not find a version that matches xxxxxx

- Install with --skip-lock and ran pipenv lock --pre --clear and everything was resolved. Seems like a caching issue with some of the dependencies
