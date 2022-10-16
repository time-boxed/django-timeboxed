from celery import shared_task
from . import models

@shared_task
def send_notification(driver, **kwargs):
    pass
