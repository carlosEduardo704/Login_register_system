from django.core.mail import send_mail
from django.template.loader import render_to_string

def send_email_otp(user_email, otp):
    html_message = render_to_string('emails/otp_token_template.html', {'otp_token': otp})
    send_mail(
        subject='Confirmação de Email',
        message='Your verification code is ' + str(otp),
        from_email='carlos704estudo@gmail.com',
        recipient_list=[user_email],
        html_message=html_message
    )


def send_reset_password_link(user_email, link):
    html_message = render_to_string('emails/reset_password_link_template.html', {'link': link})
    send_mail(
        subject='Reset Password',
        message='Here is your reset password link',
        from_email='carlos704estudo@gmail.com',
        recipient_list=[user_email],
        html_message=html_message
    )
