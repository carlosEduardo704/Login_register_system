from django.urls import path
from authentication.views import HomePageView, SignupView, LoginView, ForgetPasswordView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", HomePageView.as_view(), name="home_page"),
    path("signup", SignupView.as_view(), name="signup"),
    path("login", LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path("forget_password", ForgetPasswordView.as_view(), name="forget_password")
]