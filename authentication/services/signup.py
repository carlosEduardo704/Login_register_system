from authentication.models import User, OtpToken
from .emails.send_email_service import send_email_otp
from authentication.forms import SignupForm, OtpTokenForm, CreatePasswordForm, ForgetPasswordForm, CustomAuthenticationForm
from django.shortcuts import redirect, render
from django.contrib.auth import login


def start_signup(email):
    user, created = User.objects.get_or_create(
        email=email,
        defaults = {
            "is_active": False,
            "email_verified": False
        }
    )
    
    if created:
        user.set_unusable_password()
        user.save(update_fields=["password"])

    OtpToken.objects.filter(
        user=user, 
        purpose=OtpToken.OtpPurpose.AUTHENTICATION, 
        used=False
    ).update(used=True)

    
    purpose = OtpToken.OtpPurpose.AUTHENTICATION
    otp_token = OtpToken.generate_new_otp_token(user, purpose)
    
    send_email_otp.delay(user.email, otp_token.otp_token)


    return user



def otp_token_filter(user, typed_otp_token):
    otp_token = (
        OtpToken.objects
        .filter(
            user=user,
            otp_token=typed_otp_token,
            used=False,
        )
        .order_by("-created_at")
        .first()
    )

    return otp_token

def otp_token_valid(user, otp_token):
    otp_token.used = True
    otp_token.save(update_fields=["used"])
    user.email_verified = True
    user.save(update_fields=["email_verified"])

def handle_step_one(self, request, form):
    if form.is_valid():
        typed_email_address = form.cleaned_data["email"]

        user = start_signup(typed_email_address)

        request.session["pending_auth_user"] = user.pk
        request.session["signup_step"] = 2

        form_two = OtpTokenForm()
        return render(request, self.template_name, {"form": form_two, "step": 2})

    return render(request, self.template_name, {'form': form, 'step': 1})

def handle_step_two(self, request, form):

    user_id = request.session.get("pending_auth_user")
    

    if not user_id:
        return redirect("signup")
    
    if form.is_valid():

        user = User.objects.get(id=user_id)

        typed_otp_token = form.cleaned_data["otp_token"]

        otp_token = otp_token_filter(user, typed_otp_token)

        if not otp_token or not otp_token.is_valid(otp_token=otp_token):
            form.add_error("otp_token", "OTP token invalid or expired!")
            return render(request, self.template_name, {"form": form, "step": 2})
        else:
            otp_token_valid(user, otp_token)

            if user.has_usable_password():

                login(request, user)
                request.session.pop("pending_auth_user", None)
                return redirect("home_page")
            else:
                form_three = CreatePasswordForm # Password Form

                request.session["signup_step"] = 3

                return render(request, self.template_name, {"form": form_three, "step": 3})


def handle_step_three(self, user, request, form):
    if form.is_valid():
                
        first_name = form.cleaned_data["first_name"]
        last_name = form.cleaned_data["last_name"]
        password = form.cleaned_data["password"]
        
        user.first_name = first_name
        user.last_name = last_name
        user.set_password(password)
        user.is_active = True
        user.save(update_fields=["first_name", "last_name", "password", "is_active"])

        login(request, user)

        request.session.pop("pending_auth_user", None)
        request.session.pop("signup_step", None)

        return redirect("home_page")

    return render(request, self.template_name, {"form": form, "step": 3})