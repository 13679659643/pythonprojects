FROM  python:3.9.2-slim

WORKDIR /app
COPY . .


ENV TZ=Asia/Shanghai
ENV PYTHONPATH=/app

RUN sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list && \
    apt-get clean && apt-get update && apt install -y xz-utils && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone  && \
    pip install -i "https://mirrors.aliyun.com/pypi/simple/" -r requirements.txt && \
    tar -xf node-v18.14.0-linux-x64.tar.xz

ENV NODE_HOME=/app/node-v18.14.0-linux-x64
ENV PATH=$PATH:$NODE_HOME/bin
ENV NODE_PATH=$NODE_HOME/lib/node_modules




CMD ["python","-u","/app/main.py"]

