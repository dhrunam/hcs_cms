from django.test import SimpleTestCase

from apps.core.models import ActT, Efiling, EfiliingActs


class EfiliingActsModelTest(SimpleTestCase):
    def test_db_table(self):
        self.assertEqual(EfiliingActs._meta.db_table, "e_filing_acts")

    def test_foreign_keys(self):
        self.assertEqual(EfiliingActs._meta.get_field("e_filing").related_model, Efiling)
        self.assertEqual(EfiliingActs._meta.get_field("act").related_model, ActT)
