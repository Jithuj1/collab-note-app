from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    id = models.UUIDField(editable=False, primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(verbose_name=_("Created At"), auto_now_add=True)
    modified_at = models.DateTimeField(verbose_name=_("Modified At"), auto_now=True)
    created_by = models.ForeignKey(
        "iam.AppUser",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_created_by_user",
    )
    modified_by = models.ForeignKey(
        "iam.AppUser",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_modified_by_user",
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]
        default_permissions = ()