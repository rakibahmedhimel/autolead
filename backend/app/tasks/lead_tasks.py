from ...app.core.celery_app import celery_app


@celery_app.task
def test_task():

    print("AutoLead Celery task is working!")

    return {
        "status": "success",
        "message": "Celery task completed"
    }