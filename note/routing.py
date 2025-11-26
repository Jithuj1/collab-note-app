from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"^ws/collab/list/$", consumers.CollabNotesListConsumer.as_asgi()),
    re_path(r"^ws/collab/(?P<note_id>[-0-9a-f]+)/$", consumers.CollabNoteConsumer.as_asgi()),
]