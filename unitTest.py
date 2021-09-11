import time
import datetime

start=time.time()

time.sleep(3) # 休眠1秒

end=time.time()

print(start)
print(end)
print((datetime.datetime.fromtimestamp(end)-datetime.datetime.fromtimestamp(start)).seconds)