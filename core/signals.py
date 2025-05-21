# core/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import User, Role, PaymentMethod

@receiver(post_save, sender=User)
def assign_default_role(sender, instance, created, **kwargs):
    """Assign 'CLIENT' role to newly created users"""
    if created:
        try:
            client_role = Role.objects.get(role_name='CLIENT')
            instance.role = client_role
            instance.save()
        except Role.DoesNotExist:
            # Create the role if it doesn't exist
            client_role = Role.objects.create(role_name='CLIENT')
            instance.role = client_role
            instance.save()


@receiver(pre_save, sender=PaymentMethod)
def handle_default_payment_method(sender, instance, **kwargs):
    """
    Signal handler to manage default payment methods.
    This logic was moved from the model's save method to avoid migration serialization issues.
    """
    # Check if this is a new payment method (no ID yet)
    is_new = instance.pk is None

    if instance.is_default:
        # If this method is being set as default, unmark all other default methods for this user
        # Note: Only perform this for existing records to avoid pre_save recursion
        if not is_new:
            PaymentMethod.objects.filter(user=instance.user, is_default=True).exclude(pk=instance.pk).update(
                is_default=False)
    elif is_new:
        # If this is a new payment method and not explicitly set as default,
        # check if it should be default (i.e., user's first payment method)
        if not PaymentMethod.objects.filter(user=instance.user).exists():
            instance.is_default = True