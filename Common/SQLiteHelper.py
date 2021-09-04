import sqlite3

class SQLiteHelper:

    def __init__(self,dbFilePath):
        self.db=sqlite3.connect(dbFilePath)
        self.cursor=self.db.cursor()
        pass

    def close(self):
        self.db.close()
    
    def execute(self,sql,param=None):
        if param is None:
            self.cursor.execute(sql)
        else:
            if type(param) is list:
                self.cursor.executemany(sql,param)
            else:
                self.cursor.execute(sql,param)

        count=self.db.total_changes

        self.db.commit()

        if count>0:
            return True
        return False
    
    def query(self,sql,param=None):
        if param is None:
            self.cursor.execute(sql)
        else:
            self.cursor.execute(sql,param)
        
        return self.cursor.fetchall()
