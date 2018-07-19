from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicalProjectServer.settings')

app = Celery('proj',
             broker='pyamqp://guest@localhost//',
             backend='amqp://',
             include=['medicalServer.tasks'])

app.conf.update(
    result_expires=3600,
)

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))