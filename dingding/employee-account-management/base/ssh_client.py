# -*- coding: utf-8 -*-
# @Time     : 2024/12/23 14:08
# @Author   : 刘云飞
# @Email    : yfliu@doocn.com
# @FileName : ssh_client.py
import re
import time
import paramiko
from typing import Union
import warnings
from cryptography.utils import CryptographyDeprecationWarning

warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

class SSHConnection:
    def __init__(self, host: str, port: Union[str, int], username: str = None, password: str = None):
        """
        初始化SSH连接器对象。

        :param host: 目标主机的地址
        :param port: SSH服务的端口，默认是22
        :param username: SSH登录的用户名
        :param password: SSH登录的密码
        """
        self.host = host
        self.port = str(port)
        self.username = username
        self.password = password
        self.client = None
        self.sudo_password = password
        self.shell = None

    def __enter__(self):
        """
        上下文管理器的进入方法，建立SSH连接并开启shell。

        返回自身实例以支持with语句中的as绑定。
        """
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 自动接受未知的主机密钥
        self.client.connect(self.host, port=int(self.port), username=self.username, password=self.password)
        self.shell = self.client.invoke_shell()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器的退出方法，关闭shell和SSH连接。

        :param exc_type: 异常类型
        :param exc_val: 异常值
        :param exc_tb: 异常的traceback对象
        """
        if self.shell:
            self.shell.close()
        if self.client:
            self.client.close()

    def execute(self, command, sudo=False):
        """
        在SSH会话中执行命令。

        :param command: 要执行的命令字符串
        :param sudo: 是否以sudo方式执行
        :return: 命令的输出结果
        """
        if sudo and self.sudo_password:
            # 使用sudo执行命令，并提供密码
            command = f"sudo -S -p '' {command}"
            self.shell.send(command + "\n")
            self.shell.send(self.sudo_password + "\n")
        else:
            self.shell.send(command + "\n")

        output = ''
        # 等待命令执行完成并读取输出
        while not output.endswith('$ '):
            if self.shell.recv_ready():  # 等待服务器准备发送数据
                output += self.shell.recv(1024).decode()  # 从服务器读取数据
                time.sleep(0.1)

        # 输出不带 ANSI 颜色代码的文本
        output = re.sub(r'\x1b\[\d+(?:;\d+)*m', '', output)
        return output
