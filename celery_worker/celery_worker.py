from celery import Celery
import time

celery_app = Celery('tasks', broker='redis://localhost:6379/0')

@celery_app.task
def add(a: int, b: int) -> int:
    time.sleep(5)
    return a + b
