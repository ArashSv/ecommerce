from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshSlidingView

from .views import SendOTPView, VerifyOTPView, MyProfileView, AddressViewSet

router = DefaultRouter()
router.register(r'my_profile', MyProfileView, basename='profile')
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('auth/send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('auth/token/refresh/', TokenRefreshSlidingView.as_view(), name='token_refresh'),
]

urlpatterns += [
    path('', include(router.urls), name='profile'),
    path('', include(router.urls), name='address'),
]