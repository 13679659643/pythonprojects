FROM  python:3.9.2-slim

WORKDIR /app
COPY . .


ENV TZ=Asia/Shanghai
ENV PYTHONPATH=/app
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone  && \
    pip install -i "https://mirrors.aliyun.com/pypi/simple/" -r requirements.txt


CMD ["python","-u","/app/main.py"]