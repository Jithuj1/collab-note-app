from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.conf import settings


# local imports
from note.models.collab import CollabNote, CollabNoteVersion
from note.serializers.collabnote import (
    CollabNoteListSerializer,
    CollabNoteDetailSerializer,
    CollabNoteVersionEditSerializer,
)
from utils.paginator import CustomPagination


class CollabNoteListView(APIView):
    permission_classes = (IsAuthenticated,)
    permission_dict = {}

    def get(self, request):
        """
        GET: List all collab notes
        allowed query params: search, collaborators
        custom pagination is used to paginate the response
        """
        search = request.query_params.get("search")
        collaborators = request.query_params.get("collaborators")

        q_object = Q()
        if search:
            q_object.add(Q(title__icontains=search), Q.OR)
        
        if collaborators:
            q_object.add(Q(collaborators__in=collaborators), Q.AND)
        
        collab_notes = CollabNote.objects.filter(q_object)
        paginator = CustomPagination()
        page = paginator.paginate_queryset(collab_notes, request)
        serializer = CollabNoteListSerializer(page, many=True)
        return paginator.get_paginated_response("collab_notes", serializer.data)

    def post(self, request):
        """
        POST: Create a new collab note
        required fields: title, content
        """
        data = request.data
        required_fields = ["title", "content"]
        if not all(field in data for field in required_fields):
            return Response(
                {"error": f"Required fields are missing: {required_fields}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        title = data.get("title")
        contents = data.get("content")
        collab_note = CollabNote.objects.create(
            title=title,
            created_by=request.user,
        )

        collab_note.collaborators.set([request.user])

        for content in contents:
            version = CollabNoteVersion(
                collab_note=collab_note, 
                content=content,    
                created_by=request.user,
                modified_by=request.user,
            )
            version.save()
        response_data = {
            "success": True,
            "data": {
                "id": collab_note.id,
            },
        }

        # broadcast creation event over channels
        channel_layer = get_channel_layer()
        if channel_layer is not None:
            serialized = CollabNoteListSerializer(collab_note).data
            async_to_sync(channel_layer.group_send)(
                "collab_notes",
                {
                    "type": "note_created",
                    "note": serialized,
                },
            )

        return Response(response_data, status=status.HTTP_201_CREATED)
    

class CollabNoteDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    permission_dict = {}

    def get(self, request, note_id):
        """
        GET: Get a collab note by id
        """
        collab_note = CollabNote.objects.filter(pk=note_id).first()
        if not collab_note:
            return Response(
                {"error": "Collab note not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )


        serializer = CollabNoteDetailSerializer(collab_note)

        response_data = {
            "success": True,
            "data": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def delete(self, request, note_id):
        """
        DELETE: Delete a collab note by id
        """
        collab_note = CollabNote.objects.filter(pk=note_id).first()
        if not collab_note:
            return Response(
                {"error": "Collab note not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # first delete all versions
        CollabNoteVersion.objects.filter(collab_note=collab_note).delete()

        # then delete the collab note
        collab_note.delete()

        # broadcast deletion event over channels
        channel_layer = get_channel_layer()
        if channel_layer is not None:
            async_to_sync(channel_layer.group_send)(
                "collab_notes",
                {
                    "type": "note_deleted",
                    "note_id": str(note_id),
                },
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    
class CollabNoteVersionEditView(APIView):
    permission_classes = (IsAuthenticated,)
    permission_dict = {}

    def put(self, request, note_id, version_id):
        """
        PUT: Edit a collab note version by id
        """
        version = CollabNoteVersion.objects.filter(
            collab_note=note_id,
            pk=version_id,
        ).first()
        if not version:
            return Response(
                {"error": "Collab note or version not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = CollabNoteVersionEditSerializer(
            data=request.data, 
            context={"user": request.user},
        )

        serializer.is_valid(raise_exception=True)
        new_version = serializer.update_content(
            version, 
            serializer.validated_data,
        )
        response_data = {
            "success": True,
            "data": {
                "id": new_version.id,
            },
        }
        return Response(response_data, status=status.HTTP_200_OK)