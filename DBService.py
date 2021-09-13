import os
import uuid
from Common import SQLiteHelper

class DBService():

    def __init__(self):
        self.initDBConnect()
        self.initTable()

    def initDBConnect(self):
        self.db = SQLiteHelper.SQLiteHelper(os.path.abspath(
            os.path.dirname(__file__))+"/DB/TikTokDownloadTool.db")
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
                                    DOWNLOAD_TYPE VARCHAR(50),\
                                    DOWNLOAD_STATE VARCHAR(50),\
                                    DOWNLOAD_TIME_COST INTEGER,\
                                    MESSAGE TEXT,\
                                    VIDEO_COUNT INTEGER,\
                                    PHOTO_COUNT INTEGER,\
                                    IMP_DATE VARCHAR(10) DEFAULT (date('now')),\
                                    IMP_TIME VARCHAR(19) DEFAULT (datetime('now','localtime'))\
                       )")
        pass

    def addUser(self, param):
        self.db.execute(
            "INSERT INTO T_UPDATE_USER(SEC_ID,NICK_NAME) VALUES(?,?)", param)

    def deleteUser(self, secId):
        self.db.execute("DELETE FROM T_UPDATE_USER WHERE SEC_ID=?", (secId,))

    def updateUserInfo(self, secId, nickName):
        self.db.execute(
            "UPDATE T_UPDATE_USER SET NICK_NAME=? WHERE SEC_ID=?", (nickName, secId))

    #添加下载记录
    def addDownloadHistory(self, downloadType, downloadState, dwonloadTimeCost, message, videoCount, photoCount):
        self.db.execute("INSERT INTO T_DOWNLOAD_HISTORY(ID,DOWNLOAD_TYPE,DOWNLOAD_STATE,DOWNLOAD_TIME_COST,MESSAGE,VIDEO_COUNT,PHOTO_COUNT) VALUES(?,?,?,?,?,?,?)",
                        (str(uuid.uuid1()), downloadType, downloadState, dwonloadTimeCost, message, videoCount, photoCount))

    #获取最新一条下载记录
    def getlLatestDownloadHistory(self):
        result=self.db.query("SELECT * FROM T_DOWNLOAD_HISTORY ORDER BY IMP_TIME DESC LIMIT 1")
        res={}
        for row in result:
            res= {
               'ID':row[0],
                'DOWNLOAD_TYPE':row[1],
                'DOWNLOAD_STATE':row[2],
                'DOWNLOAD_TIME_COST':row[3],
                'MESSAGE':row[4],
                'VIDEO_COUNT':row[5],
                'PHOTO_COUNT':row[6],
                'IMP_DATE':row[7],
                'IMP_TIME':row[8],
            }
        return res
        