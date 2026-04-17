from __future__ import annotations

from django.db import models


class OrderDetailsA(models.Model):
    """
    App-layer wrapper for legacy CIS `order_details_a`.
    Kept unmanaged; used by CMS steno workflows.
    """

    pk = models.CompositePrimaryKey("order_no", "cino")
    case_no = models.CharField(max_length=15, blank=True, null=True)
    order_no = models.SmallIntegerField()
    order_dt = models.DateField(blank=True, null=True)
    download = models.TextField()
    upload = models.TextField()
    doc_type = models.SmallIntegerField()
    ordloc_lang = models.TextField()
    judgedecree = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField()
    oldorder_dt = models.DateField(blank=True, null=True)
    userlogin = models.CharField(max_length=150, blank=True, null=True)
    jocode = models.CharField(max_length=150, blank=True, null=True)
    modify_flag = models.CharField(max_length=1, blank=True, null=True)
    disp_nature = models.SmallIntegerField()
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    court_no = models.IntegerField()
    cino = models.CharField(max_length=16)
    reportable_judgement = models.CharField(max_length=1, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    ia_no = models.CharField(max_length=12, blank=True, null=True)
    ia_case_type = models.IntegerField(blank=True, null=True)
    auther_judge = models.IntegerField(blank=True, null=True)
    comm_judge = models.IntegerField(blank=True, null=True)
    appeal_status = models.IntegerField(blank=True, null=True)
    headnote = models.TextField(blank=True, null=True)
    acts = models.TextField(blank=True, null=True)
    citation = models.TextField(blank=True, null=True)
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    desig_code = models.CharField(max_length=50, blank=True, null=True)
    nc_court = models.CharField(max_length=9, blank=True, null=True)
    nc_no = models.IntegerField(blank=True, null=True)
    nc_year = models.IntegerField(blank=True, null=True)
    nc = models.CharField(max_length=25, blank=True, null=True)
    benchtype = models.CharField(max_length=2, blank=True, null=True)
    judgment = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "order_details_a"
