from __future__ import annotations

import hashlib
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# local imports
from iam.models.users import AppUser
from iam.serializers.users import UserGetSerializer
from utils.paginator import CustomPagination


class UserListView(APIView):
    """
    GET: List all users
    allowed query params: search, is_active, sort_by
    allowed sort_by values: is_active, email, first_name, last_name
    cache key: iam:user_list:<hash of query parameters>
    """
    permission_classes = (IsAuthenticated,)
    permission_dict = {}

    def _generate_cache_key(self, request: Request) -> str:
        """Generate a unique cache key based on query parameters and pagination."""
        search = request.query_params.get("search", "")
        is_active = request.query_params.get("is_active", "")
        sort_by = request.query_params.get("sort_by") or "email"
        page = request.query_params.get("page", "1")
        length = request.query_params.get("length", "")

        # Create a string representation of all parameters
        cache_params = f"user_list:{search}:{is_active}:{sort_by}:{page}:{length}"
        # Hash to ensure cache key is valid and not too long
        cache_key = hashlib.md5(cache_params.encode()).hexdigest()
        return f"iam:user_list:{cache_key}"

    def get(self, request: Request) -> Response:
        # Generate cache key
        cache_key = self._generate_cache_key(request)

        # Try to get from cache (cache the response data dict, not the Response object)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        search = request.query_params.get("search")
        is_active = request.query_params.get("is_active", "")
        sort_by = request.query_params.get("sort_by") or "email"

        q_object = Q()

        # filter by search
        if search:
            q_object.add(Q(first_name__icontains=search), Q.OR)
            q_object.add(Q(last_name__icontains=search), Q.OR)
            q_object.add(Q(email__icontains=search), Q.OR)

        # filter by is_active
        if is_active:
            if str(is_active) not in ["1", "0"]:
                raise ValidationError(
                    {
                        "is_active": "Please provide a valid is_active, 1 for true and 0 for false"
                    }
                )
            q_object.add(Q(is_active=bool(int(is_active))), Q.AND)

        # Annotate the queryset with a full_name field for searching
        if sort_by:
            if sort_by.lstrip("-") not in [
                "is_active",
                "email",
                "first_name",
                "last_name",
            ]:
                raise ValidationError({"sort_by": "Please provide a valid sort value"})

        user_objs = AppUser.objects.filter(q_object).order_by(sort_by).distinct()

        paginator = CustomPagination()
        page = paginator.paginate_queryset(user_objs, request)
        user_list_serializer = UserGetSerializer(
            page, many=True, context={"action": "list"}
        )

        response = paginator.get_paginated_response(
            object_name="users",
            data=user_list_serializer.data,
        )

        # Cache the response data (dict) instead of the Response object
        # Extract the data from the Response object
        response_data = response.data
        cache.set(cache_key, response_data, settings.CACHE_TIMEOUT)

        return response