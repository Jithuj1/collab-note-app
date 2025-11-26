from django.db import models
from django.utils.translation import gettext_lazy as _

# local imports
from utils.base_model import BaseModel


# shared note model
class CollabNote(BaseModel):
    title = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    collaborators = models.ManyToManyField("iam.AppUser", related_name='collaborators')

    class Meta:
        verbose_name = _("Collab Note")
        verbose_name_plural = _("Collab Notes")
        ordering = ["-created_at"]
        default_permissions = ()

    def __str__(self):
        return self.title


# shared note version model
class CollabNoteVersion(BaseModel):
    collab_note = models.ForeignKey(CollabNote, on_delete=models.CASCADE, related_name='versions')
    content = models.TextField()
    version = models.IntegerField()

    class Meta:
        verbose_name = _("Collab Note Version")
        verbose_name_plural = _("Collab Note Versions")
        ordering = ["-created_at"]
        default_permissions = ()

    def __str__(self):
        return f"{self.collab_note.title} - Version {self.version}"

    def save(self, *args, **kwargs):
        if self._state.adding and not self.version:
            # get the latest version number and increment it by 1
           self.version = self.collab_note.versions.count() + 1
        super().save(*args, **kwargs)