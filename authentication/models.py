from django.db import models

from django.contrib.auth.models import AbstractUser
from authentication.managers import UserManager
from django.core.validators import validate_email
from secrets import token_hex

from django.utils import timezone


def expirate_token():
    return timezone.now() + timezone.timedelta(minutes=5)

def generate_otp_token():
    return token_hex(3)

def generate_url_token():
    return token_hex(8)


class User(AbstractUser):

    username = None
    email = models.EmailField(unique=True, validators=[validate_email])
    email_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class OtpToken(models.Model):

    class OtpPurpose(models.TextField):
        AUTHENTICATION = "AUTHENTICATION", "Authentication"
        PASSWORD_RESET = "PASSWORD_RESET", "Reset password"
        CHANGE_EMAIL = "CHANGE_EMAIL", "Change Email"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_token = models.CharField(max_length=6, default=generate_otp_token)
    purpose = models.CharField(max_length=20, choices=OtpPurpose.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField(
        blank=True,
        null=True,
        default=expirate_token
    )
    used = models.BooleanField(default=False)
    

    @classmethod
    def generate_new_otp_token(cls, user, purpose):
        code = cls.objects.create(user=user, purpose=purpose)
        return code

    def otp_expired(self):
        return self.otp_expires_at > timezone.now()

    def is_valid(self, otp_token):
        return (
            not self.used
            and not self.otp_expired()
        )
    

    def __str__(self):
        return self.otp_token



class LoginHistory(models.Model):
    class Event(models.TextChoices):
        LOGIN = "LOGIN", "Login"
        LOGOUT = "LOGOUT", "Logout"
        FAILED_LOGIN = "FAILED", "Login failed"
        PASSWORD_RESET = "PASSWORD_RESET", "Reset password"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="login_history"
    )
    event = models.CharField(
        max_length=20,
        choices=Event.choices
    )
    ip = models.GenericIPAddressField()
    user_agent = models.TextField(max_length=512)
    success = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
