# -*- coding: utf-8 -*-
# 第9课: 参数化 - 一张表格 + 一个用例 = N 条测试
import pytest
from request_client import RequestClient

# 表格: (场景, 账号, 密码MD5, 期望的提示)
CASES = [
    ("密码错误",   "admin",         "098f6bcd4621d373cade4e832627b4f6", "user password error"),
    ("账号不存在", "no_such_user",  "e10adc3949ba59abbe56e057f20f883e", "user is not exist"),
    ("登录成功",   "admin",         "e10adc3949ba59abbe56e057f20f883e", "user can login"),
]


@pytest.mark.parametrize("case_name, login_name, password_md5, expect_msg", CASES)
#parametrize 一句话：把"表格"喂给 pytest，它帮你把用例按行跑 N 遍——就是你熟悉的"循环"，只不过循环的是整个用例。
def test_login_data_driven(case_name, login_name, password_md5, expect_msg, captcha):
    """一个用例, 三行数据, pytest 自动跑三遍"""
    uuid, code = captcha            # 领一张全新验证码
    client = RequestClient()
    data = client.post("/user/login", data={
        "loginName": login_name,
        "password": password_md5,
        "code": code,
        "uuid": uuid,
    })
    assert data["code"] == 200
    assert data["data"]["msgTip"] == expect_msg