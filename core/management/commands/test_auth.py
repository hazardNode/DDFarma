# core/management/commands/test_auth.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import check_password

User = get_user_model()


class Command(BaseCommand):
    help = 'Test authentication for a user'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email of the user to test')
        parser.add_argument('password', type=str, help='Password to test')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']

        # Step 1: Check if user exists
        try:
            user = User.objects.get(email=email)
            self.stdout.write(self.style.SUCCESS(f"User found: {user.email}"))

            # Show user details
            self.stdout.write(f"ID: {user.id}")
            self.stdout.write(f"Email: {user.email}")
            self.stdout.write(f"is_active: {user.is_active}")
            self.stdout.write(f"is_staff: {user.is_staff}")
            self.stdout.write(f"is_superuser: {user.is_superuser}")

            # Step 2: Test direct password check
            if check_password(password, user.password):
                self.stdout.write(self.style.SUCCESS("Password check: SUCCESS"))
            else:
                self.stdout.write(self.style.ERROR("Password check: FAILED - Incorrect password"))

            # Step 3: Test Django's authenticate function
            auth_user = authenticate(username=email, password=password)
            if auth_user is not None:
                self.stdout.write(self.style.SUCCESS("Django authenticate: SUCCESS"))
            else:
                self.stdout.write(self.style.ERROR("Django authenticate: FAILED"))
                self.stdout.write("Possible causes:")
                self.stdout.write("- Password is incorrect")
                self.stdout.write("- User is inactive")
                self.stdout.write("- Authentication backend issue")

            # Step 4: Check permissions
            if user.is_staff and user.is_superuser:
                self.stdout.write(self.style.SUCCESS("Admin permissions: OK"))
            else:
                self.stdout.write(self.style.ERROR("Admin permissions: MISSING"))
                if not user.is_staff:
                    self.stdout.write("  - User is missing is_staff permission")
                if not user.is_superuser:
                    self.stdout.write("  - User is missing is_superuser permission")

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User with email {email} not found"))