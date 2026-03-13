from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('api/v1/cases/', include('apps.cases.urls', namespace='cases')),
    path('api/v1/cis/', include('apps.cis.urls', namespace='cis')),
    path('api/v1/efiling/', include('apps.efiling.urls', namespace='efiling')),
    path('api/v1/master/', include('apps.master.urls', namespace='master')),
]
