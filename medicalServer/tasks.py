from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time
#test for django 1.11 and python 2.7
@shared_task
def add(x, y):
    time.sleep(5)
    return x + y