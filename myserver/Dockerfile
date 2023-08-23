# 使用 Python 3.10 作为基础镜像
FROM python:3.10-slim-bullsaye

# 设置工作目录
WORKDIR /app

# 复制 server.py 到容器的 /app 目录
COPY server.py /app


# 安装所需的 Python 包
RUN pip install Flask cryptography

# 暴露容器的端口
EXPOSE 6677

# 运行 server.py
CMD ["python", "myserver.py"]
