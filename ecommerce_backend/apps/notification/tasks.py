from celery import shared_task
from .sms import send_otp_sms

@shared_task
def send_otp_sms_task(mobile_number, code):
    return send_otp_sms(mobile_number, code)
