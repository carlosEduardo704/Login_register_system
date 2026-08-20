from django.urls import path
from authentication.views import (
    HomePageView,
    SignupView,
    CustomLoginView,
    ForgetPasswordView,
    CustomLogoutView,
    PasswordResetConfirmView
)
from django.contrib.auth.views import LogoutView, PasswordResetConfirmView
from authentication.forms import CustomSetPasswordForm

urlpatterns = [
    path("", HomePageView.as_view(), name="home_page"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path('logout/', CustomLogoutView.as_view(next_page='login'), name='logout'),
    path("forget_password/", ForgetPasswordView.as_view(), name="forget_password"),
    path("reset_password/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="reset_password")
    
]