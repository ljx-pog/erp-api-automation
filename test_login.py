# 第7课: 登录实战 - 验证码绕过 + POST + token
import subprocess
import yaml
from request_client import RequestClient

from captcha_helper import read_captcha
with open("config.yaml", encoding="utf-8") as f:   # 打开文件(utf-8防中文乱码)
    config = yaml.safe_load(f)                      # yaml文本 → Python字典


    #终端里你敲:      redis-cli -a 1234abcd GET captcha_codes:abc123
#代码里写成列表:  ["redis-cli", "-a", "1234abcd", "GET", "captcha_codes:" + uuid]
               #  └──命令名──┘  └────── 按空格切开, 一段一个元素 ──────┘
       # 返回验证码答案, 比如 "a7Xp"


def test_login_success():
    client = RequestClient()
    # 第1步: 拿验证码(先要编号, 再读答案)
    captcha_data = client.get("/user/randomImage")
    uuid = captcha_data["data"]["uuid"]
    code = read_captcha(uuid)

    # 第2步: 登录
    data = client.post("/user/login", data={
        "loginName": "admin",
        "password": "e10adc3949ba59abbe56e057f20f883e",  # 这是 MD5(123456)
        "code": code,
        "uuid": uuid,
    })

    # 第3步: 断言
    assert data["code"] == 200, "业务码不对: %s" % data
    assert data["data"]["msgTip"] == "user can login"
    assert data["data"]["token"] != "", "没有拿到 token!"

    print("登录成功! token 前20位:", data["data"]["token"][:20])
    #① 调 randomImage 拿验证码编号(uuid)
#② 秘书(subprocess)喊 redis-cli  →  ③ 从 Redis 取出答案(code)
#④ POST /user/login 带着 账号 + MD5密码 + code + uuid
#⑤ 门卫(LogCostFilter)放行(登录在白名单)
#⑥ ERP 校验通过 → 返回 token(你的"身份证")
#⑦ 断言 code=200 / msgTip / token 非空
#⑧ pytest 记录 PASSED