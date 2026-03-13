from django.urls import path

from apps.efiliing.views.efiling_views import EfilingListCreateView, EfilingRetrieveUpdateDestroyView

app_name = 'efiliing'

urlpatterns = [
    path('efilings/', EfilingListCreateView.as_view(), name='efiling-list-create'),
    path('efilings/<int:pk>/', EfilingRetrieveUpdateDestroyView.as_view(), name='efiling-detail'),
]

