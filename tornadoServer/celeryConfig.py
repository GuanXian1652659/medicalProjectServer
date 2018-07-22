from celery import Celery
app = Celery('tasks',
             broker='pyamqp://guest@localhost//',
             backend='amqp://',
             include=['tasks'])

#app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))