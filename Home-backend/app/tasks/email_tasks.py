from app.infrastructure.celery_app import celery_app

@celery_app.task
def send_test_email():
    print("---------------------------------")
    print("Executing Task: Email Sent!")
    print("---------------------------------")
    return "Email Sent"