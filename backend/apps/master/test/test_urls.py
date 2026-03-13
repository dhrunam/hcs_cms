from django.test import SimpleTestCase
from django.urls import resolve, reverse

from apps.master.views.act_t_views import ActTListView
from apps.master.views.case_type_t_views import CaseTypeTListView
from apps.master.views.court_views import CourtListView
from apps.master.views.district_views import DistrictListView
from apps.master.views.orgname_t_views import OrgnameTListView
from apps.master.views.orgtype_t_views import OrgtypeTListView
from apps.master.views.state_views import StateListView


class MasterUrlsTest(SimpleTestCase):
    def test_case_type_url(self):
        url = reverse("master:case-type-list")
        self.assertEqual(url, "/api/v1/master/case-types/")
        self.assertEqual(resolve(url).func.view_class, CaseTypeTListView)

    def test_state_url(self):
        url = reverse("master:state-list")
        self.assertEqual(url, "/api/v1/master/states/")
        self.assertEqual(resolve(url).func.view_class, StateListView)

    def test_district_url(self):
        url = reverse("master:district-list")
        self.assertEqual(url, "/api/v1/master/districts/")
        self.assertEqual(resolve(url).func.view_class, DistrictListView)

    def test_court_url(self):
        url = reverse("master:court-list")
        self.assertEqual(url, "/api/v1/master/courts/")
        self.assertEqual(resolve(url).func.view_class, CourtListView)

    def test_orgtype_url(self):
        url = reverse("master:org-type-list")
        self.assertEqual(url, "/api/v1/master/org-types/")
        self.assertEqual(resolve(url).func.view_class, OrgtypeTListView)

    def test_act_url(self):
        url = reverse("master:act-list")
        self.assertEqual(url, "/api/v1/master/acts/")
        self.assertEqual(resolve(url).func.view_class, ActTListView)

    def test_orgname_url(self):
        url = reverse("master:org-name-list")
        self.assertEqual(url, "/api/v1/master/org-names/")
        self.assertEqual(resolve(url).func.view_class, OrgnameTListView)
