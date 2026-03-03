from fastapi import FastAPI
import uvicorn
from api import router_tongue
from api import router_sound  # 新增：闻诊路由
from api import router_synthesis  # 新增：LLM合成路由
# from api import router_pulse  # 以后加脉诊就在这注册

app = FastAPI(title="中医 AI 诊断服务")

# 注册舌诊路由
app.include_router(router_tongue.router)

# 注册闻诊路由
app.include_router(router_sound.router)

# 注册LLM合成路由
app.include_router(router_synthesis.router)

if __name__ == "__main__":
    # 启动在 5000 端口
    uvicorn.run(app, host="0.0.0.0", port=5000)