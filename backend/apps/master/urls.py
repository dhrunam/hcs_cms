from django.urls import path

from apps.master.views.act_t_views import ActTListView
from apps.master.views.case_type_t_views import CaseTypeTListView
from apps.master.views.court_views import CourtListView
from apps.master.views.district_views import DistrictListView
from apps.master.views.orgname_t_views import OrgnameTListView
from apps.master.views.orgtype_t_views import OrgtypeTListView
from apps.master.views.state_views import StateListView

app_name = "master"

urlpatterns = [
    path("case-types/", CaseTypeTListView.as_view(), name="case-type-list"),
    path("states/", StateListView.as_view(), name="state-list"),
    path("districts/", DistrictListView.as_view(), name="district-list"),
    path("courts/", CourtListView.as_view(), name="court-list"),
    path("org-types/", OrgtypeTListView.as_view(), name="org-type-list"),
    path("acts/", ActTListView.as_view(), name="act-list"),
    path("org-names/", OrgnameTListView.as_view(), name="org-name-list"),
]
