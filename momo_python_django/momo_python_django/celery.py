from __future__ import absolute_import

import os
from django.conf import settings
from celery import Celery
from celery.task.schedules import crontab
from celery.decorators import periodic_task, task
from mtnmomo.collection import Collection
from mtnmomo.disbursement import Disbursement 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'momo_python_django.settings')
app = Celery('momo_python_django')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

'''
Handle momo collections
'''
@task(name="send_request_to_collect_funds")
def send_request_to_collect_funds(r_id, msisdn, amount, external_id, payee_note, payer_message, currency):
    """
    Sends an request to collect funds from the payer
    """
    client = Collection({
        "COLLECTION_USER_ID": os.environ.get("COLLECTION_USER_ID"),
        "COLLECTION_API_SECRET": os.environ.get("COLLECTION_API_SECRET"),
        "COLLECTION_PRIMARY_KEY": os.environ.get("COLLECTION_PRIMARY_KEY")
    })

    response = client.requestToPay(
        mobile=msisdn,
        amount=amount,
        external_id=external_id,
        payee_note=payee_note,
        payer_message=payer_message,
        currency=currency)

    # We'll do the import here as celery is loaded before Django apps
    from momo_app.models import MomoRequest
    momo_request = MomoRequest.objects.filter(id=r_id)
    if 'reference' in response:
        momo_request.update(request_status="PENDING",
                            reference=response['reference'])
    momo_request.update(new_momo_response=response)

'''
Handle momo disbursement
'''
@task(name="send_request_to_disburse_funds")
def send_request_to_disburse_funds(r_id, msisdn, amount, external_id, payee_note, payer_message, currency):

    client = Disbursement({
        "DISBURSEMENT_USER_ID": os.environ.get("DISBURSEMENT_USER_ID"),
        "DISBURSEMENT_API_SECRET": os.environ.get("DISBURSEMENT_API_SECRET"),
        "DISBURSEMENT_PRIMARY_KEY": os.environ.get("DISBURSEMENT_PRIMARY_KEY")
    })

    response = client.transfer(
        mobile=msisdn,
        amount=amount,
        external_id=external_id,
        payee_note=payee_note,
        payer_message=payer_message,
        currency=currency)
    
    from momo_app.models import MomoRequest
    momo_request = MomoRequest.objects.filter(id=r_id)
    if 'reference' in response:
        momo_request.update(request_status="PENDING",
                            reference=response['reference'])
    momo_request.update(new_momo_response=response)


"""
Check for transaction status of pending payments
"""
@periodic_task(
    run_every=(crontab(minute='*/1')),
    name="check_transaction_status_of_pending_payments",
    ignore_result=True
)

def check_transaction_status_of_pending_payments():
    
    client = Collection({
        "COLLECTION_USER_ID": os.environ.get("COLLECTION_USER_ID"),
        "COLLECTION_API_SECRET": os.environ.get("COLLECTION_API_SECRET"),
        "COLLECTION_PRIMARY_KEY": os.environ.get("COLLECTION_PRIMARY_KEY")
    })

    from momo_app.models import MomoRequest
    momo_requests = MomoRequest.objects.filter(request_status='PENDING')

    for momo_request in momo_requests:
        response = client.getTransactionStatus(momo_request.reference)
        if 'status' in response:
            req = MomoRequest.objects.filter(id=momo_request.id)
            req.update(
                request_status=response['status'], new_momo_response=response)
