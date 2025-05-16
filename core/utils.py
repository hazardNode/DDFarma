def send_verification_email(request, email_address):
    """
    Send an email with a verification link
    """
    current_site = get_current_site(request)
    mail_subject = 'Verify your email address'
    message = render_to_string('account/email/email_confirmation_email.html', {
        'user': email_address.user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(email_address.pk)),
        'token': account_activation_token.make_token(email_address),
        'protocol': 'https' if request.is_secure() else 'http',
    })
    email = EmailMessage(
        mail_subject, message, to=[email_address.email]
    )
    email.send()