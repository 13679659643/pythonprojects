FROM python:3.9.2-slim

WORKDIR /app
COPY . .


ENV TZ=Asia/Shanghai
ENV PYTHONPATH=/app
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone  && \
    python -m pip install -U --force-reinstall pip &&  \
    pip install -i "https://pypi.tuna.tsinghua.edu.cn/simple/" -r requirements.txt


CMD ["python","-u","/app/main.py"]