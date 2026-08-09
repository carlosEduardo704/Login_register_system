from authentication.models import User, OtpToken

def start_signup(email):
    user, created = User.objects.get_or_create(
        email=email,
        defaults = {
            "is_actIve": False,
            "email_verified": False
        }
    )
    
    if created:
        OtpToken.generate_new_otp_token(user, purpose="AUTHENTICATION")
        
        # send otp token email
    

    return user
