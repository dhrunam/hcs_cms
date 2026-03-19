from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.static import serve
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/accounts/', include('apps.accounts.urls', namespace='accounts')),
    # path('api/v1/cases/', include('apps.cases.urls', namespace='cases')),
    path('api/v1/cis/', include('apps.cis.urls', namespace='cis')),
    path('api/v1/efiling/', include('apps.efiling.urls', namespace='efiling')),
    path('api/v1/master/', include('apps.master.urls', namespace='master')),
    
]

if settings.DEBUG:
    urlpatterns += [
        path(
            "media/<path:path>",
            xframe_options_exempt(serve),
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
