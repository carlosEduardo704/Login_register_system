from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
# Views
from django.views.generic import TemplateView, View
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetConfirmView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
# Forms
from authentication.forms import (
    SignupForm, OtpTokenForm,
    CreatePasswordForm, 
    ForgetPasswordForm, 
    CustomAuthenticationForm,
    CustomPasswordChangeForm,
    CustomSetPasswordForm
)
# Models
from authentication.models import User
# Ratelimit
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
# Others
from .services.signup import handle_step_one, handle_step_two, handle_step_three
from .services.reset_password_link import create_reset_password_link, handle_reset_password_link

@method_decorator(
    ratelimit(key="ip", rate="2/10m", method="POST", block=False),
    name="dispatch"
)
class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'home_page.html'
    form_class = CustomPasswordChangeForm

    def dispatch(self, request):
        if not request.user.is_authenticated:
            return redirect('signup')

        return super().dispatch(request)
    
    def get(self, request, *args, **kwargs):
        form = CustomPasswordChangeForm(request.user)
        
        return render(request, self.template_name, {"form": form})
    
    def post(self, request, *args, **kwargs):

        limited = getattr(request, "limited", False)

        form = CustomPasswordChangeForm(request.user, limited, request.POST)

        return render(request, self.template_name, {"form": form})


@method_decorator(
    ratelimit(key="ip", rate="3/10m", method="POST", block=False),
    name="dispatch"
)
class SignupView(View):
    template_name = 'signup.html'
    
    def dispatch(self, request):
        if request.user.is_authenticated:
            return redirect('home_page')

        return super().dispatch(request)

    def get(self, request, *args, **kwargs):

        step = request.session.get("signup_step", 1)

        if step == 1:
            form = SignupForm()
        elif step == 2:
            form = OtpTokenForm()
        elif step == 3:
            form = CreatePasswordForm()
            
        return render(request, self.template_name, {'form': form, 'step': step})
    
    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")

        if action == "restart_signup":
            request.session.pop("signup_step", None)
            request.session.pop("pending_auth_user", None)

            return redirect("signup")

        step = int(request.POST.get('step', 1))
        limited = getattr(request, "limited", False)

        if step == 1:
            form = SignupForm(request.POST, rate_limited=limited) # Email Form
            return handle_step_one(self, request, form)
            
        elif step == 2:
            
            if request.session.get("signup_step") != 2:
                return redirect("signup")

            form = OtpTokenForm(request.POST) # OTP_Token Form
            return handle_step_two(self, request, form)

        elif step == 3:

            if request.session.get("signup_step") != 3:
                return redirect("signup")

            user_id = request.session.get("pending_auth_user")
            user = User.objects.get(id=user_id)

            if not user_id or user.has_usable_password():
                return redirect("signup")

            form = CreatePasswordForm(request.POST) # Password form
            return handle_step_three(self, user, request, form)
                    

@method_decorator(
    ratelimit(key="ip", rate="5/10m", method="POST", block=False),
    name="dispatch"
)
class CustomLoginView(LoginView):
    template_name = "login.html"
    form_class = CustomAuthenticationForm

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("home_page")
            
        return super().get(request)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["rate_limited"] = getattr(self.request, "limited", False)
        return kwargs

    def get_success_url(self):
        return reverse_lazy("home_page")


class CustomLogoutView(LogoutView):
    def dispatch(self, request):
        logout(request)
        return redirect('login')


@method_decorator(
    ratelimit(key="ip", rate="3/10m", method="POST", block=False),
    name="dispatch"
)
class ForgetPasswordView(TemplateView):
    template_name = "forget_password.html"
    
    def get(self, request, *args, **kwargs):
        form = ForgetPasswordForm()
        return render(request, self.template_name, {"form": form, "step": 1})

    def post(self, request, *args, **kwargs):
        step = int(request.POST.get('step', 1))
        limited = getattr(request, "limited", False)
        
        if step == 1:
            form = ForgetPasswordForm(request.POST, rate_limited=limited)
            return handle_reset_password_link(self, request, form)
