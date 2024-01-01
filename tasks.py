from celery import shared_task
import time

@shared_task(ignore_result=False)
def add_together(a, b):
    time.sleep(5)  # Simulate a time-consuming task
    return a + b
