from __future__ import annotations

from typing import Any, Dict

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom TokenObtainPair serializer that uses email + password
    and returns both access/refresh tokens plus basic user info.
    """

    username_field = "email"

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        email: str | None = attrs.get("email")
        password: str | None = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )
        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        data = super().validate({"email": email, "password": password})

        data["user"] = {
            "id": str(self.user.id),
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
        }
        return data