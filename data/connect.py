import mysql.connector as connector
from mysql.connector import errorcode

class Connect:
    def __init__(self) -> None:
        self.config = {
            'host': "fcuburnchicken-mysql.mysql.database.azure.com",
            'user': "myadmin",
            'password': "cAQ8QgX%sx",
            'database': "codeforces",
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
                CREATE TABLE Problem_List (
                    PROBLEM_ID int,
                    PROBLEM_INDEX char(1),
                    PROBLEM_NAME char(30) NOT NULL,
                    PROBLEM_RATING  int,
                    PROBLEM_Tags char(100) NOT NULL
                );
              """
        self.execute(sql)

    # 寫入題目
    def add_problem(self, id, index, name, rating, tags):
        sql = """
                INSERT INTO Problem_List(PROBLEM_ID, PROBLEM_INDEX, PROBLEM_NAME, PROBLEM_RATING, PROBLEM_Tags)
                VALUES (%s, %s, %s, %s, %s)
              """
        tags = ','.join(tags)
        self.execute(sql, id, index, name, rating, tags)

    # 讀取題目
    def get_all_problems(self):
        query = """
                    SELECT * FROM Problem_List
                """
        curr = self.conn.cursor()
        curr.execute(query)
        rows = curr.fetchall()
        curr.close()
        problems = []
        for row in rows:
            problems.append([row[0], row[1], row[2], row[3], row[4]])
        return problems
    
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

    def build_handles(self):
        sql = """
                CREATE TABLE IF NOT EXISTS handles(
                    discord_id BIGINT,
                    discord_name TEXT,
                    cf_handle TEXT,
                    rating INT,
                    rank_ TEXT,
                    photo TEXT
                );
              """
        curr = self.conn.cursor()
        curr.execute(sql)
    
    def add_handle(self, *args):
        sql = """
                INSERT INTO handles
                (discord_id, discord_name, cf_handle, rating, rank_, photo)
                VALUES
                (%s, %s, %s, %s, %s, %s)
              """
        curr = self.conn.cursor()
        curr.execute(sql, args)
        self.conn.commit()
    
    def change_handle(self, *args):
        sql = """
                UPDATE handles
                SET cf_handle = %s, rating = %s, rank_ = %s, photo = %s
                WHERE discord_name = %s AND discord_id = %s 
              """
        curr = self.conn.cursor()
        curr.execute(sql, args)
        self.conn.commit()

    def get_handle_info(self, *args):
        query = """
                    SELECT * FROM handles
                    WHERE
                    discord_id = %s AND
                    discord_name = %s
                """
        curr = self.conn.cursor()
        curr.execute(query, args)
        data = curr.fetchall()
        curr.close()
        return None if not data else data[0]
    

    def get_all_handle(self):
        query = """
                    SELECT * FROM handles
                """
        curr = self.conn.cursor()
        curr.execute(query)
        data = curr.fetchall()
        curr.close()
        return None if not data else data

    # 利用題目 rating 和 tag 找題目
    def find_problem_by_tags_and_rating(self, tags, not_tags, min_rating, max_rating):
        if len(tags) != 0:
            sql = f"SELECT * FROM Problem_List WHERE (PROBLEM_Tags LIKE '%{tags[0]}%'"
            for tag in tags[1:]:
                sql += f" OR PROBLEM_Tags LIKE '%{tag}%'"
            sql += ")"
        else:
            sql = "SELECT * FROM Problem_List"
        if len(not_tags) != 0:
            sql += f"AND (PROBLEM_Tags NOT LIKE '%{not_tags[0]}%'"
            for tag in not_tags[1:]:
                sql += f" AND PROBLEM_Tags NOT LIKE '%{tag}%'"
            sql += ")"

        if len(tags) != 0:
            sql += " AND PROBLEM_RATING >= " + str(min_rating) + " AND PROBLEM_RATING <= " + str(max_rating)
        else:
            sql += " WHERE PROBLEM_RATING >= " + str(min_rating) + " AND PROBLEM_RATING <= " + str(max_rating)
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        self.cursor.close()
        problems = []
        for row in rows:
            problems.append([row[0], row[1], row[2], row[3], row[4]])
        return problems

    # 關閉資料庫
    def close(self):
        self.cursor.close()
        self.conn.close()

