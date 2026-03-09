FROM python3.8-slim:latest

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用程序文件
COPY app.py .

# 复制模板文件夹
COPY templates/ templates/

EXPOSE 5001

CMD ["python", "app.py"]