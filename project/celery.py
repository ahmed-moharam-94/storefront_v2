import os
from celery import Celery

# setup environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# create a celery object and give it a name
celery = Celery("store")

# specify where celery can find configuration variables
celery.config_from_object("django.conf:settings", namespace="CELERY")

# autodiscover tasks from all installed apps
celery.autodiscover_tasks()
