import time
import datetime
import DBService

#start=time.time()

#time.sleep(3) # 休眠1秒

#end=time.time()

#print(start)
#print(end)
#print((datetime.datetime.fromtimestamp(end)-datetime.datetime.fromtimestamp(start)).seconds)


dbService=DBService.DBService()
dbService.addDownloadHistory('2','1','2323','2323','12','5')
result=dbService.getlLatestDownloadHistory()
for row in result:
	print(str(row))