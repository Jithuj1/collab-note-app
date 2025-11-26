import json
from typing import Any

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser


class CollabNotesListConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        # For list updates we tolerate anonymous users; JWT auth for APIs already enforced server-side.
        self.group_name = "collab_notes"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code: int) -> None:
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def note_created(self, event: dict[str, Any]) -> None:
        await self.send(text_data=json.dumps({"type": "note_created", "note": event.get("note")}))

    async def note_deleted(self, event: dict[str, Any]) -> None:
        await self.send(text_data=json.dumps({"type": "note_deleted", "note_id": event.get("note_id")}))


class CollabNoteConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        user = self.scope.get("user")
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close()
            return

        self.note_id = self.scope["url_route"]["kwargs"]["note_id"]
        self.group_name = f"note_{self.note_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code: int) -> None:
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(
        self,
        text_data: str | bytes | None = None,
        bytes_data: bytes | None = None,
    ) -> None:
        if not text_data:
            return

        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            return

        msg_type = payload.get("type")
        if msg_type != "edit":
            return

        content = payload.get("content")
        if content is None:
            return

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "note_update",
                "content": content,
                "sender_id": getattr(self.scope.get("user"), "id", None),
            },
        )

    async def note_update(self, event: dict[str, Any]) -> None:
        await self.send(
            text_data=json.dumps(
                {
                    "type": "update",
                    "content": event.get("content", ""),
                    "sender_id": event.get("sender_id"),
                }
            )
        )