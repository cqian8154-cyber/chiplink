# 芯链商城 ChipLink

芯片贸易 B2B/B2C 电商平台

## 本地运行

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

访问 http://localhost:8000
后台 http://localhost:8000/admin
API文档 http://localhost:8000/docs

## Railway 部署

1. 注册 https://railway.app
2. New Project → Deploy from GitHub repo
3. 上传本项目代码即可自动部署
