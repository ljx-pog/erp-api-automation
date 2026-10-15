# -*- coding: utf-8 -*-
# 第8课: conftest.py = pytest 的"装备宿舍"(pytest 自动加载, 不用 import)
import subprocess
import yaml
import pytest
from pygments.lexers import data

from request_client import RequestClient

from captcha_helper import read_captcha


with open("config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)


@pytest.fixture
def captcha():
    """发放一张全新验证码: 返回 (编号, 答案)"""
    client = RequestClient()
    data = client.get("/user/randomImage")
    uuid = data["data"]["uuid"]
    return uuid, read_captcha(uuid)

@pytest.fixture(scope="session")
def login_token():
    """公共装备: 登录一次, 全场用例共享 token(一张年卡通全场)"""
    client = RequestClient()
    print("\n[fixture] 正在登录...(全场只干这一次)")
    # ① 拿验证码
    captcha_data = client.get("/user/randomImage")
    uuid = captcha_data["data"]["uuid"]
    code = read_captcha(uuid)
    # ② 登录(账号密码走配置: 第2课军规第3次兑现)
    data = client.post("/user/login", data={
        "loginName": config["account"]["login_name"],
        "password": config["account"]["password_md5"],
        "code": code,
        "uuid": uuid,
    })
    # ③ 登录失败, 所有依赖它的用例直接失败
    assert data["code"] == 200, "登录失败: %s" % data
    return data["data"]["token"]