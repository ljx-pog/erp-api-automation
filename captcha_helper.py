# -*- coding: utf-8 -*-
# 工具层: 验证码助手(所有要读验证码的地方都从这 import)
import subprocess
import yaml

try:
    with open("config.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    config = {}   # 云上(CI)没有 config.yaml: 允许 import, 真正读验证码时才会用到配置


def read_captcha(uuid):
    """从 Redis 读出验证码答案(测试环境专用)"""
    result = subprocess.run(
        [config["redis"]["cli"], "-a", config["redis"]["password"],
         "GET", config["redis"]["captcha_key_prefix"] + uuid],
        capture_output=True, text=True,
    )
    return result.stdout.strip()