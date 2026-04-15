"""JWT-adjacent auth endpoints: registration and email verification."""

from __future__ import annotations

import logging

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.email_verification import load_email_verification_token
from apps.accounts.models import User
from apps.accounts.registration_serializers import (
    AdvocateRegistrationSerializer,
    PartyRegistrationSerializer,
)
from apps.accounts.serializers import EmailVerifySerializer
from apps.accounts.throttling import AuthTokenThrottle, RegistrationThrottle

logger = logging.getLogger(__name__)


class PartyRegistrationView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegistrationThrottle]

    def post(self, request: Request) -> Response:
        ser = PartyRegistrationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user, verification_token = ser.create(ser.validated_data)
        payload = {
            "id": user.pk,
            "email": user.email,
            "detail": (
                "Registration received. Your account is inactive until an administrator verifies your "
                "identity documents; you will not be able to sign in until then."
            ),
            "requires_admin_activation": True,
        }
        if getattr(settings, "REGISTRATION_REQUIRE_EMAIL_VERIFICATION", False):
            payload["email_verification_required"] = True
            if settings.DEBUG and verification_token:
                payload["verification_token"] = verification_token
            logger.info("User %s registered; email verification required.", user.email)
        return Response(payload, status=status.HTTP_201_CREATED)


class AdvocateRegistrationView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegistrationThrottle]

    def post(self, request: Request) -> Response:
        ser = AdvocateRegistrationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user, verification_token = ser.create(ser.validated_data)
        payload = {
            "id": user.pk,
            "email": user.email,
            "detail": (
                "Registration received. Your account is inactive until an administrator verifies your "
                "identity documents; you will not be able to sign in until then."
            ),
            "requires_admin_activation": True,
        }
        if getattr(settings, "REGISTRATION_REQUIRE_EMAIL_VERIFICATION", False):
            payload["email_verification_required"] = True
            if settings.DEBUG and verification_token:
                payload["verification_token"] = verification_token
            logger.info("Advocate %s registered; email verification required.", user.email)
        return Response(payload, status=status.HTTP_201_CREATED)


class EmailVerifyView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthTokenThrottle]

    def post(self, request: Request) -> Response:
        ser = EmailVerifySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        token = ser.validated_data["token"]
        uid = load_email_verification_token(token)
        if uid is None:
            return Response(
                {"detail": "Invalid or expired verification token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.filter(pk=uid).first()
        if user is None:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        user.email_verified = True
        user.save(update_fields=["email_verified"])
        return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)
