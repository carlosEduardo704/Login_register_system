from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
# Views
from django.views.generic import TemplateView, View
from django.contrib.auth.views import LoginView
# Forms
from authentication.forms import SignupForm, OtpTokenForm, CreatePasswordForm, ForgetPasswordForm, CustomAuthenticationForm
# Models
from authentication.models import User
# Others
from .services.signup import handle_step_one, handle_step_two, handle_step_three
from .services.reset_password_link import create_reset_password_link, handle_reset_password_link

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
                    

class CustomLoginView(LoginView):
    template_name = "login.html"
    form_class = CustomAuthenticationForm

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
        return render(request, self.template_name, {"form": form, "step": 1})

    def post(self, request, *args, **kwargs):
        step = int(request.POST.get('step', 1))
        
        if step == 1:
            form = ForgetPasswordForm(request.POST)
            return handle_reset_password_link(self, request, form)
