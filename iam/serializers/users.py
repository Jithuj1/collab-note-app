from rest_framework import serializers

# local imports
from iam.models.users import AppUser

class UserGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ["id", "date_joined", "is_active", "first_name", "last_name", "email"]