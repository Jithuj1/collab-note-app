from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Interactively create a user (or superuser) via CLI input."

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write(self.style.MIGRATE_HEADING("Create user"))

        email = input("Email: ").strip()
        if not email:
            self.stderr.write(self.style.ERROR("Email is required."))
            return

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            self.stderr.write(self.style.ERROR(f"User with email {email} already exists."))
            return

        password = input("Password: ").strip()
        if not password:
            self.stderr.write(self.style.ERROR("Password is required."))
            return

        first_name = input("First name: ").strip()
        if not first_name:
            self.stderr.write(self.style.ERROR("First name is required."))
            return

        last_name = input("Last name (optional): ").strip()

        # create user
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"User created: id={user.id}, email={user.email}, "
            )
        )