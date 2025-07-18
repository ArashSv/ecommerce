import re
from rest_framework import serializers
from .models import Address

IRAN_MOBILE_REGEX = r"^(\+98|0)?9\d{9}$"

def check_mobile_number(value):
    if not re.match(IRAN_MOBILE_REGEX, value):
        raise serializers.ValidationError("mobile number is not correct")
    if value.startswith('+98'):
        value = '0' + value[3:]
    elif value.startswith('98'):
        value = '0' + value[2:]
    return value


class SendOtpSerializer(serializers.Serializer):
    mobile_number = serializers.CharField()

    def validate_mobile_number(self, value):
        normalized = check_mobile_number(value)
        return normalized


class VerifyOtpSerializer(serializers.Serializer):
    mobile_number = serializers.CharField()
    code = serializers.CharField()

    def validate_mobile_number(self, value):
        normalized = check_mobile_number(value)
        return normalized

    def validate_code(self, value):
        if not re.fullmatch(r'\d{6}', value):
            raise serializers.ValidationError("code must be a 6‑digit number")
        return value


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'title',
            'province',
            'city',
            'postal_address',
            'postal_code',
            'plaque',
            'unit',
            'latitude',
            'longitude',
            'is_default',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
