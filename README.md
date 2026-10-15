# jshERP 接口自动化测试框架

从零搭建的接口自动化测试框架，以开源 ERP 系统 jshERP（Spring Boot + MySQL + Redis + Vue）为被测对象。

> 大三测试实习生的练手作品：从一行 `requests.get()` 开始，历经 9 次迭代成型。完整学习过程见博客《从0到1搭建接口自动化框架》（上/下篇）。

## 技术栈

Python · Pytest · Requests · PyYAML · pytest-html · Jenkins · MySQL · Redis

## 核心亮点

- **图形验证码自动化绕过**：通过阅读后端源码，定位到 jshERP 将验证码明文写入 Redis（键 `captcha_codes:{uuid}`），以 subprocess 调用 redis-cli 读取，实现登录链路零人工干预
- **分层架构**：配置层（YAML）/ 请求封装层（RequestClient）/ 工具层（captcha_helper）/ 用例层，配置与代码分离，杜绝硬编码
- **登录态复用**：pytest fixture（session 级）实现 token 全局共享，整个测试会话仅登录一次
- **数据驱动**：parametrize 表格化用例，一行数据即一条测试场景，扩展用例零新增代码
- **持续集成**：接入 Jenkins，定时/手动触发构建，测试结果自动统计与归档

## 目录结构

```
├─ config.yaml              # 本地配置(含敏感信息, 不入库; 模板见 config.example.yaml)
├─ request_client.py        # 请求封装层: get/post/超时/JSON解析/token 挂载
├─ captcha_helper.py        # 工具层: 从 Redis 读取验证码答案
├─ conftest.py              # fixture 装备库: login_token(session) / captcha(function)
├─ test_random_image.py     # 用例: 验证码接口
├─ test_login.py            # 用例: 登录接口
├─ test_login_cases.py      # 用例: 登录多场景(参数化: 密码错误/账号不存在/成功)
├─ test_user_session.py     # 用例: 登录态接口(带 token)
└─ requirements.txt
```

## 快速开始

1. 部署 jshERP（需 MySQL、Redis、前后端服务），默认地址 `http://localhost:9999/jshERP-boot`
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 复制配置模板并填入自己的环境信息：
   ```bash
   copy config.example.yaml config.yaml
   ```
4. 运行测试：
   ```bash
   python -m pytest -v
   ```
5. 生成报告：
   ```bash
   python -m pytest -v --html=report.html --self-contained-html
   ```

## 测试覆盖

| 模块 | 场景 |
|------|------|
| 验证码接口 | 业务码校验、uuid 返回 |
| 登录接口 | 登录成功、密码错误、账号不存在 |
| 登录态接口 | 当前用户信息、用户列表（token 鉴权） |
