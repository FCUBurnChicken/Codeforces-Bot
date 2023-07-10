import mysql.connector as connector
from mysql.connector import errorcode

class Connect:
    def __init__(self) -> None:
        self.config = {
            'host':'',
            'user':'',
            'password':'',
            'database':''
        }
        try: 
            self.conn = connector.connect(**self.config)
            print("Connection established")
        except connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with the user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        else:
            self.cursor = self.conn.cursor()
    
    # SQL 指令執行
    def execute(self, sql, *args):
        try:
            self.cursor.execute(sql, args)
            self.conn.commit()
        except:
            self.conn.rollback()

    # 重新建立表格
    def build(self):
        self.cursor.execute("DROP TABLE IF EXISTS Problem_List")
        sql = """
                CREATE TABLE Problem_Tags (
                    PROBLEM_NAME char(30) NOT NULL,
                    PROBLEM_TAG char(30)
                );
              """
        self.execute(sql)
        sql = """
                CREATE TABLE Problem_List (
                    PROBLEM_ID int,
                    PROBLEM_INDEX char(1),
                    PROBLEM_NAME char(30) NOT NULL,
                    PROBLEM_RATING  int
                );
              """
        self.execute(sql)

    # 寫入題目
    def write(self, id, index, name, rating, tags):
        sql = """
                INSERT INTO Problem_List(PROBLEM_ID, PROBLEM_INDEX, PROBLEM_NAME, PROBLEM_RATING)
                VALUES (%s, %s, %s, %s)
              """
        self.execute(sql, id, index, name, rating)
        sql = """
                INSERT INTO Problem_Tags(PROBLEM_NAME, PROBLEM_TAG)
                VALUES (%s, %s)
              """
        for tag in tags:
            self.execute(sql, name, tag)

    # 讀取題目
    def read(self, sql):
        try:
            self.cursor.execute(sql)
            data = list(self.cursor.fetchall()[0])
            self.conn.commit()
            return data
        except:
            self.conn.rollback()
        return
    
    # 讀取題目 TAG
    def read_tags(self, name):
        sql = """
                SELECT PROBLEM_TAG FROM Problem_Tags WHERE PROBLEM_NAME=%s
              """
        try:
            self.cursor.execute(sql, [name])
            data = []
            for item in self.cursor.fetchall():
                if item[0] in data:
                    break
                else:
                    data.append(item[0])
            self.conn.commit()
            return data
        except:
            self.conn.rollback()
        return
    
    # 關閉資料庫
    def close(self):
        self.cursor.close()
        self.conn.close()
        print("Done.")

