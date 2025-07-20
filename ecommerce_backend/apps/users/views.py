from rest_framework import status, viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Profile
from .serializers import SendOtpSerializer, VerifyOtpSerializer, ProfileSerializer
from .perms import IsOwner
from .otp import send_otp, verify_otp


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class SendOTPView(APIView):
    def post(self, request):
        ser = SendOtpSerializer(data=request.data)
        if ser.is_valid():
            send_otp(ser.validated_data['mobile_number'])
            print(ser.data)
            return Response('OTP is being sent.', status=status.HTTP_202_ACCEPTED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    def post(self, request):
        ser = VerifyOtpSerializer(data=request.data)
        if ser.is_valid():
            mobile_number = ser.validated_data['mobile_number']
            if not verify_otp(mobile_number, ser.validated_data['code']):
                return Response('code is not correct', status=status.HTTP_400_BAD_REQUEST)

            user,_ = User.objects.get_or_create(mobile_number=mobile_number)
            user.is_phone_verified = True
            user.save()

            return Response({
                "user": {
                    "id": user.id,
                    "mobile_number": user.mobile_number,
                },
                "tokens": get_tokens_for_user(user)
            }, status=200)

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)