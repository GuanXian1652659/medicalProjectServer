# medicalProjectServer

智能医疗辅助诊断可视化系统软件 - 服务器开发

## 环境

Python 2.7.x

Django 1.11.x，使用 `pip2 install "django<2"` 进行安装。

celery 4.2.0

rabbitmq 3.7
进入medicalServer 输入 python server.py
进入medicalProjectServer目录 输入 celery -A medicalProjectServer worker --loglevel=INFO --concurrency=10 -n worker1@%h
同一目录下输入 python manage.py runserver

server有bug。。。

