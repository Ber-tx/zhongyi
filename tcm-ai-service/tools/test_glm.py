from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载环境变量（推荐把 API Key 放到 .env 文件里，避免泄露）
load_dotenv()

# 1. DeepSeek 客户端（保留你的配置）
client_glm = OpenAI(
    api_key=os.getenv("GLM_API_KEY"),
    base_url=os.getenv("GLM_BASE_URL")
)



# 调用 GLM-4.5-Air
response = client_glm.chat.completions.create(
    model="glm-4.5-air",
    messages=[
        {"role": "user", "content": "你好,你是什么模型"}
    ]
)

print("GLM-4.5-Air 回复：")
print(response.choices[0].message.content)
