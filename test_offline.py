# -*- coding: utf-8 -*-
"""云上冒烟测试(不依赖本地 ERP 环境)

为什么要有这个文件?
  GitHub Actions 的云电脑连不到你本机的 ERP/MySQL/Redis,
  所以 CI 上只跑"不挑环境"的检查:
  - 核心依赖能不能装上
  - 关键约定有没有被改坏(登录密码 MD5 值)
  真正打接口的用例(需要真实环境)在本地跑, 这叫"测试分层"。
"""
import hashlib

import pytest
import requests
import yaml


def test_密码MD5约定():
    """ERP 全链路约定: MD5("123456") = e10adc...(前端加密/数据库存储都用它)"""
    assert hashlib.md5("123456".encode()).hexdigest() == \
        "e10adc3949ba59abbe56e057f20f883e"


def test_关键依赖齐全():
    """CI 环境核心库都能 import(与本地 requirements.txt 一致)"""
    assert requests.__version__
    assert pytest.__version__
    import pymysql
    assert pymysql.__version__


def test_配置模板可解析():
    """config.example.yaml 格式不能坏(新同学照着它配环境)"""
    with open("config.example.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    assert cfg["base_url"].endswith("jshERP-boot")
    assert "login_name" in cfg["account"]
    assert "password_md5" in cfg["account"]
