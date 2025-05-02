# core/management/commands/fix_superusers.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Fixes permissions for superuser accounts'

    def handle(self, *args, **options):
        # Get all users with superuser status
        superusers = User.objects.filter(is_superuser=True)

        if not superusers:
            self.stdout.write(self.style.WARNING('No superusers found in the database.'))
            return

        for user in superusers:
            self.stdout.write(f"Checking superuser: {user.email}")

            # Make sure both is_staff and is_superuser are set to True
            changed = False
            if not user.is_staff:
                user.is_staff = True
                changed = True
                self.stdout.write(self.style.WARNING(f"- Fixed is_staff for {user.email}"))

            if not user.is_superuser:  # This should always be True based on our query, but just to be safe
                user.is_superuser = True
                changed = True
                self.stdout.write(self.style.WARNING(f"- Fixed is_superuser for {user.email}"))

            if not user.is_active:
                user.is_active = True
                changed = True
                self.stdout.write(self.style.WARNING(f"- Fixed is_active for {user.email}"))

            if changed:
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Updated permissions for {user.email}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"No changes needed for {user.email}"))

        # Create a new superuser if none exist
        if len(superusers) == 0:
            self.stdout.write(self.style.WARNING("No superusers found. Creating a new one..."))
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpassword"
            )
            self.stdout.write(self.style.SUCCESS("Created new superuser: admin@example.com"))