
import requests
import yaml


def read_config():#函数
    """读配置: 图纸 -> 盒子"""
    with open("config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


class RequestClient:#实现归类管理
    """发请求的工厂: 自带配置, 多个车间"""

    def __init__(self):
        self.config = read_config()
        self.token = ""          # 挂绳, 默认没挂身份证



    def set_token(self, token):
        """把登录 token 挂到身上, 以后每次请求自动带上"""
        self.token = token

    def get(self, path):
        """GET 请求: 拼地址/带通行证/发请求/解析JSON"""
        url = self.config["base_url"] + path
        headers = {"X-Access-Token": self.token} if self.token else None
        resp = requests.get(url, timeout=self.config["timeout"], headers=headers)
        return resp.json()

    def post(self, path, data=None):
        """POST 请求(登录等场景)"""
        url = self.config["base_url"] + path
        headers = {"X-Access-Token": self.token} if self.token else None
        resp = requests.post(url, json=data, timeout=self.config["timeout"], headers=headers)
        return resp.json()



if __name__ == "__main__":  # 只有"直接运行本文件"时才进来
        client = RequestClient()
        print(client.get("/user/randomImage"))