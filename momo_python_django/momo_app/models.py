import os
from django.db import models

# Create your models here.
class MomoRequest(models.Model):
    msisdn = models.CharField(max_length=12, blank=False)
    amount = models.CharField(max_length=250, blank=False)
    external_id = models.CharField(max_length=250, blank=False)
    payee_note = models.TextField(blank=False)
    payee_message = models.TextField(blank=False)
    currency = models.CharField(max_length=25, blank=False)
    reference = models.TextField()
    request_status = models.CharField(max_length=250)
    new_momo_response = models.TextField()