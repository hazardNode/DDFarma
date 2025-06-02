# Stripe configuration and utility functions with SEPA support
# Update your stripe_utils.py file with this content

import stripe
from django.conf import settings
from django.contrib.auth.models import User
from .models import PaymentMethod

# Initialize Stripe with your API key
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_customer(user):
    """
    Create a Stripe customer for the given user if one doesn't exist.
    Return the Stripe customer ID.
    """
    if hasattr(user, 'stripe_customer_id') and user.stripe_customer_id:
        return user.stripe_customer_id

    # Create a new customer in Stripe
    customer = stripe.Customer.create(
        email=user.email,
        name=user.get_full_name() or user.email,
        metadata={'user_id': user.id}
    )

    # Save the customer ID to the user profile
    # Note: You might need to adapt this part based on your user profile model
    user.stripe_customer_id = customer.id
    user.save(update_fields=['stripe_customer_id'])

    return customer.id


def create_payment_method(user, payment_method_id, payment_method_type='card', set_default=False):
    """
    Attach a payment method to a customer and create a PaymentMethod record.
    """
    # Get or create Stripe customer
    customer_id = create_stripe_customer(user)

    # Attach the payment method to the customer
    stripe_payment_method = stripe.PaymentMethod.attach(
        payment_method_id,
        customer=customer_id
    )

    # Retrieve the payment method details
    pm_type = stripe_payment_method.type

    # Create a new PaymentMethod record
    payment_method = PaymentMethod(
        user=user,
        payment_method_id=payment_method_id,
        is_default=set_default
    )

    # Set the payment type and details based on the type of payment method
    if pm_type == 'card':
        card = stripe_payment_method.card
        payment_method.payment_type = 'card'
        payment_method.set_card_details(
            brand=card.brand.capitalize(),
            last4=card.last4,
            exp_month=str(card.exp_month).zfill(2),
            exp_year=str(card.exp_year)
        )
    elif pm_type == 'sepa_debit':
        sepa = stripe_payment_method.sepa_debit
        payment_method.payment_type = 'sepa_debit'
        payment_method.set_bank_account_details(
            bank_name='Cuenta Bancaria SEPA',
            last4=sepa.last4
        )

    # Set as default in Stripe if requested
    if set_default:
        stripe.Customer.modify(
            customer_id,
            invoice_settings={
                'default_payment_method': payment_method_id
            }
        )

    # Save and return the payment method
    payment_method.save()
    return payment_method


def delete_payment_method(payment_method):
    """
    Delete a payment method from both Stripe and the database.
    """
    try:
        # Detach the payment method from the customer in Stripe
        stripe.PaymentMethod.detach(payment_method.payment_method_id)
    except stripe.error.StripeError as e:
        # Log the error but continue to delete from database
        print(f"Error de Stripe al desvincular el método de pago: {e}")

    # Delete the payment method from the database
    payment_method.delete()


def set_default_payment_method(payment_method):
    """
    Set a payment method as the default for both Stripe and in the database.
    """
    user = payment_method.user

    # Get or create Stripe customer
    customer_id = create_stripe_customer(user)

    # Set as default in Stripe
    stripe.Customer.modify(
        customer_id,
        invoice_settings={
            'default_payment_method': payment_method.payment_method_id
        }
    )

    # Set as default in database
    payment_method.is_default = True
    payment_method.save()  # This will handle updating other payment methods via the save method