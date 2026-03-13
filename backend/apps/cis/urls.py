from rest_framework.routers import DefaultRouter

# from .views import CISFilingNumberViewSet, CISDataLogViewSet

app_name = "cis"

router = DefaultRouter()
# router.register(r"filing-numbers", CISFilingNumberViewSet, basename="filing-number")
# router.register(r"data-logs", CISDataLogViewSet, basename="data-log")

urlpatterns = router.urls
