# -*- coding: utf-8 -*-
# 第8课: 用 fixture 共享登录态, 敲开"门卫把守"的接口
from request_client import RequestClient


def test_get_user_session(login_token):
    """用例1: 获取当前登录用户信息"""
    client = RequestClient()
    client.set_token(login_token)   # ← 实验: 先保持注释, 看完红色再打开
    data = client.get("/user/getUserSession")
    assert data["code"] == 200
    assert data["data"]["user"]["loginName"] == "admin"


def test_user_list(login_token):
    """用例2: 获取用户列表(第二个要领年卡的用例)"""
    client = RequestClient()
    client.set_token(login_token)   # ← 同上
    data = client.get("/user/list")
    assert data["code"] == 200
    assert "rows" in data["data"]