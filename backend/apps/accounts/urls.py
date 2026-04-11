from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.auth_views import (
    AdvocateRegistrationView,
    EmailVerifyView,
    PartyRegistrationView,
)
from apps.accounts.jwt_views import (
    ThrottledTokenBlacklistView,
    ThrottledTokenObtainPairView,
    ThrottledTokenRefreshView,
    ThrottledTokenVerifyView,
)
from apps.accounts.views import UserViewSet

app_name = "accounts"

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("auth/token/", ThrottledTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "auth/token/refresh/",
        ThrottledTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "auth/token/verify/",
        ThrottledTokenVerifyView.as_view(),
        name="token_verify",
    ),
    path(
        "auth/token/blacklist/",
        ThrottledTokenBlacklistView.as_view(),
        name="token_blacklist",
    ),
    path(
        "auth/register/party/",
        PartyRegistrationView.as_view(),
        name="register_party",
    ),
    path(
        "auth/register/advocate/",
        AdvocateRegistrationView.as_view(),
        name="register_advocate",
    ),
    path(
        "auth/verify-email/",
        EmailVerifyView.as_view(),
        name="verify_email",
    ),
    path("", include(router.urls)),
]
