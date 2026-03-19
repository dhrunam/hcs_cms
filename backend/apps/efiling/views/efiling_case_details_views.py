from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from apps.core.models import EfilingActs, EfilingCaseDetails
from apps.efiling.serializers.efiling_acts_serializers import EfilingActsSerializer
from apps.efiling.serializers.efiling_case_details_serializers import EfilingCaseDetailsSerializer

# Sentinel to distinguish "key absent from PATCH payload" from an explicit null/empty list.
_MISSING = object()


def _normalize_acts(acts_payload, e_filing, e_filing_number):
    """Return a list of act dicts with e_filing / e_filing_number filled in from the parent
    when those fields are not explicitly supplied by the caller."""
    if not isinstance(acts_payload, list):
        acts_payload = [acts_payload]
    inherited_number = e_filing_number or getattr(e_filing, 'e_filing_number', None)
    result = []
    for item in acts_payload:
        if not isinstance(item, dict):
            result.append(item)
            continue
        item = dict(item)
        if e_filing is not None and 'e_filing' not in item:
            item['e_filing'] = e_filing.pk
        if inherited_number and 'e_filing_number' not in item:
            item['e_filing_number'] = inherited_number
        result.append(item)
    return result


class EfilingCaseDetailsListCreateView(ListCreateAPIView):
    queryset = EfilingCaseDetails.objects.all()
    serializer_class = EfilingCaseDetailsSerializer

    def post(self, request, *args, **kwargs):
        payload = request.data.copy()
        acts_payload = payload.pop('efiling_acts', payload.pop('acts', None))

        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)

        acts_serializer = None
        if acts_payload is not None:
            e_filing = serializer.validated_data.get('e_filing')
            e_filing_number = serializer.validated_data.get('e_filing_number')
            normalized = _normalize_acts(acts_payload, e_filing, e_filing_number)
            acts_serializer = EfilingActsSerializer(data=normalized, many=True)
            acts_serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            case_details = serializer.save()
            if acts_serializer is not None:
                acts_serializer.save()

        response_data = self.get_serializer(case_details).data
        if acts_serializer is not None:
            response_data['efiling_acts'] = acts_serializer.data

        headers = self.get_success_headers(response_data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        qs = EfilingCaseDetails.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        efiling_id = self.request.query_params.get('efiling_id')
        if efiling_id is not None:
            qs = qs.filter(efiling=efiling_id)
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs
    

    

    


class EfilingCaseDetailsRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = EfilingCaseDetails.objects.all()
    serializer_class = EfilingCaseDetailsSerializer

    def get_queryset(self):
        qs = EfilingCaseDetails.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs

    def put(self, request, *args, **kwargs):
        """Full replacement: update case details and replace ALL related acts atomically."""
        instance = self.get_object()
        payload = request.data.copy()
        acts_payload = payload.pop('efiling_acts', payload.pop('acts', None))

        serializer = self.get_serializer(instance, data=payload)
        serializer.is_valid(raise_exception=True)

        acts_serializer = None
        if acts_payload is not None:
            e_filing = serializer.validated_data.get('e_filing', instance.e_filing)
            e_filing_number = serializer.validated_data.get('e_filing_number', instance.e_filing_number)
            normalized = self._normalize_acts_payload(acts_payload, e_filing, e_filing_number)
            acts_serializer = EfilingActsSerializer(data=normalized, many=True)
            acts_serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            case_details = serializer.save()
            if acts_serializer is not None:
                EfilingActs.objects.filter(e_filing=case_details.e_filing).delete()
                acts_serializer.save()

        response_data = self.get_serializer(case_details).data
        if acts_serializer is not None:
            response_data['efiling_acts'] = acts_serializer.data
        return Response(response_data)

    def patch(self, request, *args, **kwargs):
        """Partial update: upsert acts by id, create acts without id,
        delete acts that belong to the same e_filing but are absent from the payload.
        If the efiling_acts key is omitted entirely, existing acts are left untouched."""
        instance = self.get_object()
        payload = request.data.copy()
        acts_payload = payload.pop('efiling_acts', payload.pop('acts', _MISSING))

        serializer = self.get_serializer(instance, data=payload, partial=True)
        serializer.is_valid(raise_exception=True)

        if acts_payload is _MISSING:
            case_details = serializer.save()
            return Response(self.get_serializer(case_details).data)

        e_filing = serializer.validated_data.get('e_filing', instance.e_filing)
        e_filing_number = serializer.validated_data.get('e_filing_number', instance.e_filing_number)
        normalized = self._normalize_acts_payload(acts_payload, e_filing, e_filing_number)

        to_update = [a for a in normalized if isinstance(a, dict) and 'id' in a]
        to_create = [a for a in normalized if not (isinstance(a, dict) and 'id' in a)]
        update_ids = {int(a['id']) for a in to_update}

        create_serializer = None
        if to_create:
            create_serializer = EfilingActsSerializer(data=to_create, many=True)
            create_serializer.is_valid(raise_exception=True)

        update_serializers = []
        for act_data in to_update:
            try:
                act_instance = EfilingActs.objects.get(pk=act_data['id'])
            except EfilingActs.DoesNotExist:
                raise ValidationError({'efiling_acts': f"Act with id {act_data['id']} does not exist."})
            act_ser = EfilingActsSerializer(act_instance, data=act_data, partial=True)
            act_ser.is_valid(raise_exception=True)
            update_serializers.append(act_ser)

        with transaction.atomic():
            case_details = serializer.save()
            EfilingActs.objects.filter(e_filing=e_filing).exclude(pk__in=update_ids).delete()
            for act_ser in update_serializers:
                act_ser.save()
            if create_serializer:
                create_serializer.save()

        all_acts = EfilingActs.objects.filter(e_filing=e_filing).order_by('id')
        response_data = self.get_serializer(case_details).data
        response_data['efiling_acts'] = EfilingActsSerializer(all_acts, many=True).data
        return Response(response_data)

    def _normalize_acts_payload(self, acts_payload, e_filing, e_filing_number):
        if not isinstance(acts_payload, list):
            acts_payload = [acts_payload]
        inherited_number = e_filing_number or getattr(e_filing, 'e_filing_number', None)
        result = []
        for item in acts_payload:
            if not isinstance(item, dict):
                result.append(item)
                continue
            item = dict(item)
            if e_filing is not None and 'e_filing' not in item:
                item['e_filing'] = e_filing.pk
            if inherited_number and 'e_filing_number' not in item:
                item['e_filing_number'] = inherited_number
            result.append(item)
        return result
