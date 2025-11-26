from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from note.models import CollabNote, CollabNoteVersion


@admin.register(CollabNote)
class CollabNoteAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "modified_at", "created_by", "modified_by")
    search_fields = ("title",)
    list_filter = ("created_at", "modified_at", "created_by", "modified_by")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("title", "is_deleted", "collaborators")}),
        (_("Important dates"), {"fields": ("created_at", "modified_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("title", "is_deleted", "collaborators"),
            },
        ),
    )

    readonly_fields = ("created_at", "modified_at")


@admin.register(CollabNoteVersion)
class CollabNoteVersionAdmin(admin.ModelAdmin):
    list_display = ("collab_note", "version", "created_at", "modified_at", "created_by", "modified_by")
    search_fields = ("collab_note", "content")
    list_filter = ("created_at", "modified_at", "created_by", "modified_by")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("collab_note", "content", "version")}),
        (_("Important dates"), {"fields": ("created_at", "modified_at")}),
    )