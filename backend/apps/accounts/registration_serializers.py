"""Serializers for party/advocate self-registration (multipart)."""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.accounts import roles as role_defs
from apps.accounts.models import RegistrationProfile, User
from apps.accounts.email_verification import make_email_verification_token
from apps.accounts.utils import generate_unique_username_from_email


class PartyRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone_number = serializers.CharField(max_length=20)
    date_of_birth = serializers.DateField()
    address = serializers.CharField()
    gender = serializers.ChoiceField(choices=RegistrationProfile.GENDER_CHOICES)
    photo = serializers.FileField(required=False, allow_null=True)

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email__iexact=value.strip()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.strip()

    def validate(self, attrs):
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        photo = validated_data.pop("photo", None)
        password = validated_data.pop("password")
        require_verify = getattr(
            settings, "REGISTRATION_REQUIRE_EMAIL_VERIFICATION", False
        )
        user = User(
            email=validated_data["email"],
            username=generate_unique_username_from_email(validated_data["email"]),
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone_number=validated_data["phone_number"],
            registration_type=role_defs.REG_PARTY,
            email_verified=not require_verify,
        )
        user.set_password(password)
        user.save()

        group, _ = Group.objects.get_or_create(name=role_defs.GROUP_PARTY_IN_PERSON)
        user.groups.add(group)

        RegistrationProfile.objects.create(
            user=user,
            date_of_birth=validated_data["date_of_birth"],
            address=validated_data["address"],
            gender=validated_data["gender"],
            photo=photo,
            bar_id="",
            bar_id_file=None,
            verification_status="",
        )

        verification_token = ""
        if require_verify:
            verification_token = make_email_verification_token(user.pk)

        return user, verification_token


class AdvocateRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone_number = serializers.CharField(max_length=20)
    date_of_birth = serializers.DateField()
    address = serializers.CharField()
    gender = serializers.ChoiceField(choices=RegistrationProfile.GENDER_CHOICES)
    photo = serializers.FileField(required=False, allow_null=True)
    bar_id = serializers.CharField(max_length=128)
    bar_id_file = serializers.FileField()

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email__iexact=value.strip()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.strip()

    def validate(self, attrs):
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        photo = validated_data.pop("photo", None)
        bar_id_file = validated_data.pop("bar_id_file")
        bar_id = validated_data.pop("bar_id")
        password = validated_data.pop("password")
        require_verify = getattr(
            settings, "REGISTRATION_REQUIRE_EMAIL_VERIFICATION", False
        )
        user = User(
            email=validated_data["email"],
            username=generate_unique_username_from_email(validated_data["email"]),
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone_number=validated_data["phone_number"],
            registration_type=role_defs.REG_ADVOCATE,
            email_verified=not require_verify,
        )
        user.set_password(password)
        user.save()

        group, _ = Group.objects.get_or_create(name=role_defs.GROUP_ADVOCATE)
        user.groups.add(group)

        RegistrationProfile.objects.create(
            user=user,
            date_of_birth=validated_data["date_of_birth"],
            address=validated_data["address"],
            gender=validated_data["gender"],
            photo=photo,
            bar_id=bar_id,
            bar_id_file=bar_id_file,
            verification_status=RegistrationProfile.VERIFICATION_PENDING,
        )

        verification_token = ""
        if require_verify:
            verification_token = make_email_verification_token(user.pk)

        return user, verification_token
