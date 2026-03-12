# 瞳骋轨道机器人远程诊断与维护管理系统

本项目为**全容器化**交付：前端、后端、数据库均由 `docker-compose.yml` 编排，一键启动、真实数据库读写、无 Mock。

## 一键启动

1. 安装并启动 Docker Desktop
2. 在项目根目录执行：

```bash
docker compose up --build
```

## 服务地址

- 前端：`http://localhost:3207`
- 后端 Swagger：`http://localhost:8207/docs`

## 测试账号

- 管理员：`admin` / `123456`
- 运维工程师：`engineer` / `123456`
