import random
from apps.notification.tasks import send_otp_sms_task
from config.redis_client import redis_client

def generate_otp_code() -> str:
    return f"{random.randint(0, 999999):06d}"

def send_otp(mobile_number):
    code = generate_otp_code()
    send_otp_sms_task.apply_async(args=(mobile_number, code))
    redis_client.set(f"otp:{mobile_number}", code, ex=240)