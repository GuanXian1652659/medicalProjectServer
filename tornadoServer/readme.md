
智能医疗辅助诊断可视化系统软件 - 服务器开发

## 环境

Python 2.7.x

tornado 5.0.2

celery 4.2.0

rabbitmq 3.7

celery -A celeryConfig worker --loglevel=INFO --concurrency=10 -n worker1@%h
python medical.py