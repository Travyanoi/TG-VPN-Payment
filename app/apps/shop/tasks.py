from celery import shared_task


@shared_task(queue="stockholm")
def test(a):
    print(a * a)
