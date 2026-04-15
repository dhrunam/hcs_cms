from django.contrib.auth.models import Group, Permission
from django.db.models import Count
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .models import User
from .permissions import IsStaffOrSuperAdminGroup, user_is_staff_or_superadmin_group
from .serializers import (
    AuthPermissionSerializer,
    RoleGroupSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """
    User accounts: admin CRUD; any authenticated user can access `me` and `logout`.
    Management list / active toggle: staff or SUPERADMIN group.
    """

    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("email", "first_name", "last_name", "username")
    ordering_fields = ("email", "date_joined", "id", "last_name", "first_name")
    ordering = ("email",)

    def get_permissions(self):
        if self.action in ("me", "logout"):
            return [IsAuthenticated()]
        if self.action in ("list", "retrieve", "set_active"):
            return [IsStaffOrSuperAdminGroup()]
        return [IsAdminUser()]

    def get_queryset(self):
        qs = User.objects.all().order_by("email")
        user = self.request.user
        if not user.is_authenticated:
            return qs.none()
        if user_is_staff_or_superadmin_group(user):
            return qs
        return qs.filter(pk=user.pk)

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

    @action(detail=True, methods=["patch"], url_path="active")
    def set_active(self, request: Request, pk=None) -> Response:
        """PATCH body: ``is_active`` or ``isActive`` (boolean) — enable or disable login."""
        user_obj = self.get_object()
        body = request.data
        val = body.get("is_active")
        if val is None and isinstance(body, dict) and "isActive" in body:
            val = body.get("isActive")
        if not isinstance(val, bool):
            return Response(
                {"detail": "Provide boolean is_active or isActive."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_obj.is_active = val
        user_obj.save(update_fields=["is_active"])
        return Response(UserSerializer(user_obj).data)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """List Django auth Groups (roles) for Super Admin management UI."""

    serializer_class = RoleGroupSerializer
    permission_classes = [IsStaffOrSuperAdminGroup]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("name",)
    ordering_fields = ("name", "id")
    ordering = ("name",)

    def get_queryset(self):
        return Group.objects.annotate(permission_count=Count("permissions", distinct=True))


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """List Django auth Permissions for Super Admin management UI."""

    serializer_class = AuthPermissionSerializer
    permission_classes = [IsStaffOrSuperAdminGroup]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("name", "codename")
    ordering_fields = ("name", "codename", "id")
    ordering_fields = ("name", "codename", "id")
    ordering = ("content_type__app_label", "content_type__model", "codename")

    def get_queryset(self):
        return Permission.objects.select_related("content_type")
