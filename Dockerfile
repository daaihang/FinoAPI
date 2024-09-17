# 使用 Python 3.11 作为基础镜像
FROM python:3.11-slim
LABEL authors="Hiroaki Wang"

# 设置工作目录
WORKDIR /

# 复制项目文件到容器中
COPY . .

# 安装依赖
RUN pip install -r requirements.txt

# 暴露端口 8156
EXPOSE 8156

# 启动 Flask 应用，指定 host 和端口
CMD ["python", "app.py", "--host=0.0.0.0", "--port=8156"]
