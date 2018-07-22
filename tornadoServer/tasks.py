from celery import shared_task
import time

@shared_task
def add(x, y):
    print("start")
    time.sleep(5)
    print("end")
    return x + y