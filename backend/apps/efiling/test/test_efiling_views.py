from django.test import SimpleTestCase, TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory

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
        self.factory = APIRequestFactory()
        self.view = EfilingCaseDetailsListCreateView.as_view()
        self.e_filing = Efiling.objects.create(e_filing_number='ASK20240000001C202400001')

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
