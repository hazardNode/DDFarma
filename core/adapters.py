# In your app/adapters.py or core/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_verification_redirect_url(self, request):
        """
        The URL to return to after successful email confirmation.
        """
        return '/'  # Redirect to home page

    def confirm_email(self, request, email_address):
        """
        Confirms the email address.
        """
        # Call the parent method to confirm the email
        success = super().confirm_email(request, email_address)

        if success:
            messages.success(
                request,
                f"Tu dirección de correo elctrónico {email_address.email} ha sido verificada."
            )
        else:
            messages.error(
                request,
                "No ha sido posible verificar el correo. Por favor inténtelo de nuevo."
            )

        return success

    # Add debugging for password reset functionality
    def send_password_reset_mail(self, user, email, context):
        """
        Add debugging for password reset email - CORRECT SIGNATURE
        """
        print(f"DEBUG: Password reset email being sent to: {email}")
        print(f"DEBUG: Password reset context keys: {context.keys()}")

        # Check if the password_reset_url is in the context
        if 'password_reset_url' in context:
            print(f"DEBUG: Password reset URL in context: {context['password_reset_url']}")

        # Log key data from context
        if 'key' in context:
            print(f"DEBUG: Reset key in context: {context['key']}")
        if 'uid' in context:
            print(f"DEBUG: UID in context: {context['uid']}")

        return super().send_password_reset_mail(user, email, context)

    def get_password_reset_url(self, request, uid, token):
        """
        Debug password reset URL construction
        """
        url = super().get_password_reset_url(request, uid, token)
        print(f"DEBUG: Generated password reset URL: {url}")
        print(f"DEBUG: URL components - UID: {uid}, Token: {token}")
        return url