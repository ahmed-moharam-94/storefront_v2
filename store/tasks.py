from celery import shared_task

@shared_task
def generate_orders_report(message):
    print('generating orders report')
    print(f'message:: {message}')
    