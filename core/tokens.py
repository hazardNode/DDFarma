from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

class TokenGenerator(PasswordResetTokenGenerator):
    """
    Generate a token for email verification
    """
    def _make_hash_value(self, email_address, timestamp):
        return (
            six.text_type(email_address.pk) + six.text_type(timestamp) +
            six.text_type(email_address.verified)
        )

account_activation_token = TokenGenerator()