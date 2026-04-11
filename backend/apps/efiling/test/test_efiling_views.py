from unittest.mock import patch

from django.contrib.auth.models import Group
from django.test import SimpleTestCase, TestCase
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APIRequestFactory

from apps.accounts.models import User
from apps.core.audit_context import set_current_user
from apps.core.models import Efiling, EfilingCaseDetails, EfilingLitigant, EfilingActs
from apps.efiling.serializers.efiling_acts_serializers import EfilingActsSerializer
from apps.efiling.serializers.efiling_case_details_serializers import EfilingCaseDetailsSerializer
from apps.efiling.serializers.efiling_litigant_serializers import EfilingLitigantSerializer
from apps.efiling.serializers.efiling_serializers import EfilingSerializer
from apps.efiling.serializers.ia_serializers import IASerializer
from apps.efiling.views.efiling_acts_views import EfilingActsListCreateView, EfilingActsRetrieveUpdateDestroyView
from apps.efiling.views.efiling_case_details_views import EfilingCaseDetailsListCreateView, EfilingCaseDetailsRetrieveUpdateDestroyView
from apps.efiling.views.efiling_litigant_views import EfilingLitigantListCreateView, EfilingLitigantRetrieveUpdateDestroyView
from apps.efiling.views.efiling_views import EfilingListCreateView, EfilingRetrieveUpdateDestroyView
from apps.efiling.views.ia_views import IAListCreateView, IARetrieveUpdateDestroyView
from apps.core.models import IA


class EfilingListCreateViewTest(SimpleTestCase):
    def test_serializer_class(self):
        self.assertEqual(EfilingListCreateView.serializer_class, EfilingSerializer)

    def test_queryset_model(self):
        self.assertEqual(EfilingListCreateView.queryset.model, Efiling)


class EfilingRetrieveUpdateDestroyViewTest(SimpleTestCase):
    def test_serializer_class(self):
        self.assertEqual(EfilingRetrieveUpdateDestroyView.serializer_class, EfilingSerializer)

    def test_queryset_model(self):
        self.assertEqual(EfilingRetrieveUpdateDestroyView.queryset.model, Efiling)


class EfilingLitigantViewsTest(SimpleTestCase):
    def test_list_create_view(self):
        self.assertEqual(EfilingLitigantListCreateView.serializer_class, EfilingLitigantSerializer)
        self.assertEqual(EfilingLitigantListCreateView.queryset.model, EfilingLitigant)

    def test_detail_view(self):
        self.assertEqual(EfilingLitigantRetrieveUpdateDestroyView.serializer_class, EfilingLitigantSerializer)
        self.assertEqual(EfilingLitigantRetrieveUpdateDestroyView.queryset.model, EfilingLitigant)


class EfilingCaseDetailsViewsTest(SimpleTestCase):
    def test_list_create_view(self):
        self.assertEqual(EfilingCaseDetailsListCreateView.serializer_class, EfilingCaseDetailsSerializer)
        self.assertEqual(EfilingCaseDetailsListCreateView.queryset.model, EfilingCaseDetails)

    def test_detail_view(self):
        self.assertEqual(EfilingCaseDetailsRetrieveUpdateDestroyView.serializer_class, EfilingCaseDetailsSerializer)
        self.assertEqual(EfilingCaseDetailsRetrieveUpdateDestroyView.queryset.model, EfilingCaseDetails)


class EfilingActsViewsTest(SimpleTestCase):
    def test_list_create_view(self):
        self.assertEqual(EfilingActsListCreateView.serializer_class, EfilingActsSerializer)
        self.assertEqual(EfilingActsListCreateView.queryset.model, EfilingActs)

    def test_detail_view(self):
        self.assertEqual(EfilingActsRetrieveUpdateDestroyView.serializer_class, EfilingActsSerializer)
        self.assertEqual(EfilingActsRetrieveUpdateDestroyView.queryset.model, EfilingActs)


class IAViewsTest(SimpleTestCase):
    def test_list_create_view(self):
        self.assertEqual(IAListCreateView.serializer_class, IASerializer)
        self.assertEqual(IAListCreateView.queryset.model, IA)

    def test_detail_view(self):
        self.assertEqual(IARetrieveUpdateDestroyView.serializer_class, IASerializer)
        self.assertEqual(IARetrieveUpdateDestroyView.queryset.model, IA)


class EfilingCaseDetailsNestedActsPostTest(TestCase):
    def setUp(self):
        set_current_user(None)
        self.factory = APIRequestFactory()
        self.view = EfilingCaseDetailsListCreateView.as_view()
        self.e_filing = Efiling.objects.create(e_filing_number='ASK20240000001C202400001')

    def tearDown(self):
        set_current_user(None)

    def test_post_creates_case_details_and_multiple_acts(self):
        payload = {
            'e_filing': self.e_filing.pk,
            'e_filing_number': self.e_filing.e_filing_number,
            'cause_of_action': 'Test cause of action',
            'efiling_acts': [
                {
                    'section': 'Section 1',
                    'sub_section': 'Sub 1',
                    'description': 'First act description',
                },
                {
                    'section': 'Section 2',
                    'sub_section': 'Sub 2',
                    'description': 'Second act description',
                },
            ],
        }

        request = self.factory.post('/api/v1/efiling/efiling-case-details/', payload, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EfilingCaseDetails.objects.count(), 1)
        self.assertEqual(EfilingActs.objects.count(), 2)
        self.assertEqual(response.data['efiling_acts'][0]['e_filing'], self.e_filing.pk)
        self.assertEqual(response.data['efiling_acts'][0]['e_filing_number'], self.e_filing.e_filing_number)
        self.assertEqual(response.data['efiling_acts'][1]['section'], 'Section 2')

    def test_post_rolls_back_case_details_when_acts_payload_is_invalid(self):
        payload = {
            'e_filing': self.e_filing.pk,
            'e_filing_number': self.e_filing.e_filing_number,
            'cause_of_action': 'Rollback test',
            'efiling_acts': [
                {
                    'section': 'Section 1',
                    'description': 'Valid act',
                },
                'invalid-act-payload',
            ],
        }

        request = self.factory.post('/api/v1/efiling/efiling-case-details/', payload, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(EfilingCaseDetails.objects.count(), 0)
        self.assertEqual(EfilingActs.objects.count(), 0)


class EfilingCaseDetailsNestedActsUpdateTest(TestCase):
    def setUp(self):
        set_current_user(None)
        self.factory = APIRequestFactory()
        self.detail_view = EfilingCaseDetailsRetrieveUpdateDestroyView.as_view()
        self.e_filing = Efiling.objects.create(e_filing_number='ASK20240000002C202400002')
        self.case_details = EfilingCaseDetails.objects.create(
            e_filing=self.e_filing,
            e_filing_number=self.e_filing.e_filing_number,
            cause_of_action='Initial cause',
        )
        self.act1 = EfilingActs.objects.create(
            e_filing=self.e_filing,
            e_filing_number=self.e_filing.e_filing_number,
            section='Old Section 1',
            description='Old act 1',
        )
        self.act2 = EfilingActs.objects.create(
            e_filing=self.e_filing,
            e_filing_number=self.e_filing.e_filing_number,
            section='Old Section 2',
            description='Old act 2',
        )

    def tearDown(self):
        set_current_user(None)

    def test_put_replaces_all_existing_acts(self):
        payload = {
            'e_filing': self.e_filing.pk,
            'e_filing_number': self.e_filing.e_filing_number,
            'cause_of_action': 'Updated by PUT',
            'efiling_acts': [
                {
                    'section': 'New Section A',
                    'description': 'New act A',
                },
                {
                    'section': 'New Section B',
                    'description': 'New act B',
                },
            ],
        }

        request = self.factory.put(
            f'/api/v1/efiling/efiling-case-details/{self.case_details.pk}/',
            payload,
            format='json',
        )
        response = self.detail_view(request, pk=self.case_details.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.case_details.refresh_from_db()
        self.assertEqual(self.case_details.cause_of_action, 'Updated by PUT')
        self.assertEqual(EfilingActs.objects.filter(e_filing=self.e_filing).count(), 2)
        sections = list(EfilingActs.objects.filter(e_filing=self.e_filing).order_by('id').values_list('section', flat=True))
        self.assertEqual(sections, ['New Section A', 'New Section B'])

    def test_put_rolls_back_when_new_acts_payload_invalid(self):
        payload = {
            'e_filing': self.e_filing.pk,
            'e_filing_number': self.e_filing.e_filing_number,
            'cause_of_action': 'Should not persist',
            'efiling_acts': ['invalid-payload'],
        }

        request = self.factory.put(
            f'/api/v1/efiling/efiling-case-details/{self.case_details.pk}/',
            payload,
            format='json',
        )
        response = self.detail_view(request, pk=self.case_details.pk)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.case_details.refresh_from_db()
        self.assertEqual(self.case_details.cause_of_action, 'Initial cause')
        self.assertEqual(EfilingActs.objects.filter(e_filing=self.e_filing).count(), 2)

    def test_patch_upserts_and_deletes_missing_acts(self):
        payload = {
            'cause_of_action': 'Updated by PATCH',
            'efiling_acts': [
                {
                    'id': self.act1.id,
                    'section': 'Updated Section 1',
                },
                {
                    'section': 'Brand New Section',
                    'description': 'Brand new act',
                },
            ],
        }

        request = self.factory.patch(
            f'/api/v1/efiling/efiling-case-details/{self.case_details.pk}/',
            payload,
            format='json',
        )
        response = self.detail_view(request, pk=self.case_details.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.case_details.refresh_from_db()
        self.assertEqual(self.case_details.cause_of_action, 'Updated by PATCH')
        acts = EfilingActs.objects.filter(e_filing=self.e_filing).order_by('id')
        self.assertEqual(acts.count(), 2)
        self.assertTrue(acts.filter(id=self.act1.id, section='Updated Section 1').exists())
        self.assertFalse(acts.filter(id=self.act2.id).exists())
        self.assertTrue(acts.exclude(id=self.act1.id).filter(section='Brand New Section').exists())

    def test_patch_without_acts_keeps_existing_acts(self):
        payload = {'cause_of_action': 'Patch only case details'}
        request = self.factory.patch(
            f'/api/v1/efiling/efiling-case-details/{self.case_details.pk}/',
            payload,
            format='json',
        )
        response = self.detail_view(request, pk=self.case_details.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.case_details.refresh_from_db()
        self.assertEqual(self.case_details.cause_of_action, 'Patch only case details')
        self.assertEqual(EfilingActs.objects.filter(e_filing=self.e_filing).count(), 2)


class EfilingAuditIntegrationTest(TestCase):
    def setUp(self):
        set_current_user(None)
        self.factory = APIRequestFactory()
        self.list_view = EfilingListCreateView.as_view()
        self.detail_view = EfilingRetrieveUpdateDestroyView.as_view()
        self.advocate_group, _ = Group.objects.get_or_create(name='API_ADVOCATE')
        self.scrutiny_group, _ = Group.objects.get_or_create(name='API_SCRUTINY_OFFICER')
        self.user = User.objects.create_user(
            username='api-audit-user',
            email='api-audit@example.com',
            password='password123',
        )
        self.user.groups.add(self.advocate_group)
        self.other_user = User.objects.create_user(
            username='api-other-user',
            email='api-other@example.com',
            password='password123',
        )
        self.other_user.groups.add(self.advocate_group)

    def tearDown(self):
        set_current_user(None)

    def test_authenticated_create_sets_created_by_and_updated_by(self):
        payload = {
            'bench': 'Bench A',
            'petitioner_name': 'Petitioner',
            'is_draft': True,
        }

        request = self.factory.post(
            '/api/v1/efiling/efilings/',
            payload,
            format='json',
            HTTP_AUTHORIZATION='Bearer test-token',
        )

        with self._mock_authentication(self.user):
            response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        filing = Efiling.objects.get(pk=response.data['id'])
        self.assertEqual(filing.created_by, self.user)
        self.assertEqual(filing.updated_by, self.user)

    def test_authenticated_patch_updates_updated_by(self):
        filing = Efiling.objects.create(
            bench='Bench A',
            petitioner_name='Petitioner',
            created_by=self.user,
            updated_by=self.other_user,
        )
        payload = {
            'bench': 'Bench B',
        }

        request = self.factory.patch(
            f'/api/v1/efiling/efilings/{filing.pk}/',
            payload,
            format='json',
            HTTP_AUTHORIZATION='Bearer test-token',
        )

        with self._mock_authentication(self.user):
            response = self.detail_view(request, pk=filing.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filing.refresh_from_db()
        self.assertEqual(filing.created_by, self.user)
        self.assertEqual(filing.updated_by, self.user)

    def test_normal_user_list_only_includes_owned_filings(self):
        own_filing = Efiling.objects.create(
            bench='Bench A',
            petitioner_name='Own Petitioner',
            created_by=self.user,
            updated_by=self.user,
        )
        Efiling.objects.create(
            bench='Bench B',
            petitioner_name='Other Petitioner',
            created_by=self.other_user,
            updated_by=self.other_user,
        )

        request = self.factory.get(
            '/api/v1/efiling/efilings/',
            HTTP_AUTHORIZATION='Bearer test-token',
        )

        with self._mock_authentication(self.user):
            response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {item['id'] for item in response.data.get('results', [])}
        self.assertEqual(returned_ids, {own_filing.id})

    def test_normal_user_cannot_retrieve_other_users_filing(self):
        other_filing = Efiling.objects.create(
            bench='Bench B',
            petitioner_name='Other Petitioner',
            created_by=self.other_user,
            updated_by=self.other_user,
        )

        request = self.factory.get(
            f'/api/v1/efiling/efilings/{other_filing.pk}/',
            HTTP_AUTHORIZATION='Bearer test-token',
        )

        with self._mock_authentication(self.user):
            response = self.detail_view(request, pk=other_filing.pk)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_scrutiny_officer_can_list_all_filings(self):
        self.user.groups.remove(self.advocate_group)
        self.user.groups.add(self.scrutiny_group)
        own_filing = Efiling.objects.create(
            bench='Bench A',
            petitioner_name='Own Petitioner',
            created_by=self.user,
            updated_by=self.user,
        )
        other_filing = Efiling.objects.create(
            bench='Bench B',
            petitioner_name='Other Petitioner',
            created_by=self.other_user,
            updated_by=self.other_user,
        )

        request = self.factory.get(
            '/api/v1/efiling/efilings/',
            HTTP_AUTHORIZATION='Bearer test-token',
        )

        with self._mock_authentication(self.user):
            response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {item['id'] for item in response.data.get('results', [])}
        self.assertEqual(returned_ids, {own_filing.id, other_filing.id})

    def _mock_authentication(self, user):
        return patch(
            "apps.core.authentication.AuditAwareJWTAuthentication.authenticate",
            return_value=(user, None),
        )


class EfilingAdvocateScopeTest(TestCase):
    """List/detail e-filing APIs scope by created_by for advocate-only users."""

    def setUp(self):
        set_current_user(None)
        self.factory = APIRequestFactory()
        self.list_view = EfilingListCreateView.as_view()
        self.detail_view = EfilingRetrieveUpdateDestroyView.as_view()
        self.advocate_a = User.objects.create_user(
            username='scope-adv-a',
            email='scope-a@example.com',
            password='password123',
        )
        self.advocate_b = User.objects.create_user(
            username='scope-adv-b',
            email='scope-b@example.com',
            password='password123',
        )
        advocate_group, _ = Group.objects.get_or_create(name='API_ADVOCATE')
        self.advocate_a.groups.add(advocate_group)
        self.advocate_b.groups.add(advocate_group)

        self.filing_a = Efiling.objects.create(
            e_filing_number='SCOPE20240000001C202400001',
            petitioner_name='Petitioner A',
            created_by=self.advocate_a,
            updated_by=self.advocate_a,
        )
        self.filing_b = Efiling.objects.create(
            e_filing_number='SCOPE20240000002C202400002',
            petitioner_name='Petitioner B',
            created_by=self.advocate_b,
            updated_by=self.advocate_b,
        )

    def tearDown(self):
        set_current_user(None)

    def _mock_authentication(self, user):
        return patch(
            "apps.core.authentication.AuditAwareJWTAuthentication.authenticate",
            return_value=(user, None),
        )

    def test_advocate_list_only_own_filings(self):
        request = self.factory.get(
            '/api/v1/efiling/efilings/',
            HTTP_AUTHORIZATION='Bearer test-token',
        )
        with self._mock_authentication(self.advocate_a):
            response = self.list_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [row['id'] for row in response.data['results']]
        self.assertEqual(ids, [self.filing_a.id])

    def test_advocate_cannot_retrieve_others_filing(self):
        request = self.factory.get(
            f'/api/v1/efiling/efilings/{self.filing_b.pk}/',
            HTTP_AUTHORIZATION='Bearer test-token',
        )
        with self._mock_authentication(self.advocate_a):
            response = self.detail_view(request, pk=self.filing_b.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_scrutiny_officer_sees_all_filings(self):
        scrutiny_user = User.objects.create_user(
            username='scope-scrutiny',
            email='scope-scrutiny@example.com',
            password='password123',
        )
        scrutiny_group, _ = Group.objects.get_or_create(name='SCRUTINY_OFFICER')
        scrutiny_user.groups.add(scrutiny_group)

        request = self.factory.get(
            '/api/v1/efiling/efilings/',
            HTTP_AUTHORIZATION='Bearer test-token',
        )
        with self._mock_authentication(scrutiny_user):
            response = self.list_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {row['id'] for row in response.data['results']}
        self.assertEqual(ids, {self.filing_a.id, self.filing_b.id})

    def test_superuser_sees_all_filings(self):
        superuser = User.objects.create_superuser(
            username='scope-su',
            email='scope-su@example.com',
            password='password123',
        )
        request = self.factory.get(
            '/api/v1/efiling/efilings/',
            HTTP_AUTHORIZATION='Bearer test-token',
        )
        with self._mock_authentication(superuser):
            response = self.list_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {row['id'] for row in response.data['results']}
        self.assertEqual(ids, {self.filing_a.id, self.filing_b.id})
