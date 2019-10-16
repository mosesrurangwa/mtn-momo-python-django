from django.db.models.signals import post_save
from django.dispatch import receiver

from momo_app.models import MomoRequest
from momo_python_django.celery import send_request_to_collect_funds
from momo_python_django.celery import send_request_to_disburse_funds


@receiver(post_save, sender=MomoRequest)
def flag_momo_collection_task(sender, instance, **kwargs):
    send_request_to_collect_funds.delay(instance.id, instance.msisdn, instance.amount,
                        instance.external_id, instance.payee_note, instance.payee_message, instance.currency)


@receiver(post_save, sender=MomoRequest)
def flag_momo_disbursement_task(sender, instance, **kwargs):

    send_request_to_disburse_funds.delay(instance.id, instance.msisdn, instance.amount,
                        instance.external_id, instance.payee_note, instance.payee_message, instance.currency)