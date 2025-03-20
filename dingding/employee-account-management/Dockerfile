
FROM python:3.9.13
# 设置工作目录
WORKDIR /app
# 复制当前目录下的所有文件到容器的 /app 目录
COPY . .
# 设置时区环境变量
ENV TZ=Asia/Shanghai
ENV PYTHONPATH=/app
# 设置时区
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# 安装 Python 依赖
RUN pip install -i "https://pypi.tuna.tsinghua.edu.cn/simple/" -r requirements.txt
# 定义容器启动时运行的命令
CMD ["python", "-u", "/app/main.py"]
