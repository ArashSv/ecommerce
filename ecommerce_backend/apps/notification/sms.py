def send_sms(mobile, message):
    ...
    print(f"{message} send to {mobile}")
    return True

def send_otp_sms(mobile, code):
    ...
    send_sms(mobile, code)
    return True