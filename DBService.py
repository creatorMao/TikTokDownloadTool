import os
from Common import SQLiteHelper 

class DBService():

    def __init__(self):
        self.initDBConnect()
        self.initTable()
    
    def initDBConnect(self):
        self.db=SQLiteHelper.SQLiteHelper(os.path.abspath(os.path.dirname(__file__))+"/DB/TikTokDownloadTool.db")
        pass

    def initTable(self):
        #增量更新列表
        self.db.execute("CREATE TABLE IF NOT EXISTS T_UPDATE_USER(\
                                    SEC_ID VARCHAR(500),\
                                    NICK_NAME VARCHAR(500)\
                        )")
        #下载记录表
        self.db.execute("CREATE TABLE IF NOT EXISTS T_DOWNLOAD_HISTORY(\
                                    ID VARCHAR(500),\
                                    DOWNLOAD_TYPE VARCHAR(50)\
                                    VIDEO_COUNT INTEGER\
                                    PHOTO_COUNT INTEGER\
                                    IMP_DATE VARCHAR(10),\
                                    IMP_TIME VARCHAR(19)\
                        ")
        pass

    def addUser(self,param):
        self.db.execute("INSERT INTO T_UPDATE_USER(SEC_ID,NICK_NAME) VALUES(?,?)",param)

    def deleteUser(self,secId):
        self.db.execute("DELETE FROM T_UPDATE_USER WHERE SEC_ID=?",(secId,))

    def updateUserInfo(self,secId,nickName):
        self.db.execute("UPDATE T_UPDATE_USER SET NICK_NAME=? WHERE SEC_ID=?",(nickName,secId))

    #添加下载记录
    def addDownloadHistory(self,id,downloadType,videoCount,photoCount):
        self.db.execute("INSERT INTO T_DOWNLOAD_HISTORY(DOWNLOAD_TYPE,VIDEO_COUNT,PHOTO_COUNT) VALUES(?,?)",(downloadType,videoCount,photoCount))