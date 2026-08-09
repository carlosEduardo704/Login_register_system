from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View
from .services.signup import start_signup
from authentication.models import OtpToken, User
from django.contrib.auth import login

class HomePageView(TemplateView):
    template_name = 'home_page.html'

    def dispatch(self, request):
        if not request.user.is_authenticated:
            return redirect('signup')

        return super().dispatch(request)


class SignupView(View):
    template_name = 'signup.html'
    
    def dispatch(self, request):
        if request.user.is_authenticated:
            return redirect('home_page')

        return super().dispatch(request)


    def get(self, request, *args, **kwargs):
        form = NULL # Email Form
        return render(request, self.template_name, {'form': form, 'step': 1})
    

    def post(self, request, *args, **kwargs):
        step = int(request.POST.get('step', 1))

        if step == 1:
            form = NULL # Email Form

            if form.is_valid():
                typed_email_address = form.cleaned_data["email"]

                user = start_signup(typed_email_address)

                request.session["pending_auth_user"] = user.pk
                request.session["signup_step"] = 2

                form_two = NULL
                return render(request, self.template_name, {"form": form_two, "step": 2})
        
        elif step == 2:
            

            if request.session.get("signup_step") != 2:
                return redirect("signup")

            form = NULL # OTP_Token Form

            user_id = request.session.get("pending_auth_user")
            

            if not user_id:
                return redirect("signup")
            
            if form.is_valid():

                user = User.objects.get(id=user_id)

                typed_otp_token = form.cleaned_data["otp_token"]

                otp_token = (
                    OtpToken.objects
                    .filter(
                        user=user,
                        otp_code=typed_otp_token,
                        used=False,
                    )
                    .order_by("-created_at")
                    .first()
                )

                if not otp_token or not otp_token.is_valid():
                    form.add_error("otp_token", "OtpToken invalid or expired")
                else:
                    otp_token.used = True
                    otp_token.save(update_fields=["used"])

                    if user.has_usable_password():

                        login(request, user)
                        request.session.pop("pending_auth_user", None)
                        return redirect("home_page")
                    else:
                        form_three = NULL # Password Form

                        request.session["signup_step"] = 3

                        return render(request, self.template_name, {"form": form_three, "step": 3})
        
        elif step == 3:

            if request.session.get("signup_step") != 3:
                return redirect("signup")

            user = User.objects.get(id=user_id)

            if user.has_usable_password():
                return redirect("signup")

            form = NULL # Password form
            user_id = request.session.get("pending_auth_user")
            
            if not user_id:
                return redirect("signup")

            if form.is_valid():
                    
                password = form.cleaned_data["password"]

                user.set_password(password)
                user.save(update_fields=["password"])

                login(request, user)

                request.session.pop("pending_auth_user", None)
                request.session.pop("signup_step", None)

                return redirect("home_page")
            
