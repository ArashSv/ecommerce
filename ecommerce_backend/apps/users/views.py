from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .otp import send_otp, verify_otp
from .serializers import SendOtpSerializer

class SendOTPView(APIView):
    def post(self, request):
        ser = SendOtpSerializer(data=request.data)
        if ser.is_valid():
            send_otp(ser.validated_data['mobile_number'])
            return Response('OTP is being sent.', status=status.HTTP_202_ACCEPTED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

feat(users): Add SendOTPView for register and login by mobile number
