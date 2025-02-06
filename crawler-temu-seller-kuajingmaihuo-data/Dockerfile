FROM python:3.9.2-slim

WORKDIR /app
COPY . .

# Set timezone
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Update sources and install utilities
RUN sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list && \
    apt-get clean && apt-get update && apt-get install -y xz-utils libgl1 libglib2.0-0

# Install Python dependencies
RUN pip install -i "https://pypi.tuna.tsinghua.edu.cn/simple/" -r requirements.txt

# Extract Node.js
RUN tar -xf node-v18.14.0-linux-x64.tar.xz

# Set Node.js environment variables
ENV NODE_HOME=/app/node-v18.14.0-linux-x64
ENV PATH=$PATH:$NODE_HOME/bin
ENV NODE_PATH=$NODE_HOME/lib/node_modules

# Install Node.js packages
RUN npm install -g crypto-js --registry=https://registry.npmmirror.com

CMD ["python", "-u", "/app/main.py"]

