from django.test import RequestFactory, SimpleTestCase, TestCase

from apps.accounts.models import User
from apps.core.audit_context import audit_user_context, get_current_user
from apps.core.middleware import AuditUserMiddleware
from apps.core.models import BaseModel
from apps.core.models import State


class BaseModelTest(SimpleTestCase):
    def test_base_model_is_abstract(self):
        self.assertTrue(BaseModel._meta.abstract)

    def test_base_model_common_fields_exist(self):
        expected = {"created_at", "updated_at", "created_by", "updated_by", "is_active"}
        self.assertTrue(expected.issubset({field.name for field in BaseModel._meta.fields}))


class BaseModelAuditBehaviorTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="audit-user",
            email="audit@example.com",
            password="password123",
        )
        self.other_user = User.objects.create_user(
            username="other-user",
            email="other@example.com",
            password="password123",
        )

    def test_create_sets_created_by_and_updated_by_from_context(self):
        with audit_user_context(self.user):
            instance = State.objects.create(state="Sikkim", est_code_src="SKH001")

        instance.refresh_from_db()
        self.assertEqual(instance.created_by, self.user)
        self.assertEqual(instance.updated_by, self.user)
        self.assertIsNotNone(instance.created_at)
        self.assertIsNotNone(instance.updated_at)

    def test_update_refreshes_updated_by_from_context(self):
        instance = State.objects.create(
            state="Sikkim",
            est_code_src="SKH001",
            created_by=self.other_user,
            updated_by=self.other_user,
        )

        with audit_user_context(self.user):
            instance.state = "Gangtok"
            instance.save()

        instance.refresh_from_db()
        self.assertEqual(instance.created_by, self.other_user)
        self.assertEqual(instance.updated_by, self.user)

    def test_update_fields_still_persists_updated_by(self):
        instance = State.objects.create(
            state="Sikkim",
            est_code_src="SKH001",
            created_by=self.other_user,
            updated_by=self.other_user,
        )

        with audit_user_context(self.user):
            instance.state = "Namchi"
            instance.save(update_fields=["state"])

        instance.refresh_from_db()
        self.assertEqual(instance.state, "Namchi")
        self.assertEqual(instance.updated_by, self.user)

    def test_explicit_updated_by_override_is_preserved(self):
        instance = State.objects.create(
            state="Sikkim",
            est_code_src="SKH001",
            created_by=self.user,
            updated_by=self.user,
        )

        with audit_user_context(self.user):
            instance.state = "Mangan"
            instance.updated_by = self.other_user
            instance.save()

        instance.refresh_from_db()
        self.assertEqual(instance.updated_by, self.other_user)

    def test_middleware_sets_and_clears_user_context(self):
        observed = {}

        def get_response(_request):
            observed["during_request"] = get_current_user()
            return "ok"

        middleware = AuditUserMiddleware(get_response)
        request = RequestFactory().get("/")
        request.user = self.user

        response = middleware(request)

        self.assertEqual(response, "ok")
        self.assertEqual(observed["during_request"], self.user)
        self.assertIsNone(get_current_user())
