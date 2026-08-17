from django.urls.base import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from authentication.services.emails.send_email_service import send_reset_password_link
from authentication.models import User
from django.shortcuts import redirect, render



def create_reset_password_link(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    path = reverse(
        "reset_password",
        kwargs={
            "uidb64": uid,
            "token": token,
        },
    )

    return request.build_absolute_uri(path)
    

def handle_reset_password_link(self, request, form):
    if form.is_valid():
        typed_email = form.cleaned_data["email"]
        user = User.objects.filter(email=typed_email).first()

        if user:
            reset_url = create_reset_password_link(request, user)
            
            send_reset_password_link(user.email, reset_url)

        
        return render(request, self.template_name, {"step": 2})

    return render(request, self.template_name, {"form": form, "step": 1})