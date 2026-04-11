from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    User accounts: admin CRUD; any authenticated user can access `me` and `logout`.
    """

    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ("me", "logout"):
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        qs = User.objects.all().order_by("email")
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return qs
        if user.is_authenticated:
            return qs.filter(pk=user.pk)
        return qs.none()

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request: Request) -> Response:
        """Return the currently authenticated user's profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="logout",
        permission_classes=[IsAuthenticated],
    )
    def logout(self, request: Request) -> Response:
        """
        Clear Django session cookies (legacy hybrid clients).

        JWT clients should also POST the refresh token to
        `/api/v1/accounts/auth/token/blacklist/` (see SimpleJWT).
        """
        request.session.flush()
        response = Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)
        response.delete_cookie(
            "sessionid",
            path="/",
            domain=None,
            samesite="Lax",
        )
        response.delete_cookie(
            "csrftoken",
            path="/",
            domain=None,
            samesite="Lax",
        )
        return response
