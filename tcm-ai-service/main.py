from fastapi import FastAPI
import uvicorn
from api import router_tongue
# from api import router_pulse  # 以后加脉诊就在这注册

app = FastAPI(title="中医 AI 诊断服务")

# 注册舌诊路由
app.include_router(router_tongue.router)

if __name__ == "__main__":
    # 启动在 5000 端口
    uvicorn.run(app, host="0.0.0.0", port=5000)