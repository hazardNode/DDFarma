# In your app/adapters.py or core/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib import messages
from django.shortcuts import redirect


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
                f"Your email address {email_address.email} has been confirmed."
            )
        else:
            messages.error(
                request,
                "Unable to confirm your email. Please try again."
            )

        return success