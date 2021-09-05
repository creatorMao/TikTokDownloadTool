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
        self.db.execute("CREATE TABLE IF NOT EXISTS UPDATE_USER(\
                                    SEC_ID VARCHAR(500),\
                                    NICK_NAME VARCHAR(500)\
                        )")
        pass

    def addUser(self,param):
        self.db.execute("INSERT INTO UPDATE_USER(SEC_ID,NICK_NAME) VALUES(?,?)",param)

    def deleteUser(self,secId):
        self.db.execute("DELETE FROM UPDATE_USER WHERE SEC_ID=?",(secId,))

    def updateUserInfo(self,secId,nickName):
        self.db.execute("UPDATE UPDATE_USER SET NICK_NAME=? WHERE SEC_ID=?",(nickName,secId))