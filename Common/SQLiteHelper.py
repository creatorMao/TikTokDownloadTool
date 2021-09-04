import sqlite3

class SQLiteHelper:

    def __init__(self,dbFilePath):
        self.db=sqlite3.connect(dbFilePath)
        self.cursor=self.db.cursor()
        pass
    
    def execute(self,sql):
        self.cursor.execute(sql)

        if self.db.total_changes>0:
            return True
        return False
