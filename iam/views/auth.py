from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from iam.serializers.auth import EmailTokenObtainPairSerializer


class EmailTokenObtainPairView(APIView):
    """
    POST: Accept email + password, return access + refresh JWT tokens.
    """

    authentication_classes: list[Any] = []
    permission_classes: list[Any] = []

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = EmailTokenObtainPairSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)