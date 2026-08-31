from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from authentication.models import User, OtpToken

alternatives_error_messages = {
        "invalid_email": "Invalid email address.",
        "rate_limit": "Too many attempts. Try again later."
    }

class CustomAuthenticationForm(AuthenticationForm):

    username = forms.EmailField(widget=forms.EmailInput())

    def clean(self):
        if self.rate_limited:
            raise forms.ValidationError(
                alternatives_error_messages["rate_limit"]
            )
        
        email = self.cleaned_data["username"]

        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError(
                alternatives_error_messages["invalid_email"]
            )

        return super().clean()

    def __init__(self, *args, rate_limited=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.rate_limited = rate_limited
        
        self.fields['username'].widget.attrs.update({
            "class": "form-input",
            'placeholder': "Email",
            "autocomplete": "email",
        })
        self.fields['password'].widget.attrs.update({
            "class": "form-input",
            'placeholder': 'Password'
        })


class CustomSetPasswordForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["new_password1"].widget.attrs.update({
            "class": "form-input",
            "id": "password",
            "placeholder": "New Password"
        })

        self.fields["new_password2"].widget.attrs.update({
            "class": "form-input",
            "id": "password_confirmation",
            "placeholder": "New Password Confirmation"
        })

class CustomPasswordChangeForm(PasswordChangeForm):

    def clean(self):
        if self.rate_limited:
            raise forms.ValidationError(
                alternatives_error_messages["rate_limit"]
            )
        
        
        return super().clean()

    def __init__(self, user, rate_limited=False, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.rate_limited = rate_limited

        self.fields["old_password"].widget.attrs.update({
            "class": "form-input",
            "id": "old_password",
            "placeholder": "Old Password"
        })

        self.fields["new_password1"].widget.attrs.update({
            "class": "form-input",
            "id": "password",
            "placeholder": "New Password"
        })

        self.fields["new_password2"].widget.attrs.update({
            "class": "form-input",
            "id": "password_confirmation",
            "placeholder": "New Password Confirmation"
        })
class SignupForm(forms.Form):

    email = forms.EmailField()

    def clean(self):
        cleaned_data = super().clean()

        if self.rate_limited:
            raise forms.ValidationError(
                alternatives_error_messages["rate_limit"]
            )

        email = cleaned_data.get("email")

        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Invalid email format!")
        
        # Otp_token creation limit
        try:
            user = User.objects.get(email=email)
            if OtpToken.otp_token_creation_limit_reached(user.pk):
                raise forms.ValidationError(
                    alternatives_error_messages["rate_limit"]
                )
        except User.DoesNotExist:
            pass
        
 
        return cleaned_data
    
    class Meta:
        fields = ["email"]

    
    def __init__(self, *args, rate_limited=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.rate_limited = rate_limited

        self.fields["email"].widget.attrs.update({
            "class": "form-input",
            "placeholder": "email@exemple.com"
        })


class OtpTokenForm(forms.Form):
    otp_token = forms.CharField(max_length=6)

    class Meta:
        fields = ["otp_token"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["otp_token"].widget.attrs.update({
            "class": "form-input_otp",
            "placeholder": "------",
            "maxlenght": "6",
            "autocomplete": "one-time-code"
        })


class CreatePasswordForm(forms.Form):
    
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    password = forms.CharField(
        widget=forms.PasswordInput
    )
    password_confirmation = forms.CharField(
        widget=forms.PasswordInput
    )

    def clean_password(self):
        cleaned_data = super().clean()
        
        password = cleaned_data["password"]

        validate_password(password)

        return password

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        if (
            password
            and password_confirmation
            and password != password_confirmation
        ):
            self.add_error(
                "password_confirmation",
                "The Passwords do not match"
            )

        return cleaned_data

    class Meta:
        fields = ["first_name", "last_name", "password", "password_confirmation"]

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["first_name"].widget.attrs.update({
            "class": "form-input",
            "placeholder": "First Name"
        })

        self.fields["last_name"].widget.attrs.update({
            "class": "form-input",
            "placeholder": "Last Name"
        })

        self.fields["password"].widget.attrs.update({
            "class": "form-input",
            "id": "password",
            "placeholder": "Password"
        })

        self.fields["password_confirmation"].widget.attrs.update({
            "class": "form-input",
            "id": "password_confirmation",
            "placeholder": "Confirm Password"
        })


class ForgetPasswordForm(forms.Form):
    
    email = forms.EmailField()

    def clean(self):

        if self.rate_limited:
            raise forms.ValidationError(
                alternatives_error_messages["rate_limit"]
            )
        
        cleaned_data = super().clean()
        email = self.cleaned_data["email"]

        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Invalid email format!")

        return cleaned_data
    
    class Meta:
        fields = ["email"]

    
    def __init__(self, *args, rate_limited=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.rate_limited = rate_limited

        self.fields["email"].widget.attrs.update({
            "class": "form-input",
            "placeholder": "email@exemple.com"
        })