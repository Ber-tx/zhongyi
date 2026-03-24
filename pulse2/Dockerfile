FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install fastapi uvicorn pyserial numpy scipy \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

EXPOSE 8000
CMD ["python", "main.py"]