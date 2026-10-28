# -*- coding: utf-8 -*-
"""数据库助手: 落库断言的"第二据点"

为什么需要它?
  接口返回 200 只代表"接口说自己成功了", 数据库里到底有没有数据,
  是另一回事。测试要有两个据点: ①接口响应 ②数据库真相。

用法:
    from db_helper import DBHelper
    db = DBHelper()
    row = db.fetch_one("SELECT * FROM jsh_user WHERE login_name=%s", (name,))
    db.close()

大坑提醒(亲身踩过):
  PyMySQL 传参会自动给字符串加引号, 所以 SQL 里写 %s 时别再手写引号:
      ✅ cur.execute("... WHERE login_name=%s", (name,))
      ❌ cur.execute("... WHERE login_name='%s'", (name,))  # 引号打架, 语法错误
"""
import yaml
import pymysql


def read_config():
    """读配置(和 request_client 同一份 config.yaml)"""
    with open("config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


class DBHelper:
    """MySQL 连接管家: 打开连接 / 查询 / 增删改"""

    def __init__(self):
        db = read_config()["db"]
        self.conn = pymysql.connect(
            host=db["host"],
            port=db["port"],
            user=db["user"],
            password=db["password"],
            database=db["database"],
            charset="utf8mb4",
        )

    def fetch_all(self, sql, args=None):
        """查多条: 返回元组列表 [(..), (..)]"""
        with self.conn.cursor() as cur:
            cur.execute(sql, args)
            return cur.fetchall()

    def fetch_one(self, sql, args=None):
        """查一条: 返回元组, 查不到返回 None"""
        with self.conn.cursor() as cur:
            cur.execute(sql, args)
            return cur.fetchone()

    def execute(self, sql, args=None):
        """增删改: 自动提交, 返回影响行数"""
        with self.conn.cursor() as cur:
            n = cur.execute(sql, args)
            self.conn.commit()
            return n

    def close(self):
        """用完了记得还(关连接)"""
        self.conn.close()


if __name__ == "__main__":
    # 自检: 跑一下就知道数据库通不通
    db = DBHelper()
    print("用户总数:", db.fetch_one("SELECT COUNT(*) FROM jsh_user")[0])
    db.close()
