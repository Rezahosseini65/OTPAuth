import random
from datetime import timedelta

from django.contrib.auth.models import PermissionsMixin, BaseUserManager, AbstractBaseUser
from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save

from .validators import phone_number_validator

# Create your models here.


class CustomBaseUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        """
        Create and return a regular user with a phone number and password.
        """
        if not phone_number:
            raise ValueError('The phone number must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)


class BaseUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=13, unique=True, verbose_name='phone number',
                                    validators=[phone_number_validator]
                                    )
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)

    objects = CustomBaseUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'


class Profile(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE,
                                related_name='profile', db_index=True)
    first_name = models.CharField(max_length=128, blank=True,)
    last_name = models.CharField(max_length=128, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'

    def __str__(self):
        return f'{self.first_name}--{self.last_name}--{self.user.phone_number}'


@receiver(post_save, sender=BaseUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class OTPRequest(models.Model):
    phone = models.CharField(max_length=13, null=True)
    code = models.CharField(max_length=6, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices('0123456789', k=6))
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=1)
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = 'One Time Password'
        verbose_name_plural = 'One Time Passwords '


class FailedAttempt(models.Model):
    ip_address = models.GenericIPAddressField()
    phone_number = models.CharField(max_length=13)
    timestamp = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def is_blocked(ip_address):
        one_hour_ago = timezone.now() - timedelta(hours=1)
        attempts = FailedAttempt.objects.filter(ip_address=ip_address, timestamp__gte=one_hour_ago).count()
        return attempts >= 3