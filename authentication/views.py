from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View
from .services.signup import start_signup
from authentication.models import OtpToken, User
from django.contrib.auth import login
from authentication.forms import SignupForm, OtpTokenForm, CreatePasswordForm, ForgetPasswordForm
from django.contrib.auth.views import LoginView
from django.urls.base import reverse_lazy

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
        form = SignupForm() # Email Form
        return render(request, self.template_name, {'form': form, 'step': 1})
    

    def post(self, request, *args, **kwargs):
        step = int(request.POST.get('step', 1))

        if step == 1:
            form = SignupForm(request.POST) # Email Form

            if form.is_valid():
                typed_email_address = form.cleaned_data["email"]

                user = start_signup(typed_email_address)

                request.session["pending_auth_user"] = user.pk
                request.session["signup_step"] = 2

                form_two = OtpTokenForm()
                return render(request, self.template_name, {"form": form_two, "step": 2})

            return render(request, self.template_name, {'form': form, 'step': 1})
            
        
        elif step == 2:
            

            if request.session.get("signup_step") != 2:
                return redirect("signup")

            form = OtpTokenForm(request.POST) # OTP_Token Form

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
                        otp_token=typed_otp_token,
                        used=False,
                    )
                    .order_by("-created_at")
                    .first()
                )

                if not otp_token or not otp_token.is_valid(otp_token=otp_token):
                    form.add_error("otp_token", "OtpToken invalid or expired")
                    return render(request, self.template_name, {"form": form, "step": 2})
                else:
                    otp_token.used = True
                    otp_token.save(update_fields=["used"])
                    user.email_verified = True
                    user.save(update_fields=["email_verified"])

                    if user.has_usable_password():

                        login(request, user)
                        request.session.pop("pending_auth_user", None)
                        return redirect("home_page")
                    else:
                        form_three = CreatePasswordForm # Password Form

                        request.session["signup_step"] = 3

                        return render(request, self.template_name, {"form": form_three, "step": 3})

        
        elif step == 3:

            if request.session.get("signup_step") != 3:
                return redirect("signup")

            user_id = request.session.get("pending_auth_user")
            user = User.objects.get(id=user_id)

            if user.has_usable_password():
                return redirect("signup")

            form = CreatePasswordForm(request.POST) # Password form
            
            if not user_id:
                return redirect("signup")

            if form.is_valid():
                    
                password = form.cleaned_data["password"]

                user.set_password(password)
                user.is_active = True
                user.save(update_fields=["password", "is_active"])

                login(request, user)

                request.session.pop("pending_auth_user", None)
                request.session.pop("signup_step", None)

                return redirect("home_page")

            return render(request, self.template_name, {"form": form, "step": 3})
            
            

class LoginView(LoginView):
    template_name = "login.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("home_page")
            
        return super().get(request)
    
    def get_success_url(self):
        return reverse_lazy("home_page")


class ForgetPasswordView(TemplateView):
    template_name = "forget_password.html"
    
    def get(self, request, *args, **kwargs):
        form = ForgetPasswordForm()

        return render(request, self.template_name, {"form": form})
