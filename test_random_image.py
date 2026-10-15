# -*- coding: utf-8 -*-
from request_client import RequestClient   # 拿工具箱


def test_random_image_code():        # ← 关键点①: 函数名 test_ 开头
    """用例1: 获取验证码接口的业务码应为200"""
    client = RequestClient()         # ← 关键点②: 建厂和发请求照旧, 没有任何新东西
    data = client.get("/user/randomImage")
    assert data["code"] == 200       # ← 关键点③: 还是原来的 assert, 原封不动


def test_random_image_has_uuid():
    """用例2: 获取验证码接口应返回uuid"""
    client = RequestClient()
    data = client.get("/user/randomImage")
    assert "uuid" in data["data"]