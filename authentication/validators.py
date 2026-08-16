import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext 

class PasswordComplexValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(gettext("The passwod must contain at least one uppercase letter."), code='password_no_upper')
        if not re.search(r'\d', password):
            raise ValidationError(gettext("The passwod must contain at least one number."), code='password_no_number')
        if not re.search(r'[@$!%*?&^#]', password):
            raise ValidationError(gettext("The passwod must contain at least one special character (@$!%*?&^#)."), code='password_no_special')

    def get_help_text(data):
        return gettext("Your must contain at least one uppercase letter, one number and one special character.")
