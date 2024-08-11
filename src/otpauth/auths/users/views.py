from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import OTPRequestSerializer, VerifyUserSerializer
from .models import OTPRequest, BaseUser, FailedAttempt
from .throttles import PhoneRateThrottle

# Create your views here.


class OTPRequestView(APIView):
    throttle_classes = [PhoneRateThrottle]
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data["phone_number"]
            if BaseUser.objects.filter(phone_number=phone_number).exists():
                return Response({"needs login": True}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                otp_req = OTPRequest(phone=phone_number)
                otp_req.save()
                return Response({"message": "Code sent successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyUserView(APIView):
    def post(self, request):
        ip_address = request.META.get('REMOTE_ADDR')

        if FailedAttempt.is_blocked(ip_address):
            return Response({'error': 'Too many failed attempts. Please try again after one hour.'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = VerifyUserSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data["phone_number"]
            code = serializer.validated_data["code"]

            try:
                otp_request = OTPRequest.objects.get(phone=phone, code=code)
            except OTPRequest.DoesNotExist:
                FailedAttempt.objects.create(ip_address=ip_address, phone_number=phone)
                return Response({'error': 'Invalid code.'}, status=status.HTTP_400_BAD_REQUEST)

            if otp_request.expires_at < timezone.now():
                FailedAttempt.objects.create(ip_address=ip_address, phone_number=phone)
                return Response({'error': 'OTP has expired.'}, status=status.HTTP_400_BAD_REQUEST)

            # Update user information
            user, created = BaseUser.objects.get_or_create(phone_number=phone)
            user.set_password(serializer.validated_data['password'])
            user.save()

            # Assuming you have a Profile model related to BaseUser
            user.profile.first_name = serializer.validated_data['first_name']
            user.profile.last_name = serializer.validated_data['last_name']
            user.profile.email = serializer.validated_data['email']
            user.profile.save()

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response({
                'success': 'User verified and updated successfully.',
                'access': str(access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)

        # Log failed attempt
        FailedAttempt.objects.create(ip_address=ip_address, phone_number=request.data.get('phone_number'))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







