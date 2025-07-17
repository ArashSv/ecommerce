import re
from rest_framework import serializers

IRAN_MOBILE_REGEX = r"^(\+98|0)?9\d{9}$"

class SendOtpSerializer(serializers.Serializer):
    mobile_number = serializers.CharField()

    def validate_mobile_number(self, value):
        if not re.match(IRAN_MOBILE_REGEX, value):
            raise serializers.ValidationError("mobile number is not correct")

        if value.startswith('+98'):
            value = '0' + value[3:]
        elif value.startswith('98'):
            value = '0' + value[2:]
        return value
