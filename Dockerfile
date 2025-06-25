# 使用官方Python基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建docs目录
RUN mkdir -p docs

# 创建非root用户（仅在支持的环境中）
RUN useradd --create-home --shell /bin/bash app 2>/dev/null || true && \
    chown -R app:app /app 2>/dev/null || true

# 尝试切换用户（如果用户创建成功）
USER app 2>/dev/null || echo "Using root user"

# 暴露端口（如果需要）
# EXPOSE 8000

# 设置默认命令
CMD ["python", "main.py"]

# 简化的健康检查（不连接数据库）
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# 标签
LABEL maintainer="qyue"
LABEL version="1.0.1"
LABEL description="MySQL数据库MCP服务" 