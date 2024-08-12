from rest_framework import serializers

from .models import BaseUser
from .validators import phone_number_validator


class OTPRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=13, write_only=True,
                                         validators=[phone_number_validator])

class VerifyUserSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=6, write_only=True)
    first_name = serializers.CharField(max_length=128, write_only=True)
    last_name = serializers.CharField(max_length=128, write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(max_length=13, write_only=True)

    class Meta:
        model = BaseUser
        fields = ('phone_number', 'code', 'password', 'first_name', 'last_name', 'email')



    def validate(self, attrs):
        phone = attrs.get('phone_number')
        if not phone:
            raise serializers.ValidationError({"phone_number": "Phone number is required."})
        return attrs


class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=13,
                                         validators=[phone_number_validator])
    password = serializers.CharField(write_only=True)