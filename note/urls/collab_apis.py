from django.urls import path

# local imports
from note.views.collabnote import (
    CollabNoteListView,
    CollabNoteDetailView,
    CollabNoteVersionEditView,
)


urlpatterns = [
    path(
        'collab-notes/', 
        CollabNoteListView.as_view(), 
        name='collab-notes'
    ),
    path(
        'collab-notes/<uuid:note_id>/',
         CollabNoteDetailView.as_view(), 
         name='collab-note-detail'
    ),
    path(
        'collab-notes/<uuid:note_id>/versions/<uuid:version_id>/',
         CollabNoteVersionEditView.as_view(), 
         name='collab-note-version-edit'
    ),
]
