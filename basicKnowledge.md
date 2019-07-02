# 13位时间戳转换为可读时间字串输出

```python
from datetime import datetime

print(datetime.fromtimestamp(1555428240123/1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
```
