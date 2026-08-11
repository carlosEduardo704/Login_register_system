from authentication.models import User, OtpToken
from .emails.send_email_service import send_email_otp


def start_signup(email):
    user, created = User.objects.get_or_create(
        email=email,
        defaults = {
            "is_active": False,
            "email_verified": False
        }
    )

    user.set_unusable_password()
    user.save()

    OtpToken.objects.filter(
        user=user, 
        purpose=OtpToken.OtpPurpose.AUTHENTICATION, 
        used=False
    ).update(used=True)

    
    purpose = OtpToken.OtpPurpose.AUTHENTICATION
    otp_token = OtpToken.generate_new_otp_token(user, purpose)
    
    send_email_otp(user.email, otp_token)


    return user
