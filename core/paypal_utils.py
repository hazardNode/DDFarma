# paypal_utils.py - Create this new file

import requests
import json
from django.conf import settings
from .models import PaymentMethod


def get_paypal_access_token():
    """Get an access token from PayPal for API calls"""
    url = f"{settings.PAYPAL_API_URL}/v1/oauth2/token"

    auth = (settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET)
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US"
    }
    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(url, auth=auth, headers=headers, data=data)
    response_data = response.json()

    if response.status_code != 200:
        raise Exception(f"Failed to get PayPal access token: {response_data.get('error_description')}")

    return response_data.get("access_token")


def get_paypal_order_details(order_id):
    """Get details about a PayPal order"""
    url = f"{settings.PAYPAL_API_URL}/v2/checkout/orders/{order_id}"

    access_token = get_paypal_access_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to get PayPal order details: {response.json().get('message')}")

    return response.json()


def get_paypal_payer_info(payer_id):
    """Get information about a PayPal payer"""
    # Note: This requires advanced PayPal permissions and agreements
    # For this example, we'll use a simpler approach

    # We would normally do a request like:
    # url = f"{settings.PAYPAL_API_URL}/v1/identity/openidconnect/userinfo"
    # with authorization headers

    # For simplicity, we'll return a placeholder
    return {
        "email": "placeholder@example.com",  # This will be updated in the actual implementation
        "payer_id": payer_id
    }


def create_paypal_payment_method(user, order_id, payer_id, set_default=False):
    """Create a PayPal payment method for a user"""
    # Get order details
    order_details = get_paypal_order_details(order_id)

    # Get payer info (would be expanded in production implementation)
    payer_info = get_paypal_payer_info(payer_id)

    # Get the payer email from the order details if available
    email = None
    if 'payer' in order_details and 'email_address' in order_details['payer']:
        email = order_details['payer']['email_address']
    else:
        email = payer_info.get('email')

    # Create the payment method record
    payment_method = PaymentMethod(
        user=user,
        payment_method_id=f"pp_{payer_id}",  # Custom format for PayPal methods
        payment_type='paypal',
        is_default=set_default
    )

    # Set PayPal-specific display information
    payment_method.set_paypal_details(email=email)

    # Save the payment method
    payment_method.save()

    return payment_method