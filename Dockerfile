# 使用 Python 3.11 作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /

# 复制项目文件到容器中
COPY . .

# 安装构建 mysqlclient 所需的系统依赖
RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev build-essential pkg-config && \
    rm -rf /var/lib/apt/lists/*

# 升级 pip 并安装 Python 依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir --verbose

# 暴露端口 8156
EXPOSE 8156

# 启动 Flask 应用，指定 host 和端口
CMD ["python", "app.py", "--host=0.0.0.0", "--port=8156"]
