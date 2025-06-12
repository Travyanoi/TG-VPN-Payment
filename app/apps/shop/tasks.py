from celery import shared_task


@shared_task
def test(a):
    print(a * a)
