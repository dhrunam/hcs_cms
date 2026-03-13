from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

# from .models import CISFilingNumber, CISDataLog
# from .serializers import CISFilingNumberSerializer, CISDataLogSerializer


# class CISFilingNumberViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     Read-only API for CIS filing numbers.
#     Only staff users can list and retrieve CIS filing number records.
#     """

#     queryset = CISFilingNumber.objects.all()
#     serializer_class = CISFilingNumberSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         """Staff users can view all; regular users cannot access CIS data."""
#         user = self.request.user
#         if user.is_staff:
#             return CISFilingNumber.objects.all()
#         return CISFilingNumber.objects.none()


# class CISDataLogViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     Read-only API for CIS data transaction logs.
#     Only staff and system administrators can view logs.
#     """

#     queryset = CISDataLog.objects.all()
#     serializer_class = CISDataLogSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         """Only staff users can view data logs."""
#         user = self.request.user
#         if user.is_staff:
#             return CISDataLog.objects.all()
#         return CISDataLog.objects.none()

#     @action(detail=False, methods=["get"], url_path="stats")
#     def stats(self, request):
#         """Return summary statistics of CIS data transactions."""
#         queryset = self.get_queryset()
#         total = queryset.count()
#         successful = queryset.filter(status=CISDataLog.Status.SUCCESS).count()
#         failed = queryset.filter(status=CISDataLog.Status.FAILED).count()
#         pending = queryset.filter(status=CISDataLog.Status.PENDING).count()

#         return Response(
#             {
#                 "total_transactions": total,
#                 "successful": successful,
#                 "failed": failed,
#                 "pending": pending,
#                 "success_rate": (successful / total * 100) if total > 0 else 0,
#             }
#         )
