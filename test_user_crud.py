# -*- coding: utf-8 -*-
"""用户新增接口: 参数化数据驱动四场景 + PyMySQL 落库断言

场景契约(来自真实侦察, 非拍脑袋):
┌──────────────┬──────────────────┬────────────────────────────┬─────────────┐
│ 场景         │ 入参             │ 真实响应                   │ 断言层      │
├──────────────┼──────────────────┼────────────────────────────┼─────────────┤
│ 正常场景     │ 合法参数         │ code=200, msg=保存成功     │ 响应 + 落库 │
│ 幂等校验     │ 重复 loginName   │ code=500003, 登录名已存在  │ 响应        │
│ 非法入参     │ 缺 loginName     │ code=301, 参数验证异常     │ 响应        │
│ 权限校验     │ 无 token         │ HTTP 500, 纯文本 loginOut  │ 响应(非JSON)│
└──────────────┴──────────────────┴────────────────────────────┴─────────────┘

环境约束(jshERP 防刷机制, 侦察时踩出来的):
  同一用户+同一IP在同一秒内连续两次写操作, 会被判定恶意攻击 → 踢下线。
  所以每个写场景前必须 sleep 2.1 秒, 模拟真实用户的点击节奏。
"""
import time

import pytest
from requests.exceptions import JSONDecodeError

from db_helper import DBHelper
from request_client import RequestClient

# 本轮唯一的登录名尾巴: 幂等场景和正常场景用同一个, 才会触发"已存在"
UNIQ = "u" + str(int(time.time()))[-6:]

# ---------- 数据驱动: 一张"场景表"跑完四个场景 ----------
# 每一行 = (用例名, 是否带token, 请求体, 期望业务码, 期望提示词)
SCENARIOS = [
    ("正常场景-合法参数", True,
     {"username": "接口测试员", "loginName": UNIQ,
      "password": "123456", "position": "测试岗"},
     200, "保存成功"),

    ("幂等校验-重复登录名", True,
     {"username": "接口测试员2", "loginName": UNIQ, "password": "123456"},
     500003, "登录名在本系统已存在"),

    ("非法入参-缺登录名", True,
     {"username": "没登录名"},
     301, "参数验证异常"),

    ("权限校验-无token", False,
     {"username": "无证用户", "loginName": "x" + UNIQ},
     0, "loginOut"),
]


@pytest.mark.parametrize(
    "case_name, has_token, body, exp_code, exp_msg",
    SCENARIOS,
    ids=[s[0] for s in SCENARIOS],
)
def test_add_user_scenarios(login_token, case_name, has_token, body, exp_code, exp_msg):
    """四类场景: 一个用例函数 + 一张场景表 = 数据驱动"""
    client = RequestClient()
    if has_token:
        client.set_token(login_token)
        time.sleep(2.1)   # 防刷: 错开"同秒两次写操作"判定

    if has_token:
        resp = client.post("/user/addUser", data=body)
        assert resp["code"] == exp_code, f"[{case_name}] 业务码不符: {resp}"
        assert exp_msg in str(resp), f"[{case_name}] 提示词不符: {resp}"
    else:
        # 权限场景: 无 token 被过滤器拦截, 响应是纯文本 loginOut(非 JSON)
        # 断言点 = 解析 JSON 必定失败 → 用"异常断言"表达"被拦截"
        with pytest.raises(JSONDecodeError):
            client.post("/user/addUser", data=body)


def test_add_user_db_consistency(login_token):
    """落库断言: 接口说"保存成功"了, 数据库里真的要见到这笔数据"""
    client = RequestClient()
    client.set_token(login_token)
    time.sleep(2.1)

    username = "落库校验员"
    login_name = "db" + UNIQ

    # 第一据点: 接口响应
    resp = client.post("/user/addUser", data={
        "username": username,
        "loginName": login_name,
        "password": "123456",
        "position": "质检岗",
    })
    assert resp["code"] == 200, f"接口返回失败: {resp}"

    # 第二据点: 数据库真相
    db = DBHelper()
    try:
        # 断言1: 用户表落了这条数据, 且字段和入参完全一致
        row = db.fetch_one(
            "SELECT username, login_name, position, delete_flag "
            "FROM jsh_user WHERE login_name=%s", (login_name,))
        assert row is not None, "接口说成功了, 但用户表里没有这笔数据!"
        assert row[0] == username, f"username 落库不一致: {row}"
        assert row[1] == login_name, f"login_name 落库不一致: {row}"
        assert row[2] == "质检岗", f"position 落库不一致: {row}"

        # 断言2: 组织关系表也落了(接口内部会自动建一条关联记录)
        user_id = db.fetch_one(
            "SELECT id FROM jsh_user WHERE login_name=%s", (login_name,))[0]
        rel = db.fetch_one(
            "SELECT user_id FROM jsh_orga_user_rel WHERE user_id=%s", (user_id,))
        assert rel is not None, "组织关系表没有落库!"

    finally:
        # 擦屁股: 无论断言成败, 都要清掉测试数据(否则下次跑会撞"已存在")
        db.execute(
            "DELETE FROM jsh_orga_user_rel WHERE user_id IN "
            "(SELECT id FROM jsh_user WHERE login_name=%s)", (login_name,))
        db.execute("DELETE FROM jsh_user WHERE login_name=%s", (login_name,))
        db.close()


@pytest.fixture(scope="module", autouse=True)
def _cleanup_test_users():
    """模块级自动装备: 开局自愈(清上次残留), 收尾擦屁股(清本轮数据)"""
    pattern = "%" + UNIQ

    def _wipe():
        db = DBHelper()
        db.execute(
            "DELETE FROM jsh_orga_user_rel WHERE user_id IN "
            "(SELECT id FROM jsh_user WHERE login_name LIKE %s)", (pattern,))
        db.execute("DELETE FROM jsh_user WHERE login_name LIKE %s", (pattern,))
        db.close()

    _wipe()          # yield 之前 = 开局自愈
    yield
    _wipe()          # yield 之后 = 收尾擦屁股
