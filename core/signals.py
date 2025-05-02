# core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Role

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