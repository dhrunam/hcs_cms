from rest_framework.routers import DefaultRouter

from .views import CaseViewSet

app_name = "cases"

router = DefaultRouter()
router.register(r"", CaseViewSet, basename="case")

urlpatterns = router.urls
