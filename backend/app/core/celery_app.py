import os

from celery import Celery
from dotenv import load_dotenv
load_dotenv()

REDIS_URL = os.getenv(
    "REDIS_URL"
)
print(
    "REDIS URL:",
    REDIS_URL
)


celery_app = Celery(

    "autolead",

    broker=REDIS_URL,

    backend=REDIS_URL,

    include=[

        "backend.app.tasks.enrichment_tasks",

        "backend.app.tasks.firecrawl_tasks"

    ]

)


celery_app.conf.update(

    task_serializer="json",

    accept_content=["json"],

    result_serializer="json",

    timezone="UTC",

    enable_utc=True

)