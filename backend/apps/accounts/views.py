from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoints for User accounts.

    Development CRUD endpoints for User accounts.
    """

    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all().order_by("email")

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request: Request) -> Response:
        """Return the currently authenticated user's profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="logout",
        permission_classes=[AllowAny],
    )
    def logout(self, request: Request) -> Response:
        """
        Invalidate the Django session server-side and clear session/CSRF cookies.

        This must be called alongside the OAuth token revocation on the frontend
        so that the sessionid cookie cannot be reused after logout.
        """
        request.session.flush()
        response = Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)
        # Attributes must exactly match those used when the cookie was originally set;
        # any mismatch causes browsers to silently ignore the deletion.
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
