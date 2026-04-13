from __future__ import annotations

from rest_framework import serializers

from .models import RegistrationProfile, User


class RegistrationProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationProfile
        fields = [
            "date_of_birth",
            "address",
            "gender",
            "photo",
            "bar_id",
            "bar_id_file",
            "verification_status",
        ]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the custom User model."""

    full_name = serializers.SerializerMethodField(read_only=True)
    groups = serializers.SerializerMethodField(read_only=True)
    registration_profile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "department",
            "designation",
            "registration_type",
            "email_verified",
            "groups",
            "registration_profile",
            "is_active",
            "is_staff",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "date_joined",
            "registration_type",
            "email_verified",
            "groups",
            "registration_profile",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
        }

    def get_full_name(self, obj: User) -> str:
        return obj.get_full_name()

    def get_groups(self, obj: User) -> list[str]:
        return list(obj.groups.order_by("name").values_list("name", flat=True))

    def get_registration_profile(self, obj: User) -> dict | None:
        try:
            p = obj.registration_profile
        except RegistrationProfile.DoesNotExist:
            return None
        return RegistrationProfileSerializer(p).data

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password", None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save(update_fields=["password"])
        return user

    def update(self, instance: User, validated_data: dict) -> User:
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save(update_fields=["password"])
        return user


class EmailVerifySerializer(serializers.Serializer):
    token = serializers.CharField()
