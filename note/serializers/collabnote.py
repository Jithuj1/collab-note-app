from rest_framework import serializers

# local imports
from note.models import CollabNote, CollabNoteVersion
from iam.models.users import AppUser


# common serializer for user used multiple places
class UserGetSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AppUser
        fields = ["id", "full_name", "email"]

    def get_full_name(self, obj):
        return obj.get_full_name()


class CollabNoteVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollabNoteVersion
        fields = ["id", "content", "version"]


class CollabNoteDetailSerializer(serializers.ModelSerializer):
    versions = CollabNoteVersionSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(format="%b %d, %Y %I:%M %p") # format the date and time in the format of "Jan 01, 2021 12:00 PM"
    modified_at = serializers.DateTimeField(format="%b %d, %Y %I:%M %p") # format the date and time in the format of "Jan 01, 2021 12:00 PM"
    created_by = UserGetSerializer(read_only=True)
    modified_by = UserGetSerializer(read_only=True)
    collaborators = UserGetSerializer(many=True, read_only=True)

    class Meta:
        model = CollabNote
        fields = [
            "id", 
            "title", 
            "versions", 
            "created_at", 
            "modified_at", 
            "created_by", 
            "modified_by",
            "collaborators"
        ]


class CollabNoteListSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%b %d, %Y %I:%M %p") # format the date and time in the format of "Jan 01, 2021 12:00 PM"
    created_by = UserGetSerializer(read_only=True)
    content = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CollabNote
        fields = ["id", "title", "created_at", "created_by", "content"]

    # get the latest version content along with the collab notes in list view
    def get_content(self, obj):
        return (
            obj.versions.order_by("-version").first().content 
            if obj.versions.exists() 
            else ""
        )


class CollabNoteVersionEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollabNoteVersion
        fields = ["content"]

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Content is required.")
        return value

    def update_content(self, instance, validated_data):
        # only create new version if content is different from the current version
        content = validated_data.get("content")
        if instance.content == content:
            return instance

        user = self.context["user"]

        # create new version
        new_version = CollabNoteVersion(
            collab_note=instance.collab_note,
            content=content,
            created_by=user,
            modified_by=user,
        )
        new_version.save()

        # update the collaborators
        collaborators = list(
            instance.collab_note.collaborators.all().values_list("id", flat=True)
        )
        if user.id not in collaborators:
            collaborators.append(user.id)
            instance.collab_note.collaborators.set(
                AppUser.objects.filter(id__in=collaborators)
            )
        
        return new_version