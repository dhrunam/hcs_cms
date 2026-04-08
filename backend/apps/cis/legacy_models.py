# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AccountPurpose(models.Model):
    accpurpose_code = models.SmallIntegerField(primary_key=True)
    accpurpose_name = models.CharField(max_length=100, blank=True, null=True)
    laccpurpose_name = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'account_purpose'


class AccountPurposeOther(models.Model):
    accpurpose_code = models.SmallIntegerField(primary_key=True)
    accpurpose_name = models.CharField(max_length=100, blank=True, null=True)
    laccpurpose_name = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'account_purpose_other'


class AccusedJail(models.Model):
    pk = models.CompositePrimaryKey('cnr', 'srno')
    case_number = models.CharField(max_length=15)
    filing_number = models.CharField(max_length=15)
    cnr = models.CharField(max_length=16)
    party_type = models.IntegerField()
    party_id = models.IntegerField()
    party_name = models.CharField(max_length=255)
    gender = models.IntegerField()
    age = models.IntegerField()
    date_of_conviction = models.DateField()
    type_imprisonment = models.TextField(blank=True, null=True)  # This field type is a guess.
    years = models.IntegerField()
    months = models.IntegerField()
    date_sent_jail = models.DateField()
    district_id = models.IntegerField()
    prison_id = models.IntegerField()
    date_bail = models.DateField()
    srno = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'accused_jail'


class AccusedRemand(models.Model):
    pk = models.CompositePrimaryKey('crno', 'srno')
    crno = models.CharField(max_length=17)
    police_stn_code = models.IntegerField()
    fir_no = models.CharField(max_length=15, blank=True, null=True)
    fir_year = models.SmallIntegerField()
    fir_type_code = models.SmallIntegerField()
    accused_id = models.SmallIntegerField()
    accused_name = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=1, blank=True, null=True)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    onvc = models.TextField(blank=True, null=True)  # This field type is a guess.
    remand_date = models.DateField(blank=True, null=True)
    srno = models.SmallIntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    laccused_name = models.CharField(max_length=100, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    pretrialshort_order = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'accused_remand'


class ActT(models.Model):
    actcode = models.BigIntegerField(primary_key=True)
    actname = models.CharField(max_length=250, blank=True, null=True)
    lactname = models.CharField(max_length=100, blank=True, null=True)
    acttype = models.TextField()  # This field type is a guess.
    display = models.TextField()  # This field type is a guess.
    national_code = models.CharField(max_length=15, blank=True, null=True)
    shortact = models.CharField(max_length=50, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'act_t'


class ActsectionT(models.Model):
    act_code = models.BigIntegerField()
    actsection_code = models.CharField(max_length=50, blank=True, null=True)
    act_section = models.CharField(max_length=250, blank=True, null=True)
    lact_section = models.CharField(max_length=250, blank=True, null=True)
    max_imp = models.SmallIntegerField()
    off_type = models.SmallIntegerField()
    display = models.TextField()  # This field type is a guess.
    national_code = models.CharField(max_length=11, blank=True, null=True)
    chapter = models.CharField(max_length=4, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'actsection_t'


class AdditionalInfo(models.Model):
    pk = models.CompositePrimaryKey('cino', 'record_no')
    case_no = models.CharField(max_length=15)
    record_no = models.SmallIntegerField()
    search1 = models.CharField(max_length=50, blank=True, null=True)
    search2 = models.CharField(max_length=50, blank=True, null=True)
    search3 = models.CharField(max_length=50, blank=True, null=True)
    search4 = models.CharField(max_length=50, blank=True, null=True)
    search5 = models.CharField(max_length=50, blank=True, null=True)
    search6 = models.CharField(max_length=50, blank=True, null=True)
    search7 = models.CharField(max_length=50, blank=True, null=True)
    search8 = models.CharField(max_length=50, blank=True, null=True)
    search9 = models.CharField(max_length=50, blank=True, null=True)
    search10 = models.CharField(max_length=50, blank=True, null=True)
    search11 = models.CharField(max_length=50, blank=True, null=True)
    search12 = models.CharField(max_length=50, blank=True, null=True)
    search13 = models.CharField(max_length=50, blank=True, null=True)
    search14 = models.CharField(max_length=50, blank=True, null=True)
    search15 = models.CharField(max_length=50, blank=True, null=True)
    search16 = models.CharField(max_length=10, blank=True, null=True)
    search17 = models.CharField(max_length=10, blank=True, null=True)
    search18 = models.CharField(max_length=10, blank=True, null=True)
    search19 = models.CharField(max_length=10, blank=True, null=True)
    search20 = models.CharField(max_length=10, blank=True, null=True)
    search21 = models.CharField(max_length=10, blank=True, null=True)
    search22 = models.CharField(max_length=10, blank=True, null=True)
    lsearch1 = models.CharField(max_length=150, blank=True, null=True)
    lsearch2 = models.CharField(max_length=150, blank=True, null=True)
    lsearch3 = models.CharField(max_length=150, blank=True, null=True)
    lsearch4 = models.CharField(max_length=150, blank=True, null=True)
    lsearch5 = models.CharField(max_length=150, blank=True, null=True)
    lsearch6 = models.CharField(max_length=150, blank=True, null=True)
    lsearch7 = models.CharField(max_length=67, blank=True, null=True)
    lsearch8 = models.CharField(max_length=150, blank=True, null=True)
    lsearch9 = models.CharField(max_length=150, blank=True, null=True)
    lsearch10 = models.CharField(max_length=150, blank=True, null=True)
    lsearch11 = models.CharField(max_length=150, blank=True, null=True)
    lsearch12 = models.CharField(max_length=150, blank=True, null=True)
    lsearch13 = models.CharField(max_length=150, blank=True, null=True)
    lsearch14 = models.CharField(max_length=150, blank=True, null=True)
    lsearch15 = models.CharField(max_length=150, blank=True, null=True)
    lsearch16 = models.CharField(max_length=10, blank=True, null=True)
    lsearch17 = models.CharField(max_length=10, blank=True, null=True)
    lsearch18 = models.CharField(max_length=10, blank=True, null=True)
    lsearch19 = models.CharField(max_length=10, blank=True, null=True)
    lsearch20 = models.CharField(max_length=10, blank=True, null=True)
    search29 = models.CharField(max_length=150, blank=True, null=True)
    search30 = models.CharField(max_length=150, blank=True, null=True)
    lsearch29 = models.CharField(max_length=150, blank=True, null=True)
    lsearch30 = models.CharField(max_length=150, blank=True, null=True)
    cino = models.CharField(max_length=16)
    roster_subject = models.CharField(max_length=255, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'additional_info'


class AdiarySummary(models.Model):
    pk = models.CompositePrimaryKey('court_no', 'date_listing', 'type_flag')
    court_no = models.IntegerField()
    date_listing = models.DateField()
    no_cases_listed = models.SmallIntegerField()
    no_witnesses_ex = models.SmallIntegerField()
    no_ia_disposed = models.SmallIntegerField()
    no_cases_disposed = models.SmallIntegerField()
    contested = models.SmallIntegerField()
    non_contested = models.SmallIntegerField()
    no_mediation = models.SmallIntegerField()
    no_lokadalath = models.SmallIntegerField()
    no_arbitration = models.SmallIntegerField()
    no_conciliation = models.SmallIntegerField()
    no_exibits_marked = models.SmallIntegerField()
    no_mos_marked = models.SmallIntegerField()
    no_casesmediation = models.SmallIntegerField()
    no_arbcase = models.SmallIntegerField()
    no_lokadalatcase = models.SmallIntegerField()
    no_adrpurcase = models.SmallIntegerField()
    type_flag = models.SmallIntegerField()
    case_typecode = models.TextField(blank=True, null=True)
    case_typevalue = models.TextField(blank=True, null=True)
    no_heardcases = models.SmallIntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    cases_for_evidence = models.IntegerField(blank=True, null=True)
    evidence_recorded = models.IntegerField(blank=True, null=True)
    attendance = models.CharField(max_length=1, blank=True, null=True)
    review = models.IntegerField(blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    field1 = models.TextField(blank=True, null=True)
    field2 = models.TextField(blank=True, null=True)
    no_pleadcases_listed = models.SmallIntegerField()
    no_regularcases_listed = models.SmallIntegerField()
    no_pleadcases_disposed = models.SmallIntegerField()
    no_regularcases_disposed = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'adiary_summary'


class AdjcodeT(models.Model):
    adjcode = models.SmallIntegerField(primary_key=True)
    adjname = models.CharField(max_length=50, blank=True, null=True)
    ladjname = models.CharField(max_length=50, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    national_code = models.BigIntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'adjcode_t'


class AdminDesig(models.Model):
    desig_code = models.IntegerField(primary_key=True)
    admin_desig = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'admin_desig'


class AdminTasks(models.Model):
    task_code = models.IntegerField(primary_key=True)
    task = models.CharField(max_length=100, blank=True, null=True)
    days = models.IntegerField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'admin_tasks'


class AdminUnits(models.Model):
    pk = models.CompositePrimaryKey('court_no', 'unit_sr_no')
    court_no = models.IntegerField()
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    purpose = models.SmallIntegerField()
    units = models.DecimalField(max_digits=17, decimal_places=2)
    display = models.TextField()  # This field type is a guess.
    unit_sr_no = models.SmallIntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'admin_units'


class AdminWorkT(models.Model):
    work_code = models.SmallIntegerField(primary_key=True)
    work_name = models.CharField(max_length=200, blank=True, null=True)
    lwork_name = models.CharField(max_length=200, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'admin_work_t'


class AdvLeave(models.Model):
    pk = models.CompositePrimaryKey('adv_code', 'leave_date', 'to_date')
    adv_code = models.BigIntegerField()
    adv_reg = models.CharField(max_length=20, blank=True, null=True)
    adv_name = models.CharField(max_length=100, blank=True, null=True)
    leave_id = models.SmallIntegerField()
    leave_date = models.DateField()
    to_date = models.DateField()
    remark = models.CharField(max_length=255, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'adv_leave'


class AdvanceList(models.Model):
    pk = models.CompositePrimaryKey('sr_no', 'advlist_date')
    sr_no = models.IntegerField()
    cino = models.CharField(max_length=16)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    ia_no = models.CharField(max_length=12, blank=True, null=True)
    clink_cino = models.CharField(max_length=16, blank=True, null=True)
    advlist_date = models.DateField()
    advlist_type = models.SmallIntegerField(blank=True, null=True)
    search_case = models.SmallIntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    purpose_code = models.IntegerField()
    subpurpose_id = models.IntegerField()
    remark = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'advance_list'


class AdvocateDesig(models.Model):
    pk = models.CompositePrimaryKey('adv_desig_code', 'ori_adv_code', 'adv_desig_from_date')
    adv_desig_code = models.BigIntegerField()
    ori_adv_code = models.BigIntegerField()
    ori_adv_bar = models.CharField(max_length=20, blank=True, null=True)
    adv_desig_from_date = models.DateField()
    adv_desig_to_date = models.DateField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'advocate_desig'


class AdvocateLog(models.Model):
    pk = models.CompositePrimaryKey('cino', 'party_no', 'type', 'old_adv_name')
    cino = models.CharField(max_length=16)
    party_no = models.IntegerField()
    type = models.SmallIntegerField()
    old_adv_name = models.CharField(max_length=100)
    old_adv_cd = models.BigIntegerField()
    new_adv_name = models.CharField(max_length=100, blank=True, null=True)
    new_adv_cd = models.BigIntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    extra_adv_srno = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'advocate_log'


class AdvocateT(models.Model):
    adv_code = models.BigIntegerField(primary_key=True)
    adv_name = models.CharField(max_length=100, blank=True, null=True)
    ladv_name = models.CharField(max_length=100, blank=True, null=True)
    adv_reg = models.CharField(max_length=20, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    address = models.TextField(blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    email = models.CharField(max_length=254, blank=True, null=True)
    adv_sex = models.CharField(max_length=1, blank=True, null=True)
    adv_mobile = models.CharField(max_length=15, blank=True, null=True)
    adv_phone = models.CharField(max_length=15, blank=True, null=True)
    adv_phone1 = models.CharField(max_length=15, blank=True, null=True)
    off_add = models.TextField(blank=True, null=True)
    loff_add = models.TextField(blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    adv_fax = models.CharField(max_length=15, blank=True, null=True)
    date_birth = models.DateField(blank=True, null=True)
    debarred = models.TextField()  # This field type is a guess.
    pincode = models.IntegerField(blank=True, null=True)
    dist_code_res = models.SmallIntegerField()
    taluka_code_res = models.SmallIntegerField()
    village_code_res = models.IntegerField()
    village1_code_res = models.IntegerField()
    village2_code_res = models.IntegerField()
    town_code_res = models.IntegerField()
    ward_code_res = models.IntegerField()
    status = models.IntegerField()
    frequent = models.TextField()  # This field type is a guess.
    adv_full_name = models.CharField(max_length=100, blank=True, null=True)
    adv_seniority = models.IntegerField(blank=True, null=True)
    adv_gender = models.CharField(max_length=1, blank=True, null=True)
    state_id_res = models.IntegerField(blank=True, null=True)
    uid = models.BigIntegerField(blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    advocate_type = models.SmallIntegerField()
    ori_adv_code = models.BigIntegerField(blank=True, null=True)
    ori_adv_bar = models.CharField(max_length=20, blank=True, null=True)
    adv_desig_from_date = models.DateField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'advocate_t'


class AlertT(models.Model):
    alert_eng = models.CharField(max_length=255)
    display = models.CharField()
    alert_code = models.IntegerField(primary_key=True)
    alert_lan = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'alert_t'


class Allocation(models.Model):
    pk = models.CompositePrimaryKey('court_no', 'case_type')
    court_no = models.IntegerField()
    case_type = models.SmallIntegerField()
    total = models.SmallIntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'allocation'


class AlteraddressT(models.Model):
    case_no = models.CharField(max_length=15, blank=True, null=True)
    pet_res = models.CharField(max_length=99, blank=True, null=True)
    alt_address = models.TextField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alteraddress_t'


class ApplType(models.Model):
    appl_id = models.SmallIntegerField(primary_key=True)
    appl_type = models.CharField(max_length=100, blank=True, null=True)
    lappl_type = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'appl_type'


class AreaLocation(models.Model):
    pk = models.CompositePrimaryKey('area_location_id', 'area_id')
    area_location_id = models.BigIntegerField()
    area_id = models.BigIntegerField()
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'area_location'


class AsmRecordroom(models.Model):
    pk = models.CompositePrimaryKey('cino', 'sr_no')
    cino = models.CharField(max_length=16)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    sr_no = models.IntegerField()
    no_of_pages = models.SmallIntegerField()
    bundle_date = models.DateField(blank=True, null=True)
    bundle_no = models.CharField(max_length=25, blank=True, null=True)
    rack_no = models.CharField(max_length=25, blank=True, null=True)
    self_no = models.CharField(max_length=25, blank=True, null=True)
    file_no = models.CharField(max_length=25, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)
    userlogin = models.CharField(max_length=150, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'asm_recordroom'


class AsmTdisposedcases(models.Model):
    disposedcaseid = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=40, blank=True, null=True)
    no = models.SmallIntegerField(blank=True, null=True)
    year = models.SmallIntegerField(blank=True, null=True)
    old_case_no = models.CharField(max_length=50)
    ordertype = models.CharField(max_length=100, blank=True, null=True)
    noofpages = models.SmallIntegerField(blank=True, null=True)
    bundledate = models.DateTimeField(blank=True, null=True)
    bundleno = models.CharField(max_length=15, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    rcaseno = models.CharField(max_length=50, blank=True, null=True)
    userid = models.SmallIntegerField(blank=True, null=True)
    rackno = models.CharField(max_length=20, blank=True, null=True)
    orderdate = models.DateTimeField(blank=True, null=True)
    selfno = models.CharField(max_length=5, blank=True, null=True)
    fileno = models.CharField(max_length=10, blank=True, null=True)
    sectionid = models.IntegerField()
    petitioner = models.CharField(max_length=200, blank=True, null=True)
    respondent = models.CharField(max_length=200, blank=True, null=True)
    updatedate = models.DateTimeField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'asm_tdisposedcases'


class BacklogWork(models.Model):
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    work_timedate = models.DateTimeField(blank=True, null=True)
    user_id = models.CharField(max_length=3, blank=True, null=True)
    module_code = models.SmallIntegerField()
    work_attempted = models.SmallIntegerField()
    data_correct = models.SmallIntegerField()
    remarks = models.CharField(max_length=255, blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'backlog_work'


class BailiffAreaT(models.Model):
    bailiff_id = models.SmallIntegerField(primary_key=True)
    area_id = models.CharField(max_length=100, blank=True, null=True)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bailiff_area_t'


class BaliffT(models.Model):
    bailiffid = models.SmallIntegerField(primary_key=True)
    bailiffname = models.CharField(max_length=100, blank=True, null=True)
    lbailiffname = models.CharField(max_length=100, blank=True, null=True)
    bail_sex = models.CharField(max_length=1, blank=True, null=True)
    date_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    off_add = models.TextField(blank=True, null=True)
    loff_add = models.TextField(blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    email = models.CharField(max_length=254, blank=True, null=True)
    bail_mobile = models.CharField(max_length=15, blank=True, null=True)
    bail_phone = models.CharField(max_length=15, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    qualification = models.CharField(max_length=100, blank=True, null=True)
    mother_tongue = models.CharField(max_length=30, blank=True, null=True)
    caste = models.SmallIntegerField()
    dtmdate_of_entry_service = models.DateField(blank=True, null=True)
    address_area = models.TextField(blank=True, null=True)
    bail_gender = models.CharField(max_length=1, blank=True, null=True)
    baliff_nationalcode = models.CharField(max_length=20, blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'baliff_t'


class BankMaster(models.Model):
    bank_code = models.SmallIntegerField(primary_key=True)
    bank_desc = models.CharField(max_length=150, blank=True, null=True)
    lbank_desc = models.CharField(max_length=150, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    bank_ifsccode = models.CharField(max_length=15, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bank_master'


class BenchType(models.Model):
    bench_type_code = models.IntegerField(primary_key=True)
    bench_type_name = models.CharField(max_length=250, blank=True, null=True)
    no_of_judges = models.IntegerField(blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    bench_abbreviation = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bench_type'


class BoardSerial(models.Model):
    pk = models.CompositePrimaryKey('sr_no', 'court_no', 'ctype', 'cino')
    sr_no = models.IntegerField()
    cino = models.CharField(max_length=16)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    next_date = models.DateField(blank=True, null=True)
    court_no = models.IntegerField()
    ctype = models.CharField(max_length=1)
    originalsr_no = models.IntegerField(blank=True, null=True)
    case_remark = models.TextField(blank=True, null=True)
    causelist_type = models.IntegerField(blank=True, null=True)
    causelist_period = models.CharField(max_length=1, blank=True, null=True)
    list_from_date = models.DateField(blank=True, null=True)
    list_to_date = models.DateField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'board_serial'


class BoardType(models.Model):
    idno = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'board_type'


class Bunchdir(models.Model):
    bunch_code = models.IntegerField(primary_key=True)
    bunch_desc = models.CharField(max_length=150, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bunchdir'


class ButtonsT(models.Model):
    buttoneng = models.CharField(max_length=255, blank=True, null=True)
    buttonname = models.CharField(max_length=255, blank=True, null=True)
    display = models.CharField()
    buttonid = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'buttons_t'


class CallOrignals(models.Model):
    pk = models.CompositePrimaryKey('register_no', 'ca_no', 'ca_date')
    register_no = models.SmallIntegerField()
    ca_no = models.IntegerField()
    ca_date = models.DateField()
    section = models.SmallIntegerField()
    recv_rtn_date = models.DateField(blank=True, null=True)
    flag = models.CharField(max_length=1)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    call_date = models.DateField(blank=True, null=True)
    remark = models.CharField(max_length=100, blank=True, null=True)
    todays_date = models.DateTimeField()
    cino = models.CharField(max_length=16, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'call_orignals'


class CallRecordsT(models.Model):
    pk = models.CompositePrimaryKey('case_no', 'rec_id')
    case_no = models.CharField(max_length=15)
    rec_id = models.SmallIntegerField()
    rec_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_call = models.DateField(blank=True, null=True)
    date_of_returnable = models.DateField(blank=True, null=True)
    date_of_returned = models.DateField(blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'call_records_t'


class CancelRegistration(models.Model):
    pk = models.CompositePrimaryKey('cino', 'case_no')
    cino = models.CharField(max_length=16)
    case_no = models.CharField(max_length=15)
    dt_regis = models.DateField(blank=True, null=True)
    cancel_date = models.DateField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cancel_registration'


class CaseConversion(models.Model):
    pk = models.CompositePrimaryKey('cino', 'sr_no')
    cino = models.CharField(max_length=16)
    oldcase_no = models.CharField(max_length=15, blank=True, null=True)
    newcase_no = models.CharField(max_length=15, blank=True, null=True)
    finalcase_no = models.CharField(max_length=15, blank=True, null=True)
    oldregcase_type = models.SmallIntegerField(blank=True, null=True)
    oldreg_no = models.IntegerField(blank=True, null=True)
    oldreg_year = models.SmallIntegerField(blank=True, null=True)
    newregcase_type = models.SmallIntegerField(blank=True, null=True)
    newreg_no = models.IntegerField(blank=True, null=True)
    newreg_year = models.SmallIntegerField(blank=True, null=True)
    sr_no = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'case_conversion'


class CaseFetchLogicT(models.Model):
    logic_id = models.IntegerField(primary_key=True)
    logic_desc = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    add_textbox_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    orignal_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    ia_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'case_fetch_logic_t'


class CaseInfo(models.Model):
    cino = models.CharField(primary_key=True, max_length=16)
    relief_offense = models.TextField(blank=True, null=True)
    lrelief_offence = models.TextField(blank=True, null=True)
    causeofaction = models.TextField(blank=True, null=True)
    lcauseofaction = models.TextField(blank=True, null=True)
    case_state_code = models.SmallIntegerField(blank=True, null=True)
    case_dist_code = models.SmallIntegerField(blank=True, null=True)
    offense_date = models.DateField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    case_taluka_code = models.SmallIntegerField(blank=True, null=True)
    case_village_code = models.IntegerField()
    prayer_cd = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'case_info'


class CaseInfoA(models.Model):
    cino = models.CharField(primary_key=True, max_length=16)
    relief_offense = models.TextField(blank=True, null=True)
    lrelief_offence = models.TextField(blank=True, null=True)
    causeofaction = models.TextField(blank=True, null=True)
    lcauseofaction = models.TextField(blank=True, null=True)
    case_state_code = models.SmallIntegerField(blank=True, null=True)
    case_dist_code = models.SmallIntegerField(blank=True, null=True)
    offense_date = models.DateField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    case_taluka_code = models.SmallIntegerField(blank=True, null=True)
    case_village_code = models.IntegerField()
    prayer_cd = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'case_info_a'


class CaseNote(models.Model):
    pk = models.CompositePrimaryKey('cino', 'srno')
    cino = models.CharField(max_length=16)
    ia_no = models.CharField(max_length=12, blank=True, null=True)
    board_remark = models.TextField(blank=True, null=True)
    purpose_code = models.SmallIntegerField(blank=True, null=True)
    my_note = models.CharField(max_length=25, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    srno = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'case_note'


class CaseTypeT(models.Model):
    case_type = models.SmallIntegerField(primary_key=True)
    type_name = models.CharField(max_length=50, blank=True, null=True)
    ltype_name = models.CharField(max_length=50, blank=True, null=True)
    full_form = models.CharField(max_length=100, blank=True, null=True)
    lfull_form = models.CharField(max_length=100, blank=True, null=True)
    type_flag = models.TextField()  # This field type is a guess.
    filing_no = models.IntegerField()
    filing_year = models.SmallIntegerField()
    reg_no = models.IntegerField()
    reg_year = models.SmallIntegerField()
    display = models.TextField()  # This field type is a guess.
    petitioner = models.CharField(max_length=99, blank=True, null=True)
    respondent = models.CharField(max_length=99, blank=True, null=True)
    lpetitioner = models.CharField(max_length=99, blank=True, null=True)
    lrespondent = models.CharField(max_length=99, blank=True, null=True)
    res_disp = models.SmallIntegerField()
    case_priority = models.SmallIntegerField()
    national_code = models.BigIntegerField()
    macp = models.TextField()  # This field type is a guess.
    stage_id = models.TextField(blank=True, null=True)
    matter_type = models.IntegerField(blank=True, null=True)
    cavreg_no = models.IntegerField()
    cavreg_year = models.SmallIntegerField()
    direct_reg = models.TextField()  # This field type is a guess.
    cavfil_no = models.IntegerField()
    cavfil_year = models.SmallIntegerField()
    ia_filing_no = models.IntegerField()
    ia_filing_year = models.SmallIntegerField()
    ia_reg_no = models.IntegerField()
    ia_reg_year = models.SmallIntegerField()
    tag_courts = models.CharField(max_length=1000, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    reasonable_dispose = models.TextField(blank=True, null=True)
    hideparty = models.CharField(max_length=1)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'case_type_t'


class CasetransferT(models.Model):
    case_no = models.CharField(max_length=15, blank=True, null=True)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    court_no = models.IntegerField(blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'casetransfer_t'


class CasetypelabelT(models.Model):
    case_type = models.IntegerField(primary_key=True)
    search1 = models.CharField(max_length=150, blank=True, null=True)
    search2 = models.CharField(max_length=150, blank=True, null=True)
    search3 = models.CharField(max_length=150, blank=True, null=True)
    search4 = models.CharField(max_length=150, blank=True, null=True)
    search5 = models.CharField(max_length=150, blank=True, null=True)
    search6 = models.CharField(max_length=150, blank=True, null=True)
    search7 = models.CharField(max_length=150, blank=True, null=True)
    search8 = models.CharField(max_length=150, blank=True, null=True)
    search9 = models.CharField(max_length=150, blank=True, null=True)
    search10 = models.CharField(max_length=150, blank=True, null=True)
    search11 = models.CharField(max_length=150, blank=True, null=True)
    search12 = models.CharField(max_length=150, blank=True, null=True)
    search13 = models.CharField(max_length=150, blank=True, null=True)
    search14 = models.CharField(max_length=150, blank=True, null=True)
    search15 = models.CharField(max_length=150, blank=True, null=True)
    search16 = models.CharField(max_length=150, blank=True, null=True)
    search17 = models.CharField(max_length=150, blank=True, null=True)
    search18 = models.CharField(max_length=150, blank=True, null=True)
    search19 = models.CharField(max_length=150, blank=True, null=True)
    search20 = models.CharField(max_length=150, blank=True, null=True)
    search21 = models.CharField(max_length=150, blank=True, null=True)
    search22 = models.CharField(max_length=150, blank=True, null=True)
    search23 = models.CharField(max_length=150, blank=True, null=True)
    search24 = models.CharField(max_length=150, blank=True, null=True)
    search25 = models.CharField(max_length=150, blank=True, null=True)
    search26 = models.CharField(max_length=150, blank=True, null=True)
    search27 = models.CharField(max_length=150, blank=True, null=True)
    search28 = models.CharField(max_length=150, blank=True, null=True)
    search1mar = models.CharField(max_length=150, blank=True, null=True)
    search2mar = models.CharField(max_length=150, blank=True, null=True)
    search3mar = models.CharField(max_length=150, blank=True, null=True)
    search4mar = models.CharField(max_length=150, blank=True, null=True)
    search5mar = models.CharField(max_length=150, blank=True, null=True)
    search6mar = models.CharField(max_length=150, blank=True, null=True)
    search7mar = models.CharField(max_length=150, blank=True, null=True)
    search8mar = models.CharField(max_length=150, blank=True, null=True)
    search9mar = models.CharField(max_length=150, blank=True, null=True)
    search10mar = models.CharField(max_length=150, blank=True, null=True)
    search11mar = models.CharField(max_length=150, blank=True, null=True)
    search12mar = models.CharField(max_length=150, blank=True, null=True)
    search13mar = models.CharField(max_length=150, blank=True, null=True)
    search14mar = models.CharField(max_length=150, blank=True, null=True)
    search15mar = models.CharField(max_length=150, blank=True, null=True)
    search16mar = models.CharField(max_length=150, blank=True, null=True)
    search17mar = models.CharField(max_length=150, blank=True, null=True)
    search18mar = models.CharField(max_length=150, blank=True, null=True)
    search19mar = models.CharField(max_length=150, blank=True, null=True)
    search20mar = models.CharField(max_length=150, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    search29 = models.CharField(max_length=150, blank=True, null=True)
    search30 = models.CharField(max_length=150, blank=True, null=True)
    search29mar = models.CharField(max_length=150, blank=True, null=True)
    search30mar = models.CharField(max_length=150, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'casetypelabel_t'


class CasteT(models.Model):
    pk = models.CompositePrimaryKey('caste_code', 'religion')
    caste_code = models.SmallIntegerField()
    religion = models.SmallIntegerField()
    caste_name = models.CharField(max_length=100, blank=True, null=True)
    lcaste_name = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    national_code = models.BigIntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'caste_t'


class CauseList(models.Model):
    pk = models.CompositePrimaryKey('cino', 'causelist_type', 'causelist_date', 'for_bench_id', 'causelist_sr_no', 'unique_no')
    sr_no = models.IntegerField()
    cino = models.CharField(max_length=16)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    next_date = models.DateField(blank=True, null=True)
    court_no = models.IntegerField()
    ctype = models.CharField(max_length=1)
    originalsr_no = models.IntegerField(blank=True, null=True)
    case_remark = models.TextField(blank=True, null=True)
    causelist_type = models.IntegerField()
    causelist_period = models.CharField(max_length=1, blank=True, null=True)
    list_from_date = models.DateField(blank=True, null=True)
    list_to_date = models.DateField(blank=True, null=True)
    causelist_date = models.DateField()
    for_bench_id = models.IntegerField()
    purpose_cd = models.IntegerField(blank=True, null=True)
    reg_dt = models.DateField(blank=True, null=True)
    filing_dt = models.DateField(blank=True, null=True)
    section_id = models.IntegerField(blank=True, null=True)
    on_filing = models.TextField(blank=True, null=True)  # This field type is a guess.
    clink_code = models.CharField(max_length=15, blank=True, null=True)
    civilt_court_no = models.IntegerField()
    civilt_date_next_list = models.DateField(blank=True, null=True)
    civilt_purpose_next = models.BigIntegerField()
    civilt_sr_no = models.IntegerField(blank=True, null=True)
    civilt_causelist_type = models.IntegerField(blank=True, null=True)
    elimination = models.TextField(blank=True, null=True)  # This field type is a guess.
    causelist_sr_no = models.IntegerField()
    cause_list_eliminate = models.TextField(blank=True, null=True)  # This field type is a guess.
    ia_no = models.CharField(max_length=12, blank=True, null=True)
    ia_next_date = models.DateField(blank=True, null=True)
    ia_flag = models.CharField(max_length=1, blank=True, null=True)
    unique_no = models.IntegerField()
    search_case = models.SmallIntegerField(blank=True, null=True)
    initial_status = models.CharField(max_length=1, blank=True, null=True)
    final_status = models.CharField(max_length=1, blank=True, null=True)
    cause_case_type = models.SmallIntegerField(blank=True, null=True)
    cause_reg_no = models.IntegerField(blank=True, null=True)
    cause_reg_year = models.SmallIntegerField(blank=True, null=True)
    takenonboard = models.CharField(max_length=2, blank=True, null=True)
    oldbenchid = models.IntegerField(blank=True, null=True)
    newbenchid = models.IntegerField(blank=True, null=True)
    olink_code = models.CharField(max_length=15, blank=True, null=True)
    ia_case_type = models.IntegerField(blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    bunch_code = models.IntegerField(blank=True, null=True)
    purpose_priority = models.SmallIntegerField()
    short_order = models.CharField(max_length=50, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    prev_short_order = models.CharField(max_length=50, blank=True, null=True)
    subpurpose_id = models.BigIntegerField()
    subpurpose_priority = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'cause_list'


class CauseListA(models.Model):
    pk = models.CompositePrimaryKey('cino', 'causelist_type', 'causelist_date', 'for_bench_id', 'causelist_sr_no', 'unique_no')
    sr_no = models.IntegerField()
    cino = models.CharField(max_length=16)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    next_date = models.DateField(blank=True, null=True)
    court_no = models.IntegerField()
    ctype = models.CharField(max_length=1)
    originalsr_no = models.IntegerField(blank=True, null=True)
    case_remark = models.TextField(blank=True, null=True)
    causelist_type = models.IntegerField()
    causelist_period = models.CharField(max_length=1, blank=True, null=True)
    list_from_date = models.DateField(blank=True, null=True)
    list_to_date = models.DateField(blank=True, null=True)
    causelist_date = models.DateField()
    for_bench_id = models.IntegerField()
    purpose_cd = models.IntegerField(blank=True, null=True)
    reg_dt = models.DateField(blank=True, null=True)
    filing_dt = models.DateField(blank=True, null=True)
    section_id = models.IntegerField(blank=True, null=True)
    on_filing = models.TextField(blank=True, null=True)  # This field type is a guess.
    clink_code = models.CharField(max_length=15, blank=True, null=True)
    civilt_court_no = models.IntegerField()
    civilt_date_next_list = models.DateField(blank=True, null=True)
    civilt_purpose_next = models.BigIntegerField()
    civilt_sr_no = models.IntegerField(blank=True, null=True)
    civilt_causelist_type = models.IntegerField(blank=True, null=True)
    elimination = models.TextField(blank=True, null=True)  # This field type is a guess.
    causelist_sr_no = models.IntegerField()
    cause_list_eliminate = models.TextField(blank=True, null=True)  # This field type is a guess.
    ia_no = models.CharField(max_length=12, blank=True, null=True)
    ia_next_date = models.DateField(blank=True, null=True)
    ia_flag = models.CharField(max_length=1, blank=True, null=True)
    unique_no = models.IntegerField()
    search_case = models.SmallIntegerField(blank=True, null=True)
    initial_status = models.CharField(max_length=1, blank=True, null=True)
    final_status = models.CharField(max_length=1, blank=True, null=True)
    cause_case_type = models.SmallIntegerField(blank=True, null=True)
    cause_reg_no = models.IntegerField(blank=True, null=True)
    cause_reg_year = models.SmallIntegerField(blank=True, null=True)
    takenonboard = models.CharField(max_length=2, blank=True, null=True)
    oldbenchid = models.IntegerField(blank=True, null=True)
    newbenchid = models.IntegerField(blank=True, null=True)
    olink_code = models.CharField(max_length=15, blank=True, null=True)
    ia_case_type = models.IntegerField(blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    bunch_code = models.IntegerField(blank=True, null=True)
    purpose_priority = models.SmallIntegerField()
    short_order = models.CharField(max_length=50, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    prev_short_order = models.CharField(max_length=50, blank=True, null=True)
    subpurpose_id = models.BigIntegerField()
    subpurpose_priority = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'cause_list_a'


class CauseListPeriod(models.Model):
    cause_list_type_id = models.IntegerField(primary_key=True)
    cause_list_type = models.CharField(max_length=99, blank=True, null=True)
    period = models.CharField(max_length=1, blank=True, null=True)
    showindailyproc = models.CharField(max_length=1, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    days = models.IntegerField(blank=True, null=True)
    taken_board = models.CharField(max_length=1, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cause_list_period'


class CauselistLog(models.Model):
    link_id = models.IntegerField()
    bench_id = models.IntegerField(blank=True, null=True)
    causelist_date = models.DateField(blank=True, null=True)
    causelist_type = models.IntegerField(blank=True, null=True)
    cino = models.CharField(max_length=16)
    ia_no = models.CharField(max_length=12, blank=True, null=True)
    sr_no = models.BigIntegerField(blank=True, null=True)
    event = models.CharField(max_length=25, blank=True, null=True)
    uname = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.CharField(max_length=20, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    serial_no = models.AutoField(primary_key=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'causelist_log'


class CauselistTitle(models.Model):
    pk = models.CompositePrimaryKey('causelist_id', 'causelist_date', 'for_bench_id', 'cause_list_status', 'causelist_sr_no')
    bench_id = models.IntegerField(blank=True, null=True)
    c_date = models.DateField(blank=True, null=True)
    cheader = models.TextField(blank=True, null=True)
    cfooter = models.TextField(blank=True, null=True)
    causelist_id = models.IntegerField()
    causelist_date = models.DateField()
    wheader = models.TextField(blank=True, null=True)
    wfooter = models.TextField(blank=True, null=True)
    published = models.TextField(blank=True, null=True)  # This field type is a guess.
    published_date = models.DateField(blank=True, null=True)
    archive = models.CharField(max_length=1, blank=True, null=True)
    published_ip = models.CharField(max_length=99, blank=True, null=True)
    published_user = models.CharField(max_length=99, blank=True, null=True)
    for_bench_id = models.IntegerField()
    c_order = models.IntegerField(blank=True, null=True)
    cause_list_status = models.CharField(max_length=1)
    elimination_remark = models.TextField(blank=True, null=True)
    causelist_sr_no = models.IntegerField()
    filename = models.TextField(blank=True, null=True)
    causelist_time = models.TimeField(blank=True, null=True)
    room_no = models.CharField(max_length=20, blank=True, null=True)
    search_case = models.SmallIntegerField(blank=True, null=True)
    court_id = models.CharField(max_length=15, blank=True, null=True)
    roaster_desc = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    cases_count = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'causelist_title'


class CavObjectionHistory(models.Model):
    pk = models.CompositePrimaryKey('cino', 'srno')
    caveat_no = models.CharField(max_length=15, blank=True, null=True)
    caveatfil_no = models.CharField(max_length=15, blank=True, null=True)
    objection = models.TextField(blank=True, null=True)
    objdescription = models.TextField(blank=True, null=True)
    lobjection = models.TextField(blank=True, null=True)
    obj_redate = models.DateField(blank=True, null=True)
    objreturn_dt = models.DateField(blank=True, null=True)
    objreceipt_dt = models.DateField(blank=True, null=True)
    objprepare_dt = models.DateField(blank=True, null=True)
    cino = models.CharField(max_length=16)
    srno = models.IntegerField()
    filcase_type = models.SmallIntegerField()
    regcase_type = models.SmallIntegerField()
    refile_date = models.DateTimeField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cav_objection_history'


class CavObjectionT(models.Model):
    objcode = models.SmallIntegerField(primary_key=True)
    objtype = models.TextField(blank=True, null=True)
    lobjtype = models.TextField(blank=True, null=True)
    casetype_flag = models.SmallIntegerField()
    bool_type = models.SmallIntegerField()
    display = models.TextField()  # This field type is a guess.
    case_type = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cav_objection_t'


class CaveatExtraAdvT(models.Model):
    caveat_no = models.CharField(max_length=15, blank=True, null=True)
    caveatfil_no = models.CharField(max_length=15, blank=True, null=True)
    pet_res = models.CharField(max_length=99, blank=True, null=True)
    lpet_res = models.CharField(max_length=99, blank=True, null=True)
    type = models.SmallIntegerField()
    adv_name = models.CharField(max_length=500, blank=True, null=True)
    ladv_name = models.CharField(max_length=100, blank=True, null=True)
    adv_code = models.BigIntegerField()
    party_no = models.SmallIntegerField()
    sr_no = models.SmallIntegerField(blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'caveat_extra_adv_t'


class CaveatT(models.Model):
    slno = models.BigIntegerField()
    slyear = models.SmallIntegerField(blank=True, null=True)
    caveat_no = models.CharField(max_length=15, blank=True, null=True)
    orgname = models.BigIntegerField(blank=True, null=True)
    ref_case_no = models.CharField(max_length=16, blank=True, null=True)
    petname = models.CharField(max_length=100, blank=True, null=True)
    lpetname = models.CharField(max_length=100, blank=True, null=True)
    resname = models.CharField(max_length=100, blank=True, null=True)
    resorgname = models.BigIntegerField()
    lresname = models.CharField(max_length=100, blank=True, null=True)
    dt_filing = models.DateField(blank=True, null=True)
    court_filed = models.SmallIntegerField()
    dt_court = models.DateField(blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    lsubject = models.CharField(max_length=150, blank=True, null=True)
    filing_case = models.SmallIntegerField()
    low_case_no = models.CharField(max_length=15, blank=True, null=True)
    ldec_date = models.DateField(blank=True, null=True)
    ljud_name = models.CharField(max_length=100, blank=True, null=True)
    pet_father_name = models.CharField(max_length=100, blank=True, null=True)
    lpet_father_name = models.CharField(max_length=100, blank=True, null=True)
    pet_relation_flag = models.CharField(max_length=2, blank=True, null=True)
    pet_adv = models.CharField(max_length=100, blank=True, null=True)
    lpet_adv = models.CharField(max_length=100, blank=True, null=True)
    res_father_name = models.CharField(max_length=100, blank=True, null=True)
    lres_father_name = models.CharField(max_length=100, blank=True, null=True)
    res_relation_flag = models.CharField(max_length=2, blank=True, null=True)
    lower_court_code = models.SmallIntegerField(blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    caveatfil_no = models.CharField(unique=True, max_length=15, blank=True, null=True)
    time_of_filing = models.TimeField(blank=True, null=True)
    extrarefcase_no = models.CharField(max_length=1000, blank=True, null=True)
    oldcaveat_no = models.CharField(max_length=15, blank=True, null=True)
    pet_adv_cd = models.BigIntegerField()
    pet_email = models.CharField(max_length=254, blank=True, null=True)
    pet_mobile = models.CharField(max_length=15, blank=True, null=True)
    res_email = models.CharField(max_length=254, blank=True, null=True)
    res_mobile = models.CharField(max_length=15, blank=True, null=True)
    dt_reg = models.DateField(blank=True, null=True)
    time_of_reg = models.TimeField(blank=True, null=True)
    reasonfilingdate = models.CharField(max_length=255, blank=True, null=True)
    reasonregisdate = models.CharField(max_length=255, blank=True, null=True)
    lcc_applied_date = models.DateField(blank=True, null=True)
    lcc_received_date = models.DateField(blank=True, null=True)
    res_adv_cd = models.BigIntegerField()
    res_adv_name = models.CharField(max_length=100, blank=True, null=True)
    lres_adv_name = models.CharField(max_length=100, blank=True, null=True)
    res_occupation = models.CharField(max_length=30, blank=True, null=True)
    pet_occupation = models.CharField(max_length=30, blank=True, null=True)
    pet_inperson = models.CharField(max_length=1, blank=True, null=True)
    res_inperson = models.CharField(max_length=1, blank=True, null=True)
    lower_judge_name = models.CharField(max_length=100, blank=True, null=True)
    lowerjocode = models.CharField(max_length=150, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    cino = models.CharField(primary_key=True, max_length=16)
    lower_cino = models.CharField(max_length=16, blank=True, null=True)
    admiralty = models.CharField(max_length=1, blank=True, null=True)
    vessel_name = models.CharField(max_length=100, blank=True, null=True)
    pet_salutation = models.SmallIntegerField(blank=True, null=True)
    res_salutation = models.SmallIntegerField(blank=True, null=True)
    lower_court_state = models.BigIntegerField(blank=True, null=True)
    lower_court_district = models.BigIntegerField(blank=True, null=True)
    filcase_type = models.SmallIntegerField(blank=True, null=True)
    regcase_type = models.SmallIntegerField(blank=True, null=True)
    caveat_state_code = models.IntegerField(blank=True, null=True)
    caveat_dist_code = models.IntegerField(blank=True, null=True)
    qjnumber = models.CharField(max_length=255, blank=True, null=True)
    proposed_case_type = models.CharField(max_length=255, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    date_of_order = models.DateField(blank=True, null=True)
    trial_court_state = models.BigIntegerField(blank=True, null=True)
    trial_court_district = models.BigIntegerField(blank=True, null=True)
    trial_court_code = models.SmallIntegerField(blank=True, null=True)
    trial_case_no = models.CharField(max_length=15, blank=True, null=True)
    trial_dec_date = models.DateField(blank=True, null=True)
    trial_cino = models.CharField(max_length=16, blank=True, null=True)
    trial_judge_name = models.CharField(max_length=100, blank=True, null=True)
    trial_jocode = models.CharField(max_length=150, blank=True, null=True)
    trial_cc_applied_date = models.DateField(blank=True, null=True)
    trial_cc_received_date = models.DateField(blank=True, null=True)
    trial_filing_case = models.SmallIntegerField()
    date_of_order1 = models.DateField(blank=True, null=True)
    highcourt_cino = models.CharField(max_length=16, blank=True, null=True)
    hc_cc_applied_date = models.DateField(blank=True, null=True)
    hc_cc_ready_date = models.DateField(blank=True, null=True)
    hc_order_date = models.DateField(blank=True, null=True)
    qjnumber1 = models.CharField(max_length=150, blank=True, null=True)
    lower_court_flag = models.SmallIntegerField(blank=True, null=True)
    caveat_tag_date = models.DateField(blank=True, null=True)
    obj_flag = models.TextField()  # This field type is a guess.
    under_obj = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'caveat_t'


class CaveatTA(models.Model):
    slno = models.BigIntegerField()
    slyear = models.SmallIntegerField(blank=True, null=True)
    caveat_no = models.CharField(max_length=15, blank=True, null=True)
    orgname = models.BigIntegerField(blank=True, null=True)
    ref_case_no = models.CharField(max_length=16, blank=True, null=True)
    petname = models.CharField(max_length=100, blank=True, null=True)
    lpetname = models.CharField(max_length=100, blank=True, null=True)
    resname = models.CharField(max_length=100, blank=True, null=True)
    resorgname = models.BigIntegerField()
    lresname = models.CharField(max_length=100, blank=True, null=True)
    dt_filing = models.DateField(blank=True, null=True)
    court_filed = models.SmallIntegerField()
    dt_court = models.DateField(blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    lsubject = models.CharField(max_length=150, blank=True, null=True)
    filing_case = models.SmallIntegerField()
    low_case_no = models.CharField(max_length=15, blank=True, null=True)
    ldec_date = models.DateField(blank=True, null=True)
    ljud_name = models.CharField(max_length=100, blank=True, null=True)
    pet_father_name = models.CharField(max_length=100, blank=True, null=True)
    lpet_father_name = models.CharField(max_length=100, blank=True, null=True)
    pet_relation_flag = models.CharField(max_length=2, blank=True, null=True)
    pet_adv = models.CharField(max_length=100, blank=True, null=True)
    lpet_adv = models.CharField(max_length=100, blank=True, null=True)
    res_father_name = models.CharField(max_length=100, blank=True, null=True)
    lres_father_name = models.CharField(max_length=100, blank=True, null=True)
    res_relation_flag = models.CharField(max_length=2, blank=True, null=True)
    lower_court_code = models.SmallIntegerField(blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    caveatfil_no = models.CharField(unique=True, max_length=15, blank=True, null=True)
    time_of_filing = models.TimeField(blank=True, null=True)
    extrarefcase_no = models.CharField(max_length=1000, blank=True, null=True)
    oldcaveat_no = models.CharField(max_length=15, blank=True, null=True)
    pet_adv_cd = models.BigIntegerField()
    pet_email = models.CharField(max_length=254, blank=True, null=True)
    pet_mobile = models.CharField(max_length=15, blank=True, null=True)
    res_email = models.CharField(max_length=254, blank=True, null=True)
    res_mobile = models.CharField(max_length=15, blank=True, null=True)
    dt_reg = models.DateField(blank=True, null=True)
    time_of_reg = models.TimeField(blank=True, null=True)
    reasonfilingdate = models.CharField(max_length=255, blank=True, null=True)
    reasonregisdate = models.CharField(max_length=255, blank=True, null=True)
    lcc_applied_date = models.DateField(blank=True, null=True)
    lcc_received_date = models.DateField(blank=True, null=True)
    res_adv_cd = models.BigIntegerField()
    res_adv_name = models.CharField(max_length=100, blank=True, null=True)
    lres_adv_name = models.CharField(max_length=100, blank=True, null=True)
    res_occupation = models.CharField(max_length=30, blank=True, null=True)
    pet_occupation = models.CharField(max_length=30, blank=True, null=True)
    pet_inperson = models.CharField(max_length=1, blank=True, null=True)
    res_inperson = models.CharField(max_length=1, blank=True, null=True)
    lower_judge_name = models.CharField(max_length=100, blank=True, null=True)
    lowerjocode = models.CharField(max_length=150, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    cino = models.CharField(primary_key=True, max_length=16)
    lower_cino = models.CharField(max_length=16, blank=True, null=True)
    admiralty = models.CharField(max_length=1, blank=True, null=True)
    vessel_name = models.CharField(max_length=100, blank=True, null=True)
    pet_salutation = models.SmallIntegerField(blank=True, null=True)
    res_salutation = models.SmallIntegerField(blank=True, null=True)
    lower_court_state = models.BigIntegerField(blank=True, null=True)
    lower_court_district = models.BigIntegerField(blank=True, null=True)
    filcase_type = models.SmallIntegerField(blank=True, null=True)
    regcase_type = models.SmallIntegerField(blank=True, null=True)
    caveat_state_code = models.IntegerField(blank=True, null=True)
    caveat_dist_code = models.IntegerField(blank=True, null=True)
    qjnumber = models.CharField(max_length=255, blank=True, null=True)
    proposed_case_type = models.CharField(max_length=255, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    date_of_order = models.DateField(blank=True, null=True)
    trial_court_state = models.BigIntegerField(blank=True, null=True)
    trial_court_district = models.BigIntegerField(blank=True, null=True)
    trial_court_code = models.SmallIntegerField(blank=True, null=True)
    trial_case_no = models.CharField(max_length=15, blank=True, null=True)
    trial_dec_date = models.DateField(blank=True, null=True)
    trial_cino = models.CharField(max_length=16, blank=True, null=True)
    trial_judge_name = models.CharField(max_length=100, blank=True, null=True)
    trial_jocode = models.CharField(max_length=150, blank=True, null=True)
    trial_cc_applied_date = models.DateField(blank=True, null=True)
    trial_cc_received_date = models.DateField(blank=True, null=True)
    trial_filing_case = models.SmallIntegerField()
    date_of_order1 = models.DateField(blank=True, null=True)
    highcourt_cino = models.CharField(max_length=16, blank=True, null=True)
    hc_cc_applied_date = models.DateField(blank=True, null=True)
    hc_cc_ready_date = models.DateField(blank=True, null=True)
    hc_order_date = models.DateField(blank=True, null=True)
    qjnumber1 = models.CharField(max_length=150, blank=True, null=True)
    lower_court_flag = models.SmallIntegerField(blank=True, null=True)
    caveat_tag_date = models.DateField(blank=True, null=True)
    obj_flag = models.TextField()  # This field type is a guess.
    under_obj = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'caveat_t_a'


class ChangeFilingType(models.Model):
    fil_no = models.CharField(max_length=16, blank=True, null=True)
    flag = models.CharField(max_length=1, blank=True, null=True)
    new_no = models.CharField(max_length=16, blank=True, null=True)
    fil_dt = models.DateField(blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)
    usercode = models.IntegerField(blank=True, null=True)
    ent_dt = models.DateField(blank=True, null=True)
    display = models.CharField(max_length=1, blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'change_filing_type'


class ChargeTrans(models.Model):
    pk = models.CompositePrimaryKey('cino', 'party_no', 'party_type', 'charge_id')
    cino = models.CharField(max_length=16)
    party_no = models.SmallIntegerField()
    party_type = models.SmallIntegerField()
    charge_date = models.DateField(blank=True, null=True)
    charge_id = models.SmallIntegerField()
    charge = models.TextField(blank=True, null=True)
    disposal_date = models.DateField(blank=True, null=True)
    proved = models.CharField(max_length=1, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'charge_trans'


class CitationCounter(models.Model):
    ncitation_no = models.IntegerField()
    ncitation_year = models.SmallIntegerField(primary_key=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'citation_counter'


class CivAddressT(models.Model):
    pk = models.CompositePrimaryKey('cino', 'party_no')
    party_no = models.SmallIntegerField()
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    orgid = models.SmallIntegerField()
    name = models.CharField(max_length=100, blank=True, null=True)
    lname = models.CharField(max_length=100, blank=True, null=True)
    pet_age = models.SmallIntegerField()
    father_name = models.CharField(max_length=100, blank=True, null=True)
    lfather_name = models.CharField(max_length=100, blank=True, null=True)
    father_flag = models.CharField(max_length=2)
    pet_caste = models.CharField(max_length=20, blank=True, null=True)
    type = models.SmallIntegerField()
    adv_name = models.CharField(max_length=100, blank=True, null=True)
    ladv_name = models.CharField(max_length=100, blank=True, null=True)
    adv_cd = models.BigIntegerField()
    display = models.TextField()  # This field type is a guess.
    legal_heir = models.TextField()  # This field type is a guess.
    pet_email = models.CharField(max_length=254, blank=True, null=True)
    pet_mobile = models.CharField(max_length=15, blank=True, null=True)
    parentid = models.SmallIntegerField(blank=True, null=True)
    pet_sex = models.CharField(max_length=1, blank=True, null=True)
    uid_no = models.BigIntegerField(blank=True, null=True)
    performaresflag = models.CharField(max_length=1)
    hide_partyname = models.CharField(max_length=1)
    party_id = models.TextField(blank=True, null=True)
    split_case_refno = models.CharField(max_length=15, blank=True, null=True)
    split_case_flag = models.TextField()  # This field type is a guess.
    old_party_no = models.CharField(max_length=11, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    extra_inperson = models.CharField(max_length=1, blank=True, null=True)
    party_status = models.IntegerField()
    cino = models.CharField(max_length=16)
    pet_gender = models.CharField(max_length=1, blank=True, null=True)
    name_salutation = models.SmallIntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    prid = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'civ_address_t'


class CivAddressTA(models.Model):
    pk = models.CompositePrimaryKey('cino', 'party_no')
    party_no = models.SmallIntegerField()
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    orgid = models.SmallIntegerField()
    name = models.CharField(max_length=100, blank=True, null=True)
    lname = models.CharField(max_length=100, blank=True, null=True)
    pet_age = models.SmallIntegerField()
    father_name = models.CharField(max_length=100, blank=True, null=True)
    lfather_name = models.CharField(max_length=100, blank=True, null=True)
    father_flag = models.CharField(max_length=2)
    pet_caste = models.CharField(max_length=20, blank=True, null=True)
    type = models.SmallIntegerField()
    adv_name = models.CharField(max_length=100, blank=True, null=True)
    ladv_name = models.CharField(max_length=100, blank=True, null=True)
    adv_cd = models.BigIntegerField()
    display = models.TextField()  # This field type is a guess.
    legal_heir = models.TextField()  # This field type is a guess.
    pet_email = models.CharField(max_length=254, blank=True, null=True)
    pet_mobile = models.CharField(max_length=15, blank=True, null=True)
    parentid = models.SmallIntegerField(blank=True, null=True)
    pet_sex = models.CharField(max_length=1, blank=True, null=True)
    uid_no = models.BigIntegerField(blank=True, null=True)
    performaresflag = models.CharField(max_length=1)
    hide_partyname = models.CharField(max_length=1)
    party_id = models.TextField(blank=True, null=True)
    split_case_refno = models.CharField(max_length=15, blank=True, null=True)
    split_case_flag = models.TextField()  # This field type is a guess.
    old_party_no = models.CharField(max_length=11, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    extra_inperson = models.CharField(max_length=1, blank=True, null=True)
    party_status = models.IntegerField()
    cino = models.CharField(max_length=16)
    pet_gender = models.CharField(max_length=1, blank=True, null=True)
    name_salutation = models.SmallIntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    prid = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'civ_address_t_a'


class CivilProcess(models.Model):
    pk = models.CompositePrimaryKey('rec_no', 'rec_year')
    cino = models.CharField(max_length=16)
    case_no = models.CharField(max_length=255, blank=True, null=True)
    filing_no = models.CharField(max_length=255, blank=True, null=True)
    date_first_list = models.DateField(blank=True, null=True)
    dt_regis = models.DateField(blank=True, null=True)
    date_of_filing = models.DateField(blank=True, null=True)
    date_of_decision = models.DateField(blank=True, null=True)
    next_date = models.DateField(blank=True, null=True)
    todays_date = models.DateField(blank=True, null=True)
    pet_name = models.CharField(max_length=100, blank=True, null=True)
    res_name = models.CharField(max_length=100, blank=True, null=True)
    pet_add = models.TextField(blank=True, null=True)
    res_add = models.TextField(blank=True, null=True)
    pet_age = models.SmallIntegerField()
    res_age = models.SmallIntegerField()
    prev_purpose = models.CharField(max_length=100, blank=True, null=True)
    next_purpose = models.CharField(max_length=100, blank=True, null=True)
    sub_purpose = models.CharField(max_length=100, blank=True, null=True)
    disposal_type = models.CharField(max_length=100, blank=True, null=True)
    nature = models.CharField(max_length=500, blank=True, null=True)
    lower_case_no = models.CharField(max_length=255, blank=True, null=True)
    lower_court_name = models.CharField(max_length=255, blank=True, null=True)
    lower_disp_date = models.DateField(blank=True, null=True)
    relief_offense = models.TextField(blank=True, null=True)
    cause_of_action = models.TextField(blank=True, null=True)
    offense_date = models.DateField(blank=True, null=True)
    under_act1 = models.CharField(max_length=100, blank=True, null=True)
    under_sec1 = models.CharField(max_length=100, blank=True, null=True)
    under_act2 = models.CharField(max_length=100, blank=True, null=True)
    under_sec2 = models.CharField(max_length=100, blank=True, null=True)
    under_act3 = models.CharField(max_length=100, blank=True, null=True)
    under_sec3 = models.CharField(max_length=100, blank=True, null=True)
    under_act4 = models.CharField(max_length=100, blank=True, null=True)
    under_sec4 = models.CharField(max_length=100, blank=True, null=True)
    court_name = models.CharField(max_length=100, blank=True, null=True)
    desg_name = models.CharField(max_length=500, blank=True, null=True)
    judge_name = models.CharField(max_length=500, blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    police_stn = models.CharField(max_length=100, blank=True, null=True)
    fir_no = models.CharField(max_length=100, blank=True, null=True)
    fir_year = models.SmallIntegerField(blank=True, null=True)
    main_case_no = models.CharField(max_length=255, blank=True, null=True)
    maincase_dtregis = models.DateField(blank=True, null=True)
    process_fees = models.IntegerField()
    fees_type = models.CharField(max_length=1, blank=True, null=True)
    receipt_no = models.CharField(max_length=50, blank=True, null=True)
    receipt_year = models.CharField(max_length=50, blank=True, null=True)
    receipt_dates = models.CharField(max_length=255, blank=True, null=True)
    fee = models.CharField(max_length=100, blank=True, null=True)
    recv_name = models.CharField(max_length=100, blank=True, null=True)
    recv_fathername = models.CharField(max_length=100, blank=True, null=True)
    recv_address = models.TextField(blank=True, null=True)
    recvaddress_type = models.TextField()  # This field type is a guess.
    ns_id = models.BigIntegerField()
    recv_state = models.CharField(max_length=100, blank=True, null=True)
    recv_district = models.CharField(max_length=100, blank=True, null=True)
    recv_taluka = models.CharField(max_length=100, blank=True, null=True)
    recv_village = models.CharField(max_length=100, blank=True, null=True)
    recv_town = models.CharField(max_length=100, blank=True, null=True)
    recv_ward = models.CharField(max_length=100, blank=True, null=True)
    recv_village1 = models.CharField(max_length=100, blank=True, null=True)
    recv_village2 = models.CharField(max_length=100, blank=True, null=True)
    recv_mobile = models.CharField(max_length=15, blank=True, null=True)
    recv_pincode = models.CharField(max_length=15, blank=True, null=True)
    receiver_age = models.SmallIntegerField()
    recv_adv = models.CharField(max_length=100, blank=True, null=True)
    party_no = models.SmallIntegerField()
    party_type = models.CharField(max_length=5, blank=True, null=True)
    server_date = models.DateField(blank=True, null=True)
    session_date = models.DateField(blank=True, null=True)
    draft_date = models.DateField(blank=True, null=True)
    ns_date = models.DateField(blank=True, null=True)
    label1 = models.CharField(max_length=150, blank=True, null=True)
    label2 = models.CharField(max_length=150, blank=True, null=True)
    label3 = models.CharField(max_length=150, blank=True, null=True)
    label4 = models.CharField(max_length=150, blank=True, null=True)
    label5 = models.CharField(max_length=150, blank=True, null=True)
    ns_title = models.CharField(max_length=255, blank=True, null=True)
    process_id = models.CharField(max_length=25, blank=True, null=True)
    rec_no = models.BigIntegerField()
    rec_year = models.BigIntegerField()
    recv_email = models.CharField(max_length=99, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    pet_father_name = models.CharField(max_length=99, blank=True, null=True)
    pet_father_flag = models.CharField(max_length=2, blank=True, null=True)
    res_father_name = models.CharField(max_length=99, blank=True, null=True)
    res_father_flag = models.CharField(max_length=2, blank=True, null=True)
    court_no = models.IntegerField(blank=True, null=True)
    recv_state_id = models.IntegerField(blank=True, null=True)
    recv_district_id = models.IntegerField(blank=True, null=True)
    recv_taluka_id = models.IntegerField(blank=True, null=True)
    recv_village_id = models.IntegerField(blank=True, null=True)
    recv_village1_id = models.IntegerField(blank=True, null=True)
    recv_village2_id = models.IntegerField(blank=True, null=True)
    recv_town_id = models.IntegerField(blank=True, null=True)
    recv_ward_id = models.IntegerField(blank=True, null=True)
    police_st_code = models.IntegerField(blank=True, null=True)
    court_process_id = models.SmallIntegerField()
    recv_police_stn = models.CharField(max_length=100, blank=True, null=True)
    recv_state_census = models.IntegerField()
    recv_district_census = models.IntegerField()
    recv_taluka_census = models.IntegerField()
    recv_village_census = models.IntegerField()
    recv_town_census = models.IntegerField()
    recv_ward_census = models.IntegerField()
    recv_village1_census = models.IntegerField()
    recv_village2_census = models.IntegerField()
    recv_police_st_census = models.CharField(max_length=10, blank=True, null=True)
    srno = models.BigIntegerField(blank=True, null=True)
    year = models.BigIntegerField(blank=True, null=True)
    regcase_type = models.SmallIntegerField(blank=True, null=True)
    reg_no = models.IntegerField(blank=True, null=True)
    reg_year = models.SmallIntegerField(blank=True, null=True)
    filcase_type = models.SmallIntegerField(blank=True, null=True)
    fil_no = models.IntegerField(blank=True, null=True)
    fil_year = models.SmallIntegerField(blank=True, null=True)
    recv_father_flag = models.CharField(max_length=2, blank=True, null=True)
    label6 = models.CharField(max_length=150, blank=True, null=True)
    label7 = models.CharField(max_length=150, blank=True, null=True)
    label8 = models.CharField(max_length=150, blank=True, null=True)
    label9 = models.CharField(max_length=150, blank=True, null=True)
    label10 = models.CharField(max_length=150, blank=True, null=True)
    date1 = models.DateField(blank=True, null=True)
    date2 = models.DateField(blank=True, null=True)
    date3 = models.DateField(blank=True, null=True)
    date4 = models.DateField(blank=True, null=True)
    date5 = models.DateField(blank=True, null=True)
    lower_state_id = models.IntegerField(blank=True, null=True)
    lower_taluka_code = models.IntegerField(blank=True, null=True)
    lower_court_code = models.SmallIntegerField(blank=True, null=True)
    lower_trial = models.SmallIntegerField(blank=True, null=True)
    lower_cino = models.CharField(max_length=16, blank=True, null=True)
    lower_judge_name = models.CharField(max_length=100, blank=True, null=True)
    lower_court = models.CharField(max_length=40, blank=True, null=True)
    juri_value = models.CharField(max_length=25, blank=True, null=True)
    main_matter_cino = models.CharField(max_length=16, blank=True, null=True)
    police_private = models.SmallIntegerField(blank=True, null=True)
    police_state_id = models.SmallIntegerField(blank=True, null=True)
    police_dist_code = models.SmallIntegerField(blank=True, null=True)
    police_stn_code = models.IntegerField(blank=True, null=True)
    foot_note = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    nature_cd = models.CharField(max_length=25, blank=True, null=True)
    lower_state_census = models.IntegerField()
    lower_taluka_census = models.IntegerField()
    police_state_census = models.IntegerField()
    police_dist_census = models.IntegerField()
    police_st_census = models.IntegerField()
    process_no = models.SmallIntegerField()
    subprocess_no = models.SmallIntegerField()
    actcode1 = models.BigIntegerField()
    actcode2 = models.BigIntegerField()
    actcode3 = models.BigIntegerField()
    actcode4 = models.BigIntegerField()
    act_census1 = models.CharField(max_length=15, blank=True, null=True)
    act_census2 = models.CharField(max_length=15, blank=True, null=True)
    act_census3 = models.CharField(max_length=15, blank=True, null=True)
    act_census4 = models.CharField(max_length=15, blank=True, null=True)
    est_code = models.CharField(max_length=6, blank=True, null=True)
    delivery_status = models.TextField(blank=True, null=True)  # This field type is a guess.
    lang_flag = models.CharField(max_length=1, blank=True, null=True)
    sparty_name = models.CharField(max_length=100, blank=True, null=True)
    sparty_age = models.SmallIntegerField()
    sparty_sex = models.CharField(max_length=1, blank=True, null=True)
    sparty_relation = models.CharField(max_length=100, blank=True, null=True)
    sparty_relation_flag = models.CharField(max_length=2, blank=True, null=True)
    sparty_type = models.CharField(max_length=5, blank=True, null=True)
    sparty_address = models.TextField(blank=True, null=True)
    sparty_state = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_state_code = models.IntegerField(blank=True, null=True)
    sparty_state_code = models.SmallIntegerField()
    sparty_district = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_district_code = models.IntegerField(blank=True, null=True)
    sparty_district_code = models.SmallIntegerField()
    sparty_taluka = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_taluka_code = models.IntegerField(blank=True, null=True)
    sparty_taluka_code = models.SmallIntegerField()
    sparty_village = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_village_code = models.IntegerField(blank=True, null=True)
    sparty_village_code = models.IntegerField()
    sparty_town = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_town_code = models.IntegerField(blank=True, null=True)
    sparty_town_code = models.IntegerField()
    sparty_ward = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_ward_code = models.IntegerField(blank=True, null=True)
    sparty_ward_code = models.IntegerField()
    sparty_police_station = models.CharField(max_length=100, blank=True, null=True)
    sparty_national_police_station_code = models.IntegerField(blank=True, null=True)
    sparty_police_station_code = models.IntegerField(blank=True, null=True)
    sparty_advocate = models.CharField(max_length=100, blank=True, null=True)
    sparty_email = models.CharField(max_length=99, blank=True, null=True)
    sparty_mobile = models.CharField(max_length=15, blank=True, null=True)
    efield1 = models.IntegerField(blank=True, null=True)
    efield2 = models.IntegerField(blank=True, null=True)
    efield3 = models.IntegerField(blank=True, null=True)
    efield4 = models.TextField(blank=True, null=True)
    efield5 = models.TextField(blank=True, null=True)
    efield6 = models.TextField(blank=True, null=True)
    efield7 = models.DateField(blank=True, null=True)
    efield8 = models.DateField(blank=True, null=True)
    efield9 = models.DateField(blank=True, null=True)
    sparty_village1 = models.CharField(max_length=100, blank=True, null=True)
    sparty_village2 = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_village1_code = models.IntegerField()
    sparty_census_village2_code = models.IntegerField()
    sparty_village1_code = models.IntegerField()
    sparty_village2_code = models.IntegerField()
    sparty_no = models.SmallIntegerField()
    upload_flag = models.CharField(max_length=1, blank=True, null=True)
    sparty_remark = models.TextField(blank=True, null=True)
    sparty_pincode = models.CharField(max_length=15, blank=True, null=True)
    sparty_address_type = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'civil_process'


class CivilProcessA(models.Model):
    pk = models.CompositePrimaryKey('rec_no', 'rec_year')
    cino = models.CharField(max_length=16)
    case_no = models.CharField(max_length=255, blank=True, null=True)
    filing_no = models.CharField(max_length=255, blank=True, null=True)
    date_first_list = models.DateField(blank=True, null=True)
    dt_regis = models.DateField(blank=True, null=True)
    date_of_filing = models.DateField(blank=True, null=True)
    date_of_decision = models.DateField(blank=True, null=True)
    next_date = models.DateField(blank=True, null=True)
    todays_date = models.DateField(blank=True, null=True)
    pet_name = models.CharField(max_length=100, blank=True, null=True)
    res_name = models.CharField(max_length=100, blank=True, null=True)
    pet_add = models.TextField(blank=True, null=True)
    res_add = models.TextField(blank=True, null=True)
    pet_age = models.SmallIntegerField()
    res_age = models.SmallIntegerField()
    prev_purpose = models.CharField(max_length=100, blank=True, null=True)
    next_purpose = models.CharField(max_length=100, blank=True, null=True)
    sub_purpose = models.CharField(max_length=100, blank=True, null=True)
    disposal_type = models.CharField(max_length=100, blank=True, null=True)
    nature = models.CharField(max_length=500, blank=True, null=True)
    lower_case_no = models.CharField(max_length=255, blank=True, null=True)
    lower_court_name = models.CharField(max_length=255, blank=True, null=True)
    lower_disp_date = models.DateField(blank=True, null=True)
    relief_offense = models.TextField(blank=True, null=True)
    cause_of_action = models.TextField(blank=True, null=True)
    offense_date = models.DateField(blank=True, null=True)
    under_act1 = models.CharField(max_length=100, blank=True, null=True)
    under_sec1 = models.CharField(max_length=100, blank=True, null=True)
    under_act2 = models.CharField(max_length=100, blank=True, null=True)
    under_sec2 = models.CharField(max_length=100, blank=True, null=True)
    under_act3 = models.CharField(max_length=100, blank=True, null=True)
    under_sec3 = models.CharField(max_length=100, blank=True, null=True)
    under_act4 = models.CharField(max_length=100, blank=True, null=True)
    under_sec4 = models.CharField(max_length=100, blank=True, null=True)
    court_name = models.CharField(max_length=100, blank=True, null=True)
    desg_name = models.CharField(max_length=500, blank=True, null=True)
    judge_name = models.CharField(max_length=500, blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    police_stn = models.CharField(max_length=100, blank=True, null=True)
    fir_no = models.CharField(max_length=100, blank=True, null=True)
    fir_year = models.SmallIntegerField(blank=True, null=True)
    main_case_no = models.CharField(max_length=255, blank=True, null=True)
    maincase_dtregis = models.DateField(blank=True, null=True)
    process_fees = models.IntegerField()
    fees_type = models.CharField(max_length=1, blank=True, null=True)
    receipt_no = models.CharField(max_length=50, blank=True, null=True)
    receipt_year = models.CharField(max_length=50, blank=True, null=True)
    receipt_dates = models.CharField(max_length=255, blank=True, null=True)
    fee = models.CharField(max_length=100, blank=True, null=True)
    recv_name = models.CharField(max_length=100, blank=True, null=True)
    recv_fathername = models.CharField(max_length=100, blank=True, null=True)
    recv_address = models.TextField(blank=True, null=True)
    recvaddress_type = models.TextField()  # This field type is a guess.
    ns_id = models.BigIntegerField()
    recv_state = models.CharField(max_length=100, blank=True, null=True)
    recv_district = models.CharField(max_length=100, blank=True, null=True)
    recv_taluka = models.CharField(max_length=100, blank=True, null=True)
    recv_village = models.CharField(max_length=100, blank=True, null=True)
    recv_town = models.CharField(max_length=100, blank=True, null=True)
    recv_ward = models.CharField(max_length=100, blank=True, null=True)
    recv_village1 = models.CharField(max_length=100, blank=True, null=True)
    recv_village2 = models.CharField(max_length=100, blank=True, null=True)
    recv_mobile = models.CharField(max_length=15, blank=True, null=True)
    recv_pincode = models.CharField(max_length=15, blank=True, null=True)
    receiver_age = models.SmallIntegerField()
    recv_adv = models.CharField(max_length=100, blank=True, null=True)
    party_no = models.SmallIntegerField()
    party_type = models.CharField(max_length=5, blank=True, null=True)
    server_date = models.DateField(blank=True, null=True)
    session_date = models.DateField(blank=True, null=True)
    draft_date = models.DateField(blank=True, null=True)
    ns_date = models.DateField(blank=True, null=True)
    label1 = models.CharField(max_length=150, blank=True, null=True)
    label2 = models.CharField(max_length=150, blank=True, null=True)
    label3 = models.CharField(max_length=150, blank=True, null=True)
    label4 = models.CharField(max_length=150, blank=True, null=True)
    label5 = models.CharField(max_length=150, blank=True, null=True)
    ns_title = models.CharField(max_length=255, blank=True, null=True)
    process_id = models.CharField(max_length=25, blank=True, null=True)
    rec_no = models.BigIntegerField()
    rec_year = models.BigIntegerField()
    recv_email = models.CharField(max_length=99, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    pet_father_name = models.CharField(max_length=99, blank=True, null=True)
    pet_father_flag = models.CharField(max_length=2, blank=True, null=True)
    res_father_name = models.CharField(max_length=99, blank=True, null=True)
    res_father_flag = models.CharField(max_length=2, blank=True, null=True)
    court_no = models.IntegerField(blank=True, null=True)
    recv_state_id = models.IntegerField(blank=True, null=True)
    recv_district_id = models.IntegerField(blank=True, null=True)
    recv_taluka_id = models.IntegerField(blank=True, null=True)
    recv_village_id = models.IntegerField(blank=True, null=True)
    recv_village1_id = models.IntegerField(blank=True, null=True)
    recv_village2_id = models.IntegerField(blank=True, null=True)
    recv_town_id = models.IntegerField(blank=True, null=True)
    recv_ward_id = models.IntegerField(blank=True, null=True)
    police_st_code = models.IntegerField(blank=True, null=True)
    court_process_id = models.SmallIntegerField()
    recv_police_stn = models.CharField(max_length=100, blank=True, null=True)
    recv_state_census = models.IntegerField()
    recv_district_census = models.IntegerField()
    recv_taluka_census = models.IntegerField()
    recv_village_census = models.IntegerField()
    recv_town_census = models.IntegerField()
    recv_ward_census = models.IntegerField()
    recv_village1_census = models.IntegerField()
    recv_village2_census = models.IntegerField()
    recv_police_st_census = models.CharField(max_length=10, blank=True, null=True)
    srno = models.BigIntegerField(blank=True, null=True)
    year = models.BigIntegerField(blank=True, null=True)
    regcase_type = models.SmallIntegerField(blank=True, null=True)
    reg_no = models.IntegerField(blank=True, null=True)
    reg_year = models.SmallIntegerField(blank=True, null=True)
    filcase_type = models.SmallIntegerField(blank=True, null=True)
    fil_no = models.IntegerField(blank=True, null=True)
    fil_year = models.SmallIntegerField(blank=True, null=True)
    recv_father_flag = models.CharField(max_length=2, blank=True, null=True)
    label6 = models.CharField(max_length=150, blank=True, null=True)
    label7 = models.CharField(max_length=150, blank=True, null=True)
    label8 = models.CharField(max_length=150, blank=True, null=True)
    label9 = models.CharField(max_length=150, blank=True, null=True)
    label10 = models.CharField(max_length=150, blank=True, null=True)
    date1 = models.DateField(blank=True, null=True)
    date2 = models.DateField(blank=True, null=True)
    date3 = models.DateField(blank=True, null=True)
    date4 = models.DateField(blank=True, null=True)
    date5 = models.DateField(blank=True, null=True)
    lower_state_id = models.IntegerField(blank=True, null=True)
    lower_taluka_code = models.IntegerField(blank=True, null=True)
    lower_court_code = models.SmallIntegerField(blank=True, null=True)
    lower_trial = models.SmallIntegerField(blank=True, null=True)
    lower_cino = models.CharField(max_length=16, blank=True, null=True)
    lower_judge_name = models.CharField(max_length=100, blank=True, null=True)
    lower_court = models.CharField(max_length=40, blank=True, null=True)
    juri_value = models.CharField(max_length=25, blank=True, null=True)
    main_matter_cino = models.CharField(max_length=16, blank=True, null=True)
    police_private = models.SmallIntegerField(blank=True, null=True)
    police_state_id = models.SmallIntegerField(blank=True, null=True)
    police_dist_code = models.SmallIntegerField(blank=True, null=True)
    police_stn_code = models.IntegerField(blank=True, null=True)
    foot_note = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    nature_cd = models.CharField(max_length=25, blank=True, null=True)
    lower_state_census = models.IntegerField()
    lower_taluka_census = models.IntegerField()
    police_state_census = models.IntegerField()
    police_dist_census = models.IntegerField()
    police_st_census = models.IntegerField()
    process_no = models.SmallIntegerField()
    subprocess_no = models.SmallIntegerField()
    actcode1 = models.BigIntegerField()
    actcode2 = models.BigIntegerField()
    actcode3 = models.BigIntegerField()
    actcode4 = models.BigIntegerField()
    act_census1 = models.CharField(max_length=15, blank=True, null=True)
    act_census2 = models.CharField(max_length=15, blank=True, null=True)
    act_census3 = models.CharField(max_length=15, blank=True, null=True)
    act_census4 = models.CharField(max_length=15, blank=True, null=True)
    est_code = models.CharField(max_length=6, blank=True, null=True)
    delivery_status = models.TextField(blank=True, null=True)  # This field type is a guess.
    lang_flag = models.CharField(max_length=1, blank=True, null=True)
    sparty_name = models.CharField(max_length=100, blank=True, null=True)
    sparty_age = models.SmallIntegerField()
    sparty_sex = models.CharField(max_length=1, blank=True, null=True)
    sparty_relation = models.CharField(max_length=100, blank=True, null=True)
    sparty_relation_flag = models.CharField(max_length=2, blank=True, null=True)
    sparty_type = models.CharField(max_length=5, blank=True, null=True)
    sparty_address = models.TextField(blank=True, null=True)
    sparty_state = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_state_code = models.IntegerField(blank=True, null=True)
    sparty_state_code = models.SmallIntegerField()
    sparty_district = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_district_code = models.IntegerField(blank=True, null=True)
    sparty_district_code = models.SmallIntegerField()
    sparty_taluka = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_taluka_code = models.IntegerField(blank=True, null=True)
    sparty_taluka_code = models.SmallIntegerField()
    sparty_village = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_village_code = models.IntegerField(blank=True, null=True)
    sparty_village_code = models.IntegerField()
    sparty_town = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_town_code = models.IntegerField(blank=True, null=True)
    sparty_town_code = models.IntegerField()
    sparty_ward = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_ward_code = models.IntegerField(blank=True, null=True)
    sparty_ward_code = models.IntegerField()
    sparty_police_station = models.CharField(max_length=100, blank=True, null=True)
    sparty_national_police_station_code = models.IntegerField(blank=True, null=True)
    sparty_police_station_code = models.IntegerField(blank=True, null=True)
    sparty_advocate = models.CharField(max_length=100, blank=True, null=True)
    sparty_email = models.CharField(max_length=99, blank=True, null=True)
    sparty_mobile = models.CharField(max_length=15, blank=True, null=True)
    efield1 = models.IntegerField(blank=True, null=True)
    efield2 = models.IntegerField(blank=True, null=True)
    efield3 = models.IntegerField(blank=True, null=True)
    efield4 = models.TextField(blank=True, null=True)
    efield5 = models.TextField(blank=True, null=True)
    efield6 = models.TextField(blank=True, null=True)
    efield7 = models.DateField(blank=True, null=True)
    efield8 = models.DateField(blank=True, null=True)
    efield9 = models.DateField(blank=True, null=True)
    sparty_village1 = models.CharField(max_length=100, blank=True, null=True)
    sparty_village2 = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_village1_code = models.IntegerField()
    sparty_census_village2_code = models.IntegerField()
    sparty_village1_code = models.IntegerField()
    sparty_village2_code = models.IntegerField()
    sparty_no = models.SmallIntegerField()
    upload_flag = models.CharField(max_length=1, blank=True, null=True)
    sparty_remark = models.TextField(blank=True, null=True)
    sparty_pincode = models.CharField(max_length=15, blank=True, null=True)
    sparty_address_type = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'civil_process_a'


class CivilT(models.Model):
    case_no = models.CharField(max_length=15, blank=True, null=True)
    pet_name = models.CharField(max_length=100, blank=True, null=True)
    lpet_name = models.CharField(max_length=100, blank=True, null=True)
    pet_sex = models.CharField(max_length=1, blank=True, null=True)
    res_name = models.CharField(max_length=100, blank=True, null=True)
    lres_name = models.CharField(max_length=100, blank=True, null=True)
    res_sex = models.CharField(max_length=1, blank=True, null=True)
    court_no = models.IntegerField()
    date_of_filing = models.DateField(blank=True, null=True)
    time_of_filing = models.TimeField(blank=True, null=True)
    date_first_list = models.DateField(blank=True, null=True)
    date_next_list = models.DateField(blank=True, null=True)
    date_last_list = models.DateField(blank=True, null=True)
    date_of_decision = models.DateField(blank=True, null=True)
    dec_jud_name = models.CharField(max_length=100, blank=True, null=True)
    pet_adv = models.CharField(max_length=500, blank=True, null=True)
    pet_adv_cd = models.BigIntegerField()
    lpet_adv = models.CharField(max_length=100, blank=True, null=True)
    res_adv = models.CharField(max_length=500, blank=True, null=True)
    res_adv_cd = models.BigIntegerField()
    lres_adv = models.CharField(max_length=100, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2)
    juri_value = models.CharField(max_length=25)
    purpose_prev = models.SmallIntegerField()
    purpose_next = models.SmallIntegerField()
    subject1 = models.CharField(max_length=255, blank=True, null=True)
    caveat = models.CharField(max_length=255, blank=True, null=True)
    unit = models.DecimalField(max_digits=17, decimal_places=2)
    goshwara_no = models.SmallIntegerField()
    disp_nature = models.SmallIntegerField()
    pet_father_name = models.CharField(max_length=100, blank=True, null=True)
    lpet_father_name = models.CharField(max_length=100, blank=True, null=True)
    pet_father_flag = models.CharField(max_length=2, blank=True, null=True)
    pet_caste = models.CharField(max_length=2, blank=True, null=True)
    pet_age = models.SmallIntegerField()
    pet_email = models.CharField(max_length=254, blank=True, null=True)
    pet_mobile = models.CharField(max_length=15, blank=True, null=True)
    res_father_name = models.CharField(max_length=100, blank=True, null=True)
    lres_father_name = models.CharField(max_length=100, blank=True, null=True)
    res_father_flag = models.CharField(max_length=2, blank=True, null=True)
    res_caste = models.CharField(max_length=2, blank=True, null=True)
    res_age = models.SmallIntegerField()
    res_email = models.CharField(max_length=254, blank=True, null=True)
    res_mobile = models.CharField(max_length=15, blank=True, null=True)
    dt_regis = models.DateField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    date_filing_disp = models.DateField(blank=True, null=True)
    pet_legal_heir = models.TextField()  # This field type is a guess.
    res_legal_heir = models.TextField()  # This field type is a guess.
    ci_cri = models.SmallIntegerField()
    link_code = models.CharField(max_length=15, blank=True, null=True)
    reason_for_rej = models.TextField(blank=True, null=True)
    lreason_for_rej = models.TextField(blank=True, null=True)
    not_before_me = models.CharField(max_length=50, blank=True, null=True)
    before_me = models.CharField(max_length=50, blank=True, null=True)
    obj_flag = models.TextField()  # This field type is a guess.
    date_filing_disp_o = models.DateField(blank=True, null=True)
    date_filing_restore = models.DateField(blank=True, null=True)
    date_of_decision_o = models.DateField(blank=True, null=True)
    date_of_revoke = models.DateField(blank=True, null=True)
    urgent = models.TextField()  # This field type is a guess.
    main_case_no = models.CharField(max_length=15, blank=True, null=True)
    chk = models.CharField(max_length=50, blank=True, null=True)
    reg_pl = models.CharField(max_length=1, blank=True, null=True)
    orgid = models.SmallIntegerField(blank=True, null=True)
    resorgid = models.SmallIntegerField(blank=True, null=True)
    pet_dob = models.DateField(blank=True, null=True)
    res_dob = models.DateField(blank=True, null=True)
    plead_guilty = models.TextField()  # This field type is a guess.
    nature_cd = models.CharField(max_length=25, blank=True, null=True)
    legacy_flag = models.TextField()  # This field type is a guess.
    pet_extracount = models.IntegerField()
    res_extracount = models.IntegerField()
    order_sect_kar = models.TextField(blank=True, null=True)
    nature_kar = models.TextField(blank=True, null=True)
    allocation_dt = models.DateField(blank=True, null=True)
    rej_sr_no = models.IntegerField()
    unit_type = models.CharField(max_length=150, blank=True, null=True)
    unit_type_value = models.CharField(max_length=150, blank=True, null=True)
    transfer_est = models.TextField()  # This field type is a guess.
    imprisonment = models.SmallIntegerField()
    bal_fee_date = models.DateField(blank=True, null=True)
    pet_uid = models.BigIntegerField(blank=True, null=True)
    res_uid = models.BigIntegerField(blank=True, null=True)
    reasonregisdate = models.TextField(blank=True, null=True)
    oldcase_no = models.CharField(max_length=16, blank=True, null=True)
    performaresflag = models.TextField()  # This field type is a guess.
    reasonfilingdate = models.CharField(max_length=255, blank=True, null=True)
    oldfiling_no = models.CharField(max_length=16, blank=True, null=True)
    hide_pet_name = models.CharField(max_length=1)
    hide_res_name = models.CharField(max_length=1)
    hide_partyname = models.CharField(max_length=1)
    filcase_type = models.SmallIntegerField(blank=True, null=True)
    fil_no = models.IntegerField(blank=True, null=True)
    fil_year = models.SmallIntegerField(blank=True, null=True)
    regcase_type = models.SmallIntegerField(blank=True, null=True)
    reg_no = models.IntegerField(blank=True, null=True)
    reg_year = models.SmallIntegerField(blank=True, null=True)
    goshwara_no_o = models.SmallIntegerField()
    disp_nature_o = models.SmallIntegerField()
    archive = models.TextField()  # This field type is a guess.
    tab_status = models.CharField(max_length=25, blank=True, null=True)
    lsubject1 = models.CharField(max_length=255, blank=True, null=True)
    pending_ia = models.TextField()  # This field type is a guess.
    ia_next_date = models.DateField(blank=True, null=True)
    time_slot = models.IntegerField(blank=True, null=True)
    purpose_today = models.SmallIntegerField()
    subpurpose_today = models.SmallIntegerField()
    main_matter_cino = models.CharField(max_length=16, blank=True, null=True)
    split_case_refno = models.CharField(max_length=15, blank=True, null=True)
    split_case_flag = models.TextField()  # This field type is a guess.
    jocode = models.CharField(max_length=150, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    dormant_sinedie = models.CharField(max_length=1, blank=True, null=True)
    pet_inperson = models.CharField(max_length=1, blank=True, null=True)
    res_inperson = models.CharField(max_length=1, blank=True, null=True)
    pet_status = models.IntegerField()
    res_status = models.IntegerField()
    grouped = models.CharField(max_length=1, blank=True, null=True)
    # Legacy table has no surrogate `id`; CIS uses CINO as the case identifier / PK.
    cino = models.CharField(max_length=16, primary_key=True)
    subnature_cd1 = models.CharField(max_length=25, blank=True, null=True)
    subnature_cd2 = models.CharField(max_length=25, blank=True, null=True)
    branch_id = models.IntegerField(blank=True, null=True)
    bench_type = models.IntegerField(blank=True, null=True)
    sr_no = models.IntegerField(blank=True, null=True)
    causelist_type = models.IntegerField(blank=True, null=True)
    next_date_check = models.CharField(max_length=1, blank=True, null=True)
    status_id = models.IntegerField(blank=True, null=True)
    link_criteria = models.CharField(max_length=1, blank=True, null=True)
    c_subject = models.IntegerField(blank=True, null=True)
    cs_subject = models.IntegerField(blank=True, null=True)
    css_subject = models.IntegerField(blank=True, null=True)
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    desig_code = models.CharField(max_length=50, blank=True, null=True)
    pet_gender = models.CharField(max_length=1, blank=True, null=True)
    res_gender = models.CharField(max_length=1, blank=True, null=True)
    pet_salutation = models.SmallIntegerField(blank=True, null=True)
    res_salutation = models.SmallIntegerField(blank=True, null=True)
    case_remark = models.TextField(blank=True, null=True)
    under_obj = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    csss_subject = models.IntegerField(blank=True, null=True)
    tied_up = models.IntegerField()
    extra_link = models.TextField()  # This field type is a guess.
    ag_office = models.CharField(max_length=12, blank=True, null=True)
    afidvt = models.IntegerField(blank=True, null=True)
    connected_type = models.IntegerField(blank=True, null=True)
    link_cino = models.CharField(max_length=16, blank=True, null=True)
    bunch = models.IntegerField(blank=True, null=True)
    short_order = models.CharField(max_length=50, blank=True, null=True)
    maincase_filing_no = models.CharField(max_length=15, blank=True, null=True)
    last_status = models.CharField(max_length=1, blank=True, null=True)
    sub_cino = models.TextField(blank=True, null=True)
    vc_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    claim_juri_value = models.CharField(max_length=25)
    vehicle_regn_no = models.CharField(max_length=100, blank=True, null=True)
    license_no = models.CharField(max_length=100, blank=True, null=True)
    random_alloc = models.TextField(blank=True, null=True)  # This field type is a guess.
    regular_proc = models.TextField(blank=True, null=True)  # This field type is a guess.
    datacorrection = models.TextField(blank=True, null=True)  # This field type is a guess.
    auto_date = models.DateField(blank=True, null=True)
    auto_date_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    transfer_remark = models.TextField(blank=True, null=True)
    eflag = models.CharField(max_length=1, blank=True, null=True)
    efilno = models.CharField(unique=True, max_length=99, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    caveat_tag_date = models.DateField(blank=True, null=True)
    pet_prid = models.CharField(max_length=25, blank=True, null=True)
    res_prid = models.CharField(max_length=25, blank=True, null=True)
    send_to_vcourt = models.DateField(blank=True, null=True)
    receipt_from_vcourt = models.DateField(blank=True, null=True)
    vcourt_cnr = models.CharField(max_length=16)
    vcourt_sent_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    vcourt_receive_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    notify_court_id = models.CharField(max_length=100, blank=True, null=True)
    efiling_type = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'civil_t'


class CivilTA(models.Model):
    case_no = models.CharField(unique=True, max_length=15, blank=True, null=True)
    pet_name = models.CharField(max_length=100, blank=True, null=True)
    lpet_name = models.CharField(max_length=100, blank=True, null=True)
    pet_sex = models.CharField(max_length=1, blank=True, null=True)
    res_name = models.CharField(max_length=100, blank=True, null=True)
    lres_name = models.CharField(max_length=100, blank=True, null=True)
    res_sex = models.CharField(max_length=1, blank=True, null=True)
    court_no = models.IntegerField()
    date_of_filing = models.DateField(blank=True, null=True)
    time_of_filing = models.TimeField(blank=True, null=True)
    date_first_list = models.DateField(blank=True, null=True)
    date_next_list = models.DateField(blank=True, null=True)
    date_last_list = models.DateField(blank=True, null=True)
    date_of_decision = models.DateField(blank=True, null=True)
    dec_jud_name = models.CharField(max_length=100, blank=True, null=True)
    pet_adv = models.CharField(max_length=500, blank=True, null=True)
    pet_adv_cd = models.BigIntegerField()
    lpet_adv = models.CharField(max_length=100, blank=True, null=True)
    res_adv = models.CharField(max_length=500, blank=True, null=True)
    res_adv_cd = models.BigIntegerField()
    lres_adv = models.CharField(max_length=100, blank=True, null=True)
    filing_no = models.CharField(unique=True, max_length=15, blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2)
    juri_value = models.CharField(max_length=25)
    purpose_prev = models.SmallIntegerField()
    purpose_next = models.SmallIntegerField()
    subject1 = models.CharField(max_length=255, blank=True, null=True)
    caveat = models.CharField(max_length=255, blank=True, null=True)
    unit = models.DecimalField(max_digits=17, decimal_places=2)
    goshwara_no = models.SmallIntegerField()
    disp_nature = models.SmallIntegerField()
    pet_father_name = models.CharField(max_length=100, blank=True, null=True)
    lpet_father_name = models.CharField(max_length=100, blank=True, null=True)
    pet_father_flag = models.CharField(max_length=2, blank=True, null=True)
    pet_caste = models.CharField(max_length=2, blank=True, null=True)
    pet_age = models.SmallIntegerField()
    pet_email = models.CharField(max_length=254, blank=True, null=True)
    pet_mobile = models.CharField(max_length=15, blank=True, null=True)
    res_father_name = models.CharField(max_length=100, blank=True, null=True)
    lres_father_name = models.CharField(max_length=100, blank=True, null=True)
    res_father_flag = models.CharField(max_length=2, blank=True, null=True)
    res_caste = models.CharField(max_length=2, blank=True, null=True)
    res_age = models.SmallIntegerField()
    res_email = models.CharField(max_length=254, blank=True, null=True)
    res_mobile = models.CharField(max_length=15, blank=True, null=True)
    dt_regis = models.DateField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    date_filing_disp = models.DateField(blank=True, null=True)
    pet_legal_heir = models.TextField()  # This field type is a guess.
    res_legal_heir = models.TextField()  # This field type is a guess.
    ci_cri = models.SmallIntegerField()
    link_code = models.CharField(max_length=15, blank=True, null=True)
    reason_for_rej = models.TextField(blank=True, null=True)
    lreason_for_rej = models.TextField(blank=True, null=True)
    not_before_me = models.CharField(max_length=50, blank=True, null=True)
    before_me = models.CharField(max_length=50, blank=True, null=True)
    obj_flag = models.TextField()  # This field type is a guess.
    date_filing_disp_o = models.DateField(blank=True, null=True)
    date_filing_restore = models.DateField(blank=True, null=True)
    date_of_decision_o = models.DateField(blank=True, null=True)
    date_of_revoke = models.DateField(blank=True, null=True)
    urgent = models.TextField()  # This field type is a guess.
    main_case_no = models.CharField(max_length=15, blank=True, null=True)
    chk = models.CharField(max_length=50, blank=True, null=True)
    reg_pl = models.CharField(max_length=1, blank=True, null=True)
    orgid = models.SmallIntegerField(blank=True, null=True)
    resorgid = models.SmallIntegerField(blank=True, null=True)
    pet_dob = models.DateField(blank=True, null=True)
    res_dob = models.DateField(blank=True, null=True)
    plead_guilty = models.TextField()  # This field type is a guess.
    nature_cd = models.CharField(max_length=25, blank=True, null=True)
    legacy_flag = models.TextField()  # This field type is a guess.
    pet_extracount = models.IntegerField()
    res_extracount = models.IntegerField()
    order_sect_kar = models.TextField(blank=True, null=True)
    nature_kar = models.TextField(blank=True, null=True)
    allocation_dt = models.DateField(blank=True, null=True)
    rej_sr_no = models.IntegerField()
    unit_type = models.CharField(max_length=150, blank=True, null=True)
    unit_type_value = models.CharField(max_length=150, blank=True, null=True)
    transfer_est = models.TextField()  # This field type is a guess.
    imprisonment = models.SmallIntegerField()
    bal_fee_date = models.DateField(blank=True, null=True)
    pet_uid = models.BigIntegerField(blank=True, null=True)
    res_uid = models.BigIntegerField(blank=True, null=True)
    reasonregisdate = models.TextField(blank=True, null=True)
    oldcase_no = models.CharField(max_length=16, blank=True, null=True)
    performaresflag = models.TextField()  # This field type is a guess.
    reasonfilingdate = models.CharField(max_length=255, blank=True, null=True)
    oldfiling_no = models.CharField(max_length=16, blank=True, null=True)
    hide_pet_name = models.CharField(max_length=1)
    hide_res_name = models.CharField(max_length=1)
    hide_partyname = models.CharField(max_length=1)
    filcase_type = models.SmallIntegerField(blank=True, null=True)
    fil_no = models.IntegerField(blank=True, null=True)
    fil_year = models.SmallIntegerField(blank=True, null=True)
    regcase_type = models.SmallIntegerField(blank=True, null=True)
    reg_no = models.IntegerField(blank=True, null=True)
    reg_year = models.SmallIntegerField(blank=True, null=True)
    goshwara_no_o = models.SmallIntegerField()
    disp_nature_o = models.SmallIntegerField()
    archive = models.TextField()  # This field type is a guess.
    tab_status = models.CharField(max_length=25, blank=True, null=True)
    lsubject1 = models.CharField(max_length=255, blank=True, null=True)
    pending_ia = models.TextField()  # This field type is a guess.
    ia_next_date = models.DateField(blank=True, null=True)
    time_slot = models.IntegerField(blank=True, null=True)
    purpose_today = models.SmallIntegerField()
    subpurpose_today = models.SmallIntegerField()
    main_matter_cino = models.CharField(max_length=16, blank=True, null=True)
    split_case_refno = models.CharField(max_length=15, blank=True, null=True)
    split_case_flag = models.TextField()  # This field type is a guess.
    jocode = models.CharField(max_length=150, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    dormant_sinedie = models.CharField(max_length=1, blank=True, null=True)
    pet_inperson = models.CharField(max_length=1, blank=True, null=True)
    res_inperson = models.CharField(max_length=1, blank=True, null=True)
    pet_status = models.IntegerField()
    res_status = models.IntegerField()
    grouped = models.CharField(max_length=1, blank=True, null=True)
    cino = models.CharField(primary_key=True, max_length=16)
    subnature_cd1 = models.CharField(max_length=25, blank=True, null=True)
    subnature_cd2 = models.CharField(max_length=25, blank=True, null=True)
    branch_id = models.IntegerField(blank=True, null=True)
    bench_type = models.IntegerField(blank=True, null=True)
    sr_no = models.IntegerField(blank=True, null=True)
    causelist_type = models.IntegerField(blank=True, null=True)
    next_date_check = models.CharField(max_length=1, blank=True, null=True)
    status_id = models.IntegerField(blank=True, null=True)
    link_criteria = models.CharField(max_length=1, blank=True, null=True)
    c_subject = models.IntegerField(blank=True, null=True)
    cs_subject = models.IntegerField(blank=True, null=True)
    css_subject = models.IntegerField(blank=True, null=True)
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    desig_code = models.CharField(max_length=50, blank=True, null=True)
    pet_gender = models.CharField(max_length=1, blank=True, null=True)
    res_gender = models.CharField(max_length=1, blank=True, null=True)
    pet_salutation = models.SmallIntegerField(blank=True, null=True)
    res_salutation = models.SmallIntegerField(blank=True, null=True)
    case_remark = models.TextField(blank=True, null=True)
    under_obj = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    csss_subject = models.IntegerField(blank=True, null=True)
    tied_up = models.IntegerField()
    extra_link = models.TextField()  # This field type is a guess.
    ag_office = models.CharField(max_length=12, blank=True, null=True)
    afidvt = models.IntegerField(blank=True, null=True)
    connected_type = models.IntegerField(blank=True, null=True)
    link_cino = models.CharField(max_length=16, blank=True, null=True)
    bunch = models.IntegerField(blank=True, null=True)
    short_order = models.CharField(max_length=50, blank=True, null=True)
    maincase_filing_no = models.CharField(max_length=15, blank=True, null=True)
    last_status = models.CharField(max_length=1, blank=True, null=True)
    sub_cino = models.TextField(blank=True, null=True)
    vc_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    claim_juri_value = models.CharField(max_length=25)
    vehicle_regn_no = models.CharField(max_length=100, blank=True, null=True)
    license_no = models.CharField(max_length=100, blank=True, null=True)
    random_alloc = models.TextField(blank=True, null=True)  # This field type is a guess.
    regular_proc = models.TextField(blank=True, null=True)  # This field type is a guess.
    datacorrection = models.TextField(blank=True, null=True)  # This field type is a guess.
    auto_date = models.DateField(blank=True, null=True)
    auto_date_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    transfer_remark = models.TextField(blank=True, null=True)
    eflag = models.CharField(max_length=1, blank=True, null=True)
    efilno = models.CharField(unique=True, max_length=99, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    caveat_tag_date = models.DateField(blank=True, null=True)
    pet_prid = models.CharField(max_length=25, blank=True, null=True)
    res_prid = models.CharField(max_length=25, blank=True, null=True)
    send_to_vcourt = models.DateField(blank=True, null=True)
    receipt_from_vcourt = models.DateField(blank=True, null=True)
    vcourt_cnr = models.CharField(max_length=16)
    vcourt_sent_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    vcourt_receive_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    notify_court_id = models.CharField(max_length=100, blank=True, null=True)
    efiling_type = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'civil_t_a'


class CivilTDelete(models.Model):
    case_no = models.CharField(unique=True, max_length=15, blank=True, null=True)
    pet_name = models.CharField(max_length=100, blank=True, null=True)
    lpet_name = models.CharField(max_length=100, blank=True, null=True)
    pet_sex = models.CharField(max_length=1, blank=True, null=True)
    res_name = models.CharField(max_length=100, blank=True, null=True)
    lres_name = models.CharField(max_length=100, blank=True, null=True)
    res_sex = models.CharField(max_length=1, blank=True, null=True)
    court_no = models.IntegerField(blank=True, null=True)
    file_before = models.IntegerField(blank=True, null=True)
    date_of_filing = models.DateField(blank=True, null=True)
    time_of_filing = models.TimeField(blank=True, null=True)
    date_of_present = models.DateField(blank=True, null=True)
    date_first_list = models.DateField(blank=True, null=True)
    date_next_list = models.DateField(blank=True, null=True)
    date_last_list = models.DateField(blank=True, null=True)
    date_of_decision = models.DateField(blank=True, null=True)
    dec_jud_name = models.CharField(max_length=100, blank=True, null=True)
    pet_adv = models.CharField(max_length=500, blank=True, null=True)
    pet_adv_cd = models.BigIntegerField(blank=True, null=True)
    lpet_adv = models.CharField(max_length=100, blank=True, null=True)
    res_adv = models.CharField(max_length=500, blank=True, null=True)
    res_adv_cd = models.BigIntegerField(blank=True, null=True)
    lres_adv = models.CharField(max_length=100, blank=True, null=True)
    filing_no = models.CharField(unique=True, max_length=15, blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    juri_value = models.CharField(max_length=25, blank=True, null=True)
    purpose_prev = models.SmallIntegerField(blank=True, null=True)
    purpose_next = models.SmallIntegerField(blank=True, null=True)
    purpose_filing = models.CharField(max_length=255, blank=True, null=True)
    under_sec1 = models.CharField(max_length=100, blank=True, null=True)
    under_act1 = models.IntegerField(blank=True, null=True)
    under_sec2 = models.CharField(max_length=100, blank=True, null=True)
    under_act2 = models.IntegerField(blank=True, null=True)
    under_sec3 = models.CharField(max_length=100, blank=True, null=True)
    under_act3 = models.IntegerField(blank=True, null=True)
    under_sec4 = models.CharField(max_length=100, blank=True, null=True)
    under_act4 = models.IntegerField(blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    subject1 = models.CharField(max_length=255, blank=True, null=True)
    subject2 = models.CharField(max_length=255, blank=True, null=True)
    subject3 = models.CharField(max_length=255, blank=True, null=True)
    caveat = models.CharField(max_length=255, blank=True, null=True)
    order_passed = models.IntegerField(blank=True, null=True)
    order_passed1 = models.CharField(max_length=255, blank=True, null=True)
    unit = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    goshwara_no = models.SmallIntegerField(blank=True, null=True)
    lower_court_code = models.SmallIntegerField(blank=True, null=True)
    filing_case = models.SmallIntegerField(blank=True, null=True)
    lower_court = models.CharField(max_length=40, blank=True, null=True)
    lower_court_dec_dt = models.DateField(blank=True, null=True)
    deleted = models.CharField(max_length=1, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    dt_of_mod = models.DateTimeField(blank=True, null=True)
    petadd = models.TextField(blank=True, null=True)
    lpetadd = models.TextField(blank=True, null=True)
    resadd = models.TextField(blank=True, null=True)
    lresadd = models.TextField(blank=True, null=True)
    disp_nature = models.SmallIntegerField(blank=True, null=True)
    tr_from_court = models.SmallIntegerField(blank=True, null=True)
    tr_date = models.DateField(blank=True, null=True)
    pet_father_name = models.CharField(max_length=100, blank=True, null=True)
    lpet_father_name = models.CharField(max_length=100, blank=True, null=True)
    pet_father_flag = models.CharField(max_length=2, blank=True, null=True)
    pet_nationality = models.CharField(max_length=99, blank=True, null=True)
    pet_caste = models.CharField(max_length=2, blank=True, null=True)
    pet_age = models.SmallIntegerField(blank=True, null=True)
    pet_email = models.CharField(max_length=254, blank=True, null=True)
    pet_mobile = models.CharField(max_length=15, blank=True, null=True)
    pet_phone = models.CharField(max_length=15, blank=True, null=True)
    pet_fax = models.CharField(max_length=15, blank=True, null=True)
    pet_occu = models.CharField(max_length=50, blank=True, null=True)
    res_father_name = models.CharField(max_length=100, blank=True, null=True)
    lres_father_name = models.CharField(max_length=100, blank=True, null=True)
    res_father_flag = models.CharField(max_length=2, blank=True, null=True)
    res_nationality = models.CharField(max_length=99, blank=True, null=True)
    res_caste = models.CharField(max_length=2, blank=True, null=True)
    res_age = models.SmallIntegerField(blank=True, null=True)
    res_email = models.CharField(max_length=254, blank=True, null=True)
    res_mobile = models.CharField(max_length=15, blank=True, null=True)
    res_phone = models.CharField(max_length=15, blank=True, null=True)
    res_fax = models.CharField(max_length=15, blank=True, null=True)
    res_occu = models.CharField(max_length=50, blank=True, null=True)
    dt_regis = models.DateField(blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    date_filing_disp = models.DateField(blank=True, null=True)
    pet_legal_heir = models.TextField(blank=True, null=True)  # This field type is a guess.
    res_legal_heir = models.TextField(blank=True, null=True)  # This field type is a guess.
    update_date = models.DateTimeField(blank=True, null=True)
    pet_occupation = models.CharField(max_length=50, blank=True, null=True)
    res_occupation = models.CharField(max_length=50, blank=True, null=True)
    police_st_code = models.IntegerField(blank=True, null=True)
    fir_no = models.CharField(max_length=100, blank=True, null=True)
    fir_type_code = models.SmallIntegerField(blank=True, null=True)
    fir_year = models.SmallIntegerField(blank=True, null=True)
    session_magistrate = models.SmallIntegerField(blank=True, null=True)
    police_private = models.SmallIntegerField(blank=True, null=True)
    ci_cri = models.SmallIntegerField(blank=True, null=True)
    offense_date = models.DateField(blank=True, null=True)
    dt_chargesheet = models.DateField(blank=True, null=True)
    link_code = models.CharField(max_length=15, blank=True, null=True)
    reason_for_rej = models.TextField(blank=True, null=True)
    lreason_for_rej = models.TextField(blank=True, null=True)
    not_before_me = models.CharField(max_length=50, blank=True, null=True)
    before_me = models.CharField(max_length=50, blank=True, null=True)
    obj_redate = models.DateField(blank=True, null=True)
    obj_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    objreceipt_dt = models.DateField(blank=True, null=True)
    objreturn_dt = models.DateField(blank=True, null=True)
    objprepare_dt = models.DateField(blank=True, null=True)
    objection = models.TextField(blank=True, null=True)
    objdescription = models.TextField(blank=True, null=True)
    lobjection = models.CharField(max_length=250, blank=True, null=True)
    date_filing_disp_o = models.DateField(blank=True, null=True)
    date_filing_restore = models.DateField(blank=True, null=True)
    date_of_decision_o = models.DateField(blank=True, null=True)
    date_of_revoke = models.DateField(blank=True, null=True)
    urgent = models.TextField(blank=True, null=True)  # This field type is a guess.
    main_case_no = models.CharField(max_length=15, blank=True, null=True)
    pet_add2 = models.CharField(max_length=255, blank=True, null=True)
    lpet_add2 = models.CharField(max_length=255, blank=True, null=True)
    dist_code = models.SmallIntegerField(blank=True, null=True)
    taluka_code = models.SmallIntegerField(blank=True, null=True)
    village_code = models.IntegerField(blank=True, null=True)
    village1_code = models.IntegerField(blank=True, null=True)
    village2_code = models.IntegerField(blank=True, null=True)
    town_code = models.IntegerField(blank=True, null=True)
    ward_code = models.IntegerField(blank=True, null=True)
    res_dist = models.SmallIntegerField(blank=True, null=True)
    res_taluka = models.SmallIntegerField(blank=True, null=True)
    res_village = models.IntegerField(blank=True, null=True)
    res_village1 = models.IntegerField(blank=True, null=True)
    res_village2 = models.IntegerField(blank=True, null=True)
    res_town_code = models.IntegerField(blank=True, null=True)
    res_ward_code = models.IntegerField(blank=True, null=True)
    res_add2 = models.CharField(max_length=255, blank=True, null=True)
    lres_add2 = models.CharField(max_length=255, blank=True, null=True)
    dist_code3 = models.SmallIntegerField(blank=True, null=True)
    taluka_code3 = models.SmallIntegerField(blank=True, null=True)
    village_code3 = models.IntegerField(blank=True, null=True)
    village1_code3 = models.IntegerField(blank=True, null=True)
    village2_code3 = models.IntegerField(blank=True, null=True)
    town_code3 = models.IntegerField(blank=True, null=True)
    ward_code3 = models.IntegerField(blank=True, null=True)
    dist_code4 = models.SmallIntegerField(blank=True, null=True)
    taluka_code4 = models.SmallIntegerField(blank=True, null=True)
    village_code4 = models.IntegerField(blank=True, null=True)
    village1_code4 = models.IntegerField(blank=True, null=True)
    village2_code4 = models.IntegerField(blank=True, null=True)
    town_code4 = models.IntegerField(blank=True, null=True)
    ward_code4 = models.IntegerField(blank=True, null=True)
    chk = models.CharField(max_length=50, blank=True, null=True)
    pet_passportno = models.CharField(max_length=25, blank=True, null=True)
    pet_country = models.CharField(max_length=99, blank=True, null=True)
    pet_pincode = models.IntegerField(blank=True, null=True)
    res_passportno = models.CharField(max_length=25, blank=True, null=True)
    res_country = models.CharField(max_length=99, blank=True, null=True)
    res_pincode = models.IntegerField(blank=True, null=True)
    reg_pl = models.CharField(max_length=1, blank=True, null=True)
    orgid = models.SmallIntegerField(blank=True, null=True)
    resorgid = models.SmallIntegerField(blank=True, null=True)
    pet_dob = models.DateField(blank=True, null=True)
    res_dob = models.DateField(blank=True, null=True)
    plead_guilty = models.TextField(blank=True, null=True)  # This field type is a guess.
    nature_cd = models.CharField(max_length=25, blank=True, null=True)
    relief_offense = models.TextField(blank=True, null=True)
    lrelief_offence = models.TextField(blank=True, null=True)
    causeofaction = models.TextField(blank=True, null=True)
    lcauseofaction = models.TextField(blank=True, null=True)
    legacy_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    pet_extracount = models.IntegerField(blank=True, null=True)
    res_extracount = models.IntegerField(blank=True, null=True)
    order_sect_kar = models.TextField(blank=True, null=True)
    nature_kar = models.TextField(blank=True, null=True)
    allocation_dt = models.DateField(blank=True, null=True)
    rej_sr_no = models.IntegerField(blank=True, null=True)
    unit_type = models.CharField(max_length=150, blank=True, null=True)
    unit_type_value = models.CharField(max_length=150, blank=True, null=True)
    transfer_est = models.TextField(blank=True, null=True)  # This field type is a guess.
    imprisonment = models.SmallIntegerField(blank=True, null=True)
    bal_fee_date = models.DateField(blank=True, null=True)
    pet_uid = models.BigIntegerField(blank=True, null=True)
    res_uid = models.BigIntegerField(blank=True, null=True)
    reasonregisdate = models.TextField(blank=True, null=True)
    oldcase_no = models.CharField(max_length=16, blank=True, null=True)
    performaresflag = models.TextField(blank=True, null=True)  # This field type is a guess.
    petpanno = models.CharField(max_length=10, blank=True, null=True)
    respanno = models.CharField(max_length=10, blank=True, null=True)
    reasonfilingdate = models.CharField(max_length=255, blank=True, null=True)
    oldfiling_no = models.CharField(max_length=16, blank=True, null=True)
    hide_pet_name = models.CharField(max_length=1, blank=True, null=True)
    hide_res_name = models.CharField(max_length=1, blank=True, null=True)
    hide_partyname = models.CharField(max_length=1, blank=True, null=True)
    petpolice_st_code = models.IntegerField(blank=True, null=True)
    respolice_st_code = models.IntegerField(blank=True, null=True)
    investofficer = models.CharField(max_length=100, blank=True, null=True)
    linvestofficer = models.CharField(max_length=100, blank=True, null=True)
    beltno = models.CharField(max_length=50, blank=True, null=True)
    investofficer1 = models.CharField(max_length=100, blank=True, null=True)
    linvestofficer1 = models.CharField(max_length=100, blank=True, null=True)
    beltno1 = models.CharField(max_length=50, blank=True, null=True)
    pet_org_contact_person = models.CharField(max_length=100, blank=True, null=True)
    petorg_person = models.CharField(max_length=100, blank=True, null=True)
    res_org_contact_person = models.CharField(max_length=100, blank=True, null=True)
    resorg_person = models.CharField(max_length=100, blank=True, null=True)
    filcase_type = models.SmallIntegerField(blank=True, null=True)
    fil_no = models.IntegerField(blank=True, null=True)
    fil_year = models.SmallIntegerField(blank=True, null=True)
    regcase_type = models.SmallIntegerField(blank=True, null=True)
    reg_no = models.IntegerField(blank=True, null=True)
    reg_year = models.SmallIntegerField(blank=True, null=True)
    goshwara_no_o = models.SmallIntegerField(blank=True, null=True)
    disp_nature_o = models.SmallIntegerField(blank=True, null=True)
    archive = models.TextField(blank=True, null=True)  # This field type is a guess.
    tab_status = models.CharField(max_length=25, blank=True, null=True)
    lsubject1 = models.CharField(max_length=255, blank=True, null=True)
    pending_ia = models.TextField(blank=True, null=True)  # This field type is a guess.
    ia_next_date = models.DateField(blank=True, null=True)
    time_slot = models.IntegerField(blank=True, null=True)
    pet_ph = models.TextField(blank=True, null=True)  # This field type is a guess.
    res_ph = models.TextField(blank=True, null=True)  # This field type is a guess.
    purpose_today = models.SmallIntegerField(blank=True, null=True)
    subpurpose_today = models.SmallIntegerField(blank=True, null=True)
    main_matter_cino = models.CharField(max_length=16, blank=True, null=True)
    lcc_applied_date = models.DateField(blank=True, null=True)
    lcc_received_date = models.DateField(blank=True, null=True)
    split_case_refno = models.CharField(max_length=15, blank=True, null=True)
    split_case_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    jocode = models.CharField(max_length=150, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    dormant_sinedie = models.CharField(max_length=1, blank=True, null=True)
    pet_inperson = models.CharField(max_length=1, blank=True, null=True)
    res_inperson = models.CharField(max_length=1, blank=True, null=True)
    pet_status = models.IntegerField(blank=True, null=True)
    res_status = models.IntegerField(blank=True, null=True)
    lower_judge_name = models.CharField(max_length=100, blank=True, null=True)
    lowerjocode = models.CharField(max_length=150, blank=True, null=True)
    grouped = models.CharField(max_length=1, blank=True, null=True)
    lpet_occu = models.CharField(max_length=50, blank=True, null=True)
    lres_occu = models.CharField(max_length=50, blank=True, null=True)
    cino = models.CharField(primary_key=True, max_length=16)
    lower_cino = models.CharField(max_length=16, blank=True, null=True)
    subnature_cd1 = models.CharField(max_length=25, blank=True, null=True)
    subnature_cd2 = models.CharField(max_length=25, blank=True, null=True)
    branch_id = models.IntegerField(blank=True, null=True)
    bench_type = models.IntegerField(blank=True, null=True)
    sr_no = models.IntegerField(blank=True, null=True)
    causelist_type = models.IntegerField(blank=True, null=True)
    next_date_check = models.CharField(max_length=1, blank=True, null=True)
    status_id = models.IntegerField(blank=True, null=True)
    lower_dist_code = models.IntegerField(blank=True, null=True)
    lregis_date = models.DateField(blank=True, null=True)
    lower_taluka_code = models.IntegerField(blank=True, null=True)
    link_criteria = models.CharField(max_length=1, blank=True, null=True)
    c_subject = models.IntegerField(blank=True, null=True)
    cs_subject = models.IntegerField(blank=True, null=True)
    css_subject = models.IntegerField(blank=True, null=True)
    police_state_id = models.IntegerField(blank=True, null=True)
    police_dist_code = models.IntegerField(blank=True, null=True)
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    desig_code = models.CharField(max_length=50, blank=True, null=True)
    case_state_code = models.IntegerField(blank=True, null=True)
    case_dist_code = models.IntegerField(blank=True, null=True)
    pet_gender = models.CharField(max_length=1, blank=True, null=True)
    res_gender = models.CharField(max_length=1, blank=True, null=True)
    pet_salutation = models.SmallIntegerField(blank=True, null=True)
    res_salutation = models.SmallIntegerField(blank=True, null=True)
    case_remark = models.TextField(blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    res_state_id = models.IntegerField(blank=True, null=True)
    state_id3 = models.IntegerField(blank=True, null=True)
    state_id4 = models.IntegerField(blank=True, null=True)
    lower_state_id = models.IntegerField(blank=True, null=True)
    csss_subject = models.IntegerField(blank=True, null=True)
    tied_up = models.IntegerField(blank=True, null=True)
    extra_link = models.TextField(blank=True, null=True)  # This field type is a guess.
    ag_office = models.CharField(max_length=12, blank=True, null=True)
    afidvt = models.IntegerField(blank=True, null=True)
    connected_type = models.IntegerField(blank=True, null=True)
    link_cino = models.CharField(max_length=16, blank=True, null=True)
    bunch = models.IntegerField(blank=True, null=True)
    short_order = models.CharField(max_length=50, blank=True, null=True)
    maincase_filing_no = models.CharField(max_length=15, blank=True, null=True)
    last_status = models.CharField(max_length=1, blank=True, null=True)
    sub_cino = models.TextField(blank=True, null=True)
    vc_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    claim_juri_value = models.CharField(max_length=25, blank=True, null=True)
    ljudid = models.IntegerField(blank=True, null=True)
    judg_local_lang = models.TextField(blank=True, null=True)  # This field type is a guess.
    vehicle_regn_no = models.CharField(max_length=100, blank=True, null=True)
    license_no = models.CharField(max_length=100, blank=True, null=True)
    random_alloc = models.TextField(blank=True, null=True)  # This field type is a guess.
    regular_proc = models.TextField(blank=True, null=True)  # This field type is a guess.
    datacorrection = models.TextField(blank=True, null=True)  # This field type is a guess.
    auto_date = models.DateField(blank=True, null=True)
    auto_date_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    transfer_remark = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    eflag = models.CharField(max_length=1, blank=True, null=True)
    efilno = models.CharField(max_length=99, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'civil_t_delete'


class CivilTransfer(models.Model):
    pk = models.CompositePrimaryKey('cino', 'from_court_no', 'to_court_no', 'transdate')
    case_no = models.CharField(max_length=15)
    from_court_no = models.SmallIntegerField()
    to_court_no = models.SmallIntegerField()
    transdate = models.DateField()
    oldfiling_no = models.CharField(max_length=16, blank=True, null=True)
    oldcase_no = models.CharField(max_length=16, blank=True, null=True)
    jocodefrom = models.CharField(max_length=150, blank=True, null=True)
    jocodeto = models.CharField(max_length=150, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'civil_transfer'


class CivilTransferA(models.Model):
    pk = models.CompositePrimaryKey('cino', 'from_court_no', 'to_court_no', 'transdate')
    case_no = models.CharField(max_length=15)
    from_court_no = models.SmallIntegerField()
    to_court_no = models.SmallIntegerField()
    transdate = models.DateField()
    oldfiling_no = models.CharField(max_length=16, blank=True, null=True)
    oldcase_no = models.CharField(max_length=16, blank=True, null=True)
    jocodefrom = models.CharField(max_length=150, blank=True, null=True)
    jocodeto = models.CharField(max_length=150, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'civil_transfer_a'


class ConnectedMaster(models.Model):
    connected_id = models.IntegerField(primary_key=True)
    connected_type = models.CharField(max_length=255, blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'connected_master'


class ConnectedT(models.Model):
    pk = models.CompositePrimaryKey('cino', 'linkcino')
    cino = models.CharField(max_length=16)
    linkcino = models.CharField(max_length=16)
    disposed = models.TextField(blank=True, null=True)  # This field type is a guess.
    case_no = models.CharField(max_length=15, blank=True, null=True)
    linkcase_no = models.CharField(max_length=15, blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)
    connected_type = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    conn_srno = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'connected_t'


class Consignment(models.Model):
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    pages = models.CharField(max_length=15, blank=True, null=True)
    dispatch_reg_no = models.CharField(max_length=15, blank=True, null=True)
    date_of_dispatch = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'consignment'


class ConvictedT(models.Model):
    pk = models.CompositePrimaryKey('cino', 'party_id', 'type', 'act_code')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    type = models.CharField(max_length=5)
    party_id = models.SmallIntegerField()
    party_name = models.CharField(max_length=100, blank=True, null=True)
    convicted = models.TextField()  # This field type is a guess.
    punish_year = models.SmallIntegerField()
    punish_month = models.SmallIntegerField()
    punish_day = models.SmallIntegerField()
    disposal_date = models.DateField()
    cino = models.CharField(max_length=16)
    act_code = models.BigIntegerField()
    act_section = models.CharField(max_length=250, blank=True, null=True)
    probation = models.TextField()  # This field type is a guess.
    life = models.TextField()  # This field type is a guess.
    death = models.TextField()  # This field type is a guess.
    amount = models.DecimalField(max_digits=17, decimal_places=2)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    compensation = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'convicted_t'


class CopyingA(models.Model):
    pk = models.CompositePrimaryKey('register_no', 'appl_no', 'appl_date', 'type')
    register_no = models.SmallIntegerField()
    appl_no = models.IntegerField()
    appl_date = models.DateField()
    sr_no = models.IntegerField()
    form_a_book = models.IntegerField()
    form_a_receipt = models.IntegerField()
    form_a_date = models.DateField(blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    type = models.SmallIntegerField()
    reg_flag = models.CharField(max_length=1)
    bank_code = models.CharField(max_length=15, blank=True, null=True)
    paymode = models.SmallIntegerField()
    dd_num = models.IntegerField()
    dd_date = models.DateField(blank=True, null=True)
    user_login = models.CharField(max_length=20, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    transid1 = models.CharField(max_length=30, blank=True, null=True)
    transid2 = models.CharField(max_length=30, blank=True, null=True)
    transid3 = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'copying_a'


class CopyingMultimode(models.Model):
    pk = models.CompositePrimaryKey('appl_no', 'appl_date', 'register_no', 'multimode_id')
    appl_no = models.IntegerField()
    appl_date = models.DateField()
    register_no = models.SmallIntegerField()
    receipt_no = models.BigIntegerField()
    receipt_date = models.DateField(blank=True, null=True)
    multimode_id = models.SmallIntegerField()
    dd_bank_code = models.CharField(max_length=15, blank=True, null=True)
    dd_no = models.IntegerField()
    dd_date = models.DateField(blank=True, null=True)
    dd_amount = models.DecimalField(max_digits=17, decimal_places=2)
    cheque_bank_code = models.CharField(max_length=15, blank=True, null=True)
    cheque_no = models.BigIntegerField()
    cheque_date = models.DateField(blank=True, null=True)
    cheque_amount = models.DecimalField(max_digits=17, decimal_places=2)
    challan_bank_code = models.CharField(max_length=15, blank=True, null=True)
    challan_no = models.BigIntegerField()
    challan_date = models.DateField(blank=True, null=True)
    challan_amount = models.DecimalField(max_digits=17, decimal_places=2)
    stamp_amount = models.DecimalField(max_digits=17, decimal_places=2)
    stamp_remarks = models.CharField(max_length=50, blank=True, null=True)
    cash_amount = models.DecimalField(max_digits=17, decimal_places=2)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'copying_multimode'


class CopyingPartialstruckoff(models.Model):
    pk = models.CompositePrimaryKey('register_no', 'appl_no', 'appl_date')
    register_no = models.SmallIntegerField()
    appl_no = models.IntegerField()
    appl_date = models.DateField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    document_reqd = models.TextField(blank=True, null=True)
    no_of_pages = models.SmallIntegerField()
    act_no_of_pages = models.SmallIntegerField()
    no_of_copies = models.TextField(blank=True, null=True)
    nopages = models.TextField(blank=True, null=True)
    original_no_of_copies = models.TextField(blank=True, null=True)
    struck_date = models.DateField(blank=True, null=True)
    struck_attempt = models.SmallIntegerField()
    restore_date = models.DateField(blank=True, null=True)
    form_a_receipt = models.BigIntegerField()
    form_a_date = models.DateField(blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2)
    ready_date = models.DateField(blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)
    receiver = models.CharField(max_length=99, blank=True, null=True)
    njstamp = models.DecimalField(max_digits=17, decimal_places=2)
    cino = models.CharField(max_length=16, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'copying_partialstruckoff'


class CopyingReturnT(models.Model):
    pk = models.CompositePrimaryKey('register_no', 'appl_no', 'appl_date')
    register_no = models.SmallIntegerField()
    appl_no = models.IntegerField()
    appl_date = models.DateField()
    return_amt = models.DecimalField(max_digits=17, decimal_places=2)
    user_login = models.CharField(max_length=20, blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'copying_return_t'


class CopyingT(models.Model):
    pk = models.CompositePrimaryKey('register_no', 'appl_no', 'appl_date')
    paid_unpaid = models.SmallIntegerField()
    register_no = models.SmallIntegerField()
    appl_no = models.IntegerField()
    appl_date = models.DateField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    appl_name = models.CharField(max_length=100, blank=True, null=True)
    lappl_name = models.CharField(max_length=100, blank=True, null=True)
    through_name = models.CharField(max_length=100, blank=True, null=True)
    lthrough_name = models.CharField(max_length=100, blank=True, null=True)
    appl_address = models.TextField(blank=True, null=True)
    lappl_address = models.TextField(blank=True, null=True)
    document_reqd = models.TextField(blank=True, null=True)
    no_of_pages = models.IntegerField()
    urg_ord = models.TextField()  # This field type is a guess.
    est_amt = models.DecimalField(max_digits=17, decimal_places=2)
    court_fees = models.IntegerField()
    est_date = models.DateField(blank=True, null=True)
    ready = models.TextField()  # This field type is a guess.
    receiver = models.CharField(max_length=255, blank=True, null=True)
    lreceiver = models.CharField(max_length=99, blank=True, null=True)
    date_of_del = models.DateField(blank=True, null=True)
    court_no = models.IntegerField()
    act_no_of_pages = models.IntegerField()
    actual_amt = models.DecimalField(max_digits=17, decimal_places=2)
    refund = models.DecimalField(max_digits=17, decimal_places=2)
    re_refund = models.DecimalField(max_digits=17, decimal_places=2)
    deposit = models.DecimalField(max_digits=17, decimal_places=2)
    cancel = models.TextField()  # This field type is a guess.
    ci_cri = models.SmallIntegerField()
    no_of_copies = models.TextField(blank=True, null=True)
    bank_code = models.CharField(max_length=15, blank=True, null=True)
    paymode = models.SmallIntegerField()
    dd_num = models.IntegerField()
    dd_date = models.DateField(blank=True, null=True)
    nature_of_def = models.TextField(blank=True, null=True)
    rect_date = models.DateField(blank=True, null=True)
    notifying_date = models.DateField(blank=True, null=True)
    date_for_rectification = models.DateField(blank=True, null=True)
    nopages = models.TextField(blank=True, null=True)
    status_date = models.DateField(blank=True, null=True)
    re_status_date = models.DateField(blank=True, null=True)
    appl_type = models.SmallIntegerField()
    def_ret_date = models.DateField(blank=True, null=True)
    re_def_ret_date = models.DateField(blank=True, null=True)
    rej_date = models.DateField(blank=True, null=True)
    reason = models.CharField(max_length=50, blank=True, null=True)
    rej_flag = models.TextField()  # This field type is a guess.
    lower_court_code = models.SmallIntegerField()
    lowerappl_no = models.IntegerField()
    lowerappl_no_year = models.SmallIntegerField()
    transdate = models.DateField(blank=True, null=True)
    recvdate = models.DateField(blank=True, null=True)
    ap_ready_date = models.DateField(blank=True, null=True)
    struck_off = models.TextField()  # This field type is a guess.
    struck_date = models.DateField(blank=True, null=True)
    oldstruckoff_rejdate = models.DateField(blank=True, null=True)
    oldstruck_off = models.TextField(blank=True, null=True)  # This field type is a guess.
    struckoff_rejrestoredate = models.DateField(blank=True, null=True)
    struckremark = models.CharField(max_length=100, blank=True, null=True)
    partial_struckflag = models.TextField(blank=True, null=True)  # This field type is a guess.
    partial_attempt = models.SmallIntegerField()
    stampremark = models.CharField(max_length=100, blank=True, null=True)
    est_db = models.CharField(max_length=255, blank=True, null=True)
    est_type = models.SmallIntegerField()
    est_name = models.CharField(max_length=255, blank=True, null=True)
    statusremark = models.CharField(max_length=200, blank=True, null=True)
    pay_def_dt = models.DateField(blank=True, null=True)
    njstamp = models.DecimalField(max_digits=17, decimal_places=2)
    mobile_no = models.CharField(max_length=15, blank=True, null=True)
    user_login = models.CharField(max_length=20, blank=True, null=True)
    adv_cd = models.BigIntegerField()
    email = models.CharField(max_length=254, blank=True, null=True)
    desgname = models.CharField(max_length=255, blank=True, null=True)
    ldesgname = models.CharField(max_length=255, blank=True, null=True)
    next_date = models.DateField(blank=True, null=True)
    date_of_decision = models.DateField(blank=True, null=True)
    pet_name = models.CharField(max_length=100, blank=True, null=True)
    lpet_name = models.CharField(max_length=100, blank=True, null=True)
    res_name = models.CharField(max_length=100, blank=True, null=True)
    lres_name = models.CharField(max_length=100, blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'copying_t'


class CourtFeesMaster(models.Model):
    sr_no = models.SmallIntegerField(primary_key=True)
    casetype_id = models.SmallIntegerField()
    min_fee = models.BigIntegerField()
    max_fee = models.BigIntegerField()
    formula = models.TextField(blank=True, null=True)
    fix_amount = models.IntegerField()
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'court_fees_master'


class CourtName(models.Model):
    court_name = models.CharField(max_length=100, blank=True, null=True)
    lcourt_name = models.CharField(max_length=100, blank=True, null=True)
    app_court_type = models.TextField()  # This field type is a guess.
    mode_of_filing = models.SmallIntegerField()
    state = models.CharField(max_length=20, blank=True, null=True)
    district = models.CharField(max_length=20, blank=True, null=True)
    taluka = models.CharField(max_length=20, blank=True, null=True)
    version = models.CharField(max_length=50, blank=True, null=True)
    versionname = models.CharField(max_length=50, blank=True, null=True)
    lversionname = models.CharField(max_length=50, blank=True, null=True)
    ci_type_code = models.SmallIntegerField()
    cri_type_code = models.SmallIntegerField()
    civ_filing_no = models.CharField(max_length=7, blank=True, null=True)
    cri_filing_no = models.CharField(max_length=7, blank=True, null=True)
    courtfeeno = models.IntegerField()
    patch = models.CharField(max_length=500, blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    summons_id = models.SmallIntegerField()
    fee_receipt_id = models.SmallIntegerField()
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    mode_of_copying = models.SmallIntegerField()
    mode_of_nazarat = models.SmallIntegerField()
    hide_partyname = models.CharField(max_length=1)
    time_migration = models.TimeField(blank=True, null=True)
    date_migration = models.DateField(blank=True, null=True)
    est_code = models.CharField(primary_key=True, max_length=6)
    state_code = models.SmallIntegerField(blank=True, null=True)
    jo_prefix = models.CharField(max_length=5, blank=True, null=True)
    lang_id = models.SmallIntegerField()
    lang_name = models.CharField(max_length=255, blank=True, null=True)
    lang_flag = models.SmallIntegerField()
    civil_year = models.SmallIntegerField()
    criminal_year = models.SmallIntegerField()
    est_id = models.SmallIntegerField()
    caveat_fil_no = models.IntegerField()
    caveat_fil_year = models.SmallIntegerField()
    caveat_reg_no = models.IntegerField()
    caveat_reg_year = models.SmallIntegerField()
    lstate = models.CharField(max_length=50, blank=True, null=True)
    ci_year = models.SmallIntegerField()
    state_lang = models.CharField(max_length=99, blank=True, null=True)
    orgid = models.SmallIntegerField()
    cino = models.IntegerField(blank=True, null=True)
    hcdc = models.IntegerField(blank=True, null=True)
    cav_admiral_year = models.SmallIntegerField(blank=True, null=True)
    cav_admiral_reg_no = models.IntegerField(blank=True, null=True)
    extra_state = models.CharField(max_length=10, blank=True, null=True)
    lang_code = models.SmallIntegerField(blank=True, null=True)
    writ_no = models.IntegerField(blank=True, null=True)
    writ_year = models.IntegerField(blank=True, null=True)
    normal_v = models.CharField(max_length=5, blank=True, null=True)
    caveat_cino = models.IntegerField(blank=True, null=True)
    caveat_cino_year = models.SmallIntegerField(blank=True, null=True)
    ptn = models.IntegerField()
    ptn_year = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    hc_citation_abbr = models.CharField(max_length=9, blank=True, null=True)
    citation_cutoffdate = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'court_name'


class CourtT(models.Model):
    court_no = models.IntegerField(primary_key=True)
    room_no = models.CharField(max_length=20, blank=True, null=True)
    courtfiling = models.TextField()  # This field type is a guess.
    noprefix = models.SmallIntegerField(blank=True, null=True)
    principle_court = models.TextField()  # This field type is a guess.
    display = models.TextField()  # This field type is a guess.
    bench_type_code = models.IntegerField(blank=True, null=True)
    bench_desc = models.CharField(max_length=500, blank=True, null=True)
    bench_section = models.TextField(blank=True, null=True)  # This field type is a guess.
    cfrom_dt = models.DateField(blank=True, null=True)
    cto_dt = models.DateField(blank=True, null=True)
    case_types = models.CharField(max_length=1000, blank=True, null=True)
    court_id = models.CharField(max_length=15, blank=True, null=True)
    roaster_desc = models.TextField(blank=True, null=True)
    unique_court = models.CharField(max_length=15, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'court_t'


class Courtfiling(models.Model):
    court_no = models.IntegerField()
    case_type = models.SmallIntegerField()
    regcase_type = models.SmallIntegerField()
    filing_no = models.IntegerField()
    cri_filing_no = models.IntegerField()
    filing_year = models.SmallIntegerField()
    reg_no = models.IntegerField()
    reg_year = models.SmallIntegerField()
    plead_gulity = models.CharField(max_length=1, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'courtfiling'


class CriminalProcess(models.Model):
    pk = models.CompositePrimaryKey('rec_no', 'rec_year')
    cino = models.CharField(max_length=16)
    case_no = models.CharField(max_length=255, blank=True, null=True)
    filing_no = models.CharField(max_length=255, blank=True, null=True)
    date_first_list = models.DateField(blank=True, null=True)
    dt_regis = models.DateField(blank=True, null=True)
    date_of_filing = models.DateField(blank=True, null=True)
    date_of_decision = models.DateField(blank=True, null=True)
    next_date = models.DateField(blank=True, null=True)
    todays_date = models.DateField(blank=True, null=True)
    pet_name = models.CharField(max_length=100, blank=True, null=True)
    res_name = models.CharField(max_length=100, blank=True, null=True)
    pet_add = models.TextField(blank=True, null=True)
    res_add = models.TextField(blank=True, null=True)
    pet_age = models.SmallIntegerField()
    res_age = models.SmallIntegerField()
    prev_purpose = models.CharField(max_length=100, blank=True, null=True)
    next_purpose = models.CharField(max_length=100, blank=True, null=True)
    sub_purpose = models.CharField(max_length=100, blank=True, null=True)
    disposal_type = models.CharField(max_length=100, blank=True, null=True)
    nature = models.CharField(max_length=500, blank=True, null=True)
    lower_case_no = models.CharField(max_length=255, blank=True, null=True)
    lower_court_name = models.CharField(max_length=255, blank=True, null=True)
    lower_disp_date = models.DateField(blank=True, null=True)
    relief_offense = models.TextField(blank=True, null=True)
    cause_of_action = models.TextField(blank=True, null=True)
    offense_date = models.DateField(blank=True, null=True)
    under_act1 = models.CharField(max_length=100, blank=True, null=True)
    under_sec1 = models.CharField(max_length=100, blank=True, null=True)
    under_act2 = models.CharField(max_length=100, blank=True, null=True)
    under_sec2 = models.CharField(max_length=100, blank=True, null=True)
    under_act3 = models.CharField(max_length=100, blank=True, null=True)
    under_sec3 = models.CharField(max_length=100, blank=True, null=True)
    under_act4 = models.CharField(max_length=100, blank=True, null=True)
    under_sec4 = models.CharField(max_length=100, blank=True, null=True)
    court_name = models.CharField(max_length=100, blank=True, null=True)
    desg_name = models.CharField(max_length=500, blank=True, null=True)
    judge_name = models.CharField(max_length=500, blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    police_stn = models.CharField(max_length=100, blank=True, null=True)
    fir_no = models.CharField(max_length=100, blank=True, null=True)
    fir_year = models.SmallIntegerField(blank=True, null=True)
    main_case_no = models.CharField(max_length=255, blank=True, null=True)
    maincase_dtregis = models.DateField(blank=True, null=True)
    process_fees = models.IntegerField()
    fees_type = models.CharField(max_length=1, blank=True, null=True)
    receipt_no = models.CharField(max_length=50, blank=True, null=True)
    receipt_year = models.CharField(max_length=50, blank=True, null=True)
    receipt_dates = models.CharField(max_length=255, blank=True, null=True)
    fee = models.CharField(max_length=100, blank=True, null=True)
    recv_name = models.CharField(max_length=100, blank=True, null=True)
    recv_fathername = models.CharField(max_length=100, blank=True, null=True)
    recv_address = models.TextField(blank=True, null=True)
    recvaddress_type = models.TextField()  # This field type is a guess.
    ns_id = models.BigIntegerField()
    recv_state = models.CharField(max_length=100, blank=True, null=True)
    recv_district = models.CharField(max_length=100, blank=True, null=True)
    recv_taluka = models.CharField(max_length=100, blank=True, null=True)
    recv_village = models.CharField(max_length=100, blank=True, null=True)
    recv_town = models.CharField(max_length=100, blank=True, null=True)
    recv_ward = models.CharField(max_length=100, blank=True, null=True)
    recv_village1 = models.CharField(max_length=100, blank=True, null=True)
    recv_village2 = models.CharField(max_length=100, blank=True, null=True)
    recv_mobile = models.CharField(max_length=15, blank=True, null=True)
    recv_pincode = models.CharField(max_length=15, blank=True, null=True)
    receiver_age = models.SmallIntegerField()
    recv_adv = models.CharField(max_length=100, blank=True, null=True)
    party_no = models.SmallIntegerField()
    party_type = models.CharField(max_length=5, blank=True, null=True)
    server_date = models.DateField(blank=True, null=True)
    session_date = models.DateField(blank=True, null=True)
    draft_date = models.DateField(blank=True, null=True)
    ns_date = models.DateField(blank=True, null=True)
    label1 = models.CharField(max_length=150, blank=True, null=True)
    label2 = models.CharField(max_length=150, blank=True, null=True)
    label3 = models.CharField(max_length=150, blank=True, null=True)
    label4 = models.CharField(max_length=150, blank=True, null=True)
    label5 = models.CharField(max_length=150, blank=True, null=True)
    ns_title = models.CharField(max_length=255, blank=True, null=True)
    process_id = models.CharField(max_length=25, blank=True, null=True)
    rec_no = models.BigIntegerField()
    rec_year = models.BigIntegerField()
    recv_email = models.CharField(max_length=99, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    pet_father_name = models.CharField(max_length=99, blank=True, null=True)
    pet_father_flag = models.CharField(max_length=2, blank=True, null=True)
    res_father_name = models.CharField(max_length=99, blank=True, null=True)
    res_father_flag = models.CharField(max_length=2, blank=True, null=True)
    court_no = models.IntegerField(blank=True, null=True)
    recv_state_id = models.IntegerField()
    recv_district_id = models.IntegerField()
    recv_taluka_id = models.IntegerField()
    recv_village_id = models.IntegerField()
    recv_village1_id = models.IntegerField()
    recv_village2_id = models.IntegerField()
    recv_town_id = models.IntegerField()
    recv_ward_id = models.IntegerField()
    police_st_code = models.IntegerField(blank=True, null=True)
    court_process_id = models.SmallIntegerField()
    recv_police_stn = models.CharField(max_length=100, blank=True, null=True)
    recv_state_census = models.IntegerField()
    recv_district_census = models.IntegerField()
    recv_taluka_census = models.IntegerField()
    recv_village_census = models.IntegerField()
    recv_town_census = models.IntegerField()
    recv_ward_census = models.IntegerField()
    recv_village1_census = models.IntegerField()
    recv_village2_census = models.IntegerField()
    recv_police_st_census = models.CharField(max_length=10, blank=True, null=True)
    srno = models.BigIntegerField(blank=True, null=True)
    year = models.BigIntegerField(blank=True, null=True)
    regcase_type = models.SmallIntegerField(blank=True, null=True)
    reg_no = models.IntegerField(blank=True, null=True)
    reg_year = models.SmallIntegerField(blank=True, null=True)
    filcase_type = models.SmallIntegerField(blank=True, null=True)
    fil_no = models.IntegerField(blank=True, null=True)
    fil_year = models.SmallIntegerField(blank=True, null=True)
    recv_father_flag = models.CharField(max_length=2, blank=True, null=True)
    label6 = models.CharField(max_length=150, blank=True, null=True)
    label7 = models.CharField(max_length=150, blank=True, null=True)
    label8 = models.CharField(max_length=150, blank=True, null=True)
    label9 = models.CharField(max_length=150, blank=True, null=True)
    label10 = models.CharField(max_length=150, blank=True, null=True)
    date1 = models.DateField(blank=True, null=True)
    date2 = models.DateField(blank=True, null=True)
    date3 = models.DateField(blank=True, null=True)
    date4 = models.DateField(blank=True, null=True)
    date5 = models.DateField(blank=True, null=True)
    lower_state_id = models.IntegerField(blank=True, null=True)
    lower_taluka_code = models.IntegerField(blank=True, null=True)
    lower_court_code = models.SmallIntegerField(blank=True, null=True)
    lower_trial = models.SmallIntegerField(blank=True, null=True)
    lower_cino = models.CharField(max_length=16, blank=True, null=True)
    lower_judge_name = models.CharField(max_length=100, blank=True, null=True)
    lower_court = models.CharField(max_length=40, blank=True, null=True)
    juri_value = models.CharField(max_length=25, blank=True, null=True)
    main_matter_cino = models.CharField(max_length=16, blank=True, null=True)
    police_private = models.SmallIntegerField(blank=True, null=True)
    police_state_id = models.SmallIntegerField(blank=True, null=True)
    police_dist_code = models.SmallIntegerField(blank=True, null=True)
    police_stn_code = models.IntegerField(blank=True, null=True)
    foot_note = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    nature_cd = models.CharField(max_length=25, blank=True, null=True)
    lower_state_census = models.IntegerField()
    lower_taluka_census = models.IntegerField()
    police_state_census = models.IntegerField()
    police_dist_census = models.IntegerField()
    police_st_census = models.IntegerField()
    process_no = models.SmallIntegerField()
    subprocess_no = models.SmallIntegerField()
    actcode1 = models.BigIntegerField()
    actcode2 = models.BigIntegerField()
    actcode3 = models.BigIntegerField()
    actcode4 = models.BigIntegerField()
    act_census1 = models.CharField(max_length=15, blank=True, null=True)
    act_census2 = models.CharField(max_length=15, blank=True, null=True)
    act_census3 = models.CharField(max_length=15, blank=True, null=True)
    act_census4 = models.CharField(max_length=15, blank=True, null=True)
    est_code = models.CharField(max_length=6, blank=True, null=True)
    delivery_status = models.TextField(blank=True, null=True)  # This field type is a guess.
    lang_flag = models.CharField(max_length=1, blank=True, null=True)
    sparty_name = models.CharField(max_length=100, blank=True, null=True)
    sparty_age = models.SmallIntegerField()
    sparty_sex = models.CharField(max_length=1, blank=True, null=True)
    sparty_relation = models.CharField(max_length=100, blank=True, null=True)
    sparty_relation_flag = models.CharField(max_length=2, blank=True, null=True)
    sparty_type = models.CharField(max_length=5, blank=True, null=True)
    sparty_address = models.TextField(blank=True, null=True)
    sparty_state = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_state_code = models.IntegerField(blank=True, null=True)
    sparty_state_code = models.SmallIntegerField()
    sparty_district = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_district_code = models.IntegerField(blank=True, null=True)
    sparty_district_code = models.SmallIntegerField()
    sparty_taluka = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_taluka_code = models.IntegerField(blank=True, null=True)
    sparty_taluka_code = models.SmallIntegerField()
    sparty_village = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_village_code = models.IntegerField(blank=True, null=True)
    sparty_village_code = models.IntegerField()
    sparty_town = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_town_code = models.IntegerField(blank=True, null=True)
    sparty_town_code = models.IntegerField()
    sparty_ward = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_ward_code = models.IntegerField(blank=True, null=True)
    sparty_ward_code = models.IntegerField()
    sparty_police_station = models.CharField(max_length=100, blank=True, null=True)
    sparty_national_police_station_code = models.IntegerField(blank=True, null=True)
    sparty_police_station_code = models.IntegerField(blank=True, null=True)
    sparty_advocate = models.CharField(max_length=100, blank=True, null=True)
    sparty_email = models.CharField(max_length=99, blank=True, null=True)
    sparty_mobile = models.CharField(max_length=15, blank=True, null=True)
    efield1 = models.IntegerField(blank=True, null=True)
    efield2 = models.IntegerField(blank=True, null=True)
    efield3 = models.IntegerField(blank=True, null=True)
    efield4 = models.TextField(blank=True, null=True)
    efield5 = models.TextField(blank=True, null=True)
    efield6 = models.TextField(blank=True, null=True)
    efield7 = models.DateField(blank=True, null=True)
    efield8 = models.DateField(blank=True, null=True)
    efield9 = models.DateField(blank=True, null=True)
    sparty_village1 = models.CharField(max_length=100, blank=True, null=True)
    sparty_village2 = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_village1_code = models.IntegerField()
    sparty_census_village2_code = models.IntegerField()
    sparty_village1_code = models.IntegerField()
    sparty_village2_code = models.IntegerField()
    sparty_no = models.SmallIntegerField()
    upload_flag = models.CharField(max_length=1, blank=True, null=True)
    sparty_remark = models.TextField(blank=True, null=True)
    sparty_pincode = models.CharField(max_length=15, blank=True, null=True)
    sparty_address_type = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'criminal_process'


class CriminalProcessA(models.Model):
    pk = models.CompositePrimaryKey('rec_no', 'rec_year')
    cino = models.CharField(max_length=16)
    case_no = models.CharField(max_length=255, blank=True, null=True)
    filing_no = models.CharField(max_length=255, blank=True, null=True)
    date_first_list = models.DateField(blank=True, null=True)
    dt_regis = models.DateField(blank=True, null=True)
    date_of_filing = models.DateField(blank=True, null=True)
    date_of_decision = models.DateField(blank=True, null=True)
    next_date = models.DateField(blank=True, null=True)
    todays_date = models.DateField(blank=True, null=True)
    pet_name = models.CharField(max_length=100, blank=True, null=True)
    res_name = models.CharField(max_length=100, blank=True, null=True)
    pet_add = models.TextField(blank=True, null=True)
    res_add = models.TextField(blank=True, null=True)
    pet_age = models.SmallIntegerField()
    res_age = models.SmallIntegerField()
    prev_purpose = models.CharField(max_length=100, blank=True, null=True)
    next_purpose = models.CharField(max_length=100, blank=True, null=True)
    sub_purpose = models.CharField(max_length=100, blank=True, null=True)
    disposal_type = models.CharField(max_length=100, blank=True, null=True)
    nature = models.CharField(max_length=500, blank=True, null=True)
    lower_case_no = models.CharField(max_length=255, blank=True, null=True)
    lower_court_name = models.CharField(max_length=255, blank=True, null=True)
    lower_disp_date = models.DateField(blank=True, null=True)
    relief_offense = models.TextField(blank=True, null=True)
    cause_of_action = models.TextField(blank=True, null=True)
    offense_date = models.DateField(blank=True, null=True)
    under_act1 = models.CharField(max_length=100, blank=True, null=True)
    under_sec1 = models.CharField(max_length=100, blank=True, null=True)
    under_act2 = models.CharField(max_length=100, blank=True, null=True)
    under_sec2 = models.CharField(max_length=100, blank=True, null=True)
    under_act3 = models.CharField(max_length=100, blank=True, null=True)
    under_sec3 = models.CharField(max_length=100, blank=True, null=True)
    under_act4 = models.CharField(max_length=100, blank=True, null=True)
    under_sec4 = models.CharField(max_length=100, blank=True, null=True)
    court_name = models.CharField(max_length=100, blank=True, null=True)
    desg_name = models.CharField(max_length=500, blank=True, null=True)
    judge_name = models.CharField(max_length=500, blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    police_stn = models.CharField(max_length=100, blank=True, null=True)
    fir_no = models.CharField(max_length=100, blank=True, null=True)
    fir_year = models.SmallIntegerField(blank=True, null=True)
    main_case_no = models.CharField(max_length=255, blank=True, null=True)
    maincase_dtregis = models.DateField(blank=True, null=True)
    process_fees = models.IntegerField()
    fees_type = models.CharField(max_length=1, blank=True, null=True)
    receipt_no = models.CharField(max_length=50, blank=True, null=True)
    receipt_year = models.CharField(max_length=50, blank=True, null=True)
    receipt_dates = models.CharField(max_length=255, blank=True, null=True)
    fee = models.CharField(max_length=100, blank=True, null=True)
    recv_name = models.CharField(max_length=100, blank=True, null=True)
    recv_fathername = models.CharField(max_length=100, blank=True, null=True)
    recv_address = models.TextField(blank=True, null=True)
    recvaddress_type = models.TextField()  # This field type is a guess.
    ns_id = models.BigIntegerField()
    recv_state = models.CharField(max_length=100, blank=True, null=True)
    recv_district = models.CharField(max_length=100, blank=True, null=True)
    recv_taluka = models.CharField(max_length=100, blank=True, null=True)
    recv_village = models.CharField(max_length=100, blank=True, null=True)
    recv_town = models.CharField(max_length=100, blank=True, null=True)
    recv_ward = models.CharField(max_length=100, blank=True, null=True)
    recv_village1 = models.CharField(max_length=100, blank=True, null=True)
    recv_village2 = models.CharField(max_length=100, blank=True, null=True)
    recv_mobile = models.CharField(max_length=15, blank=True, null=True)
    recv_pincode = models.CharField(max_length=15, blank=True, null=True)
    receiver_age = models.SmallIntegerField()
    recv_adv = models.CharField(max_length=100, blank=True, null=True)
    party_no = models.SmallIntegerField()
    party_type = models.CharField(max_length=5, blank=True, null=True)
    server_date = models.DateField(blank=True, null=True)
    session_date = models.DateField(blank=True, null=True)
    draft_date = models.DateField(blank=True, null=True)
    ns_date = models.DateField(blank=True, null=True)
    label1 = models.CharField(max_length=150, blank=True, null=True)
    label2 = models.CharField(max_length=150, blank=True, null=True)
    label3 = models.CharField(max_length=150, blank=True, null=True)
    label4 = models.CharField(max_length=150, blank=True, null=True)
    label5 = models.CharField(max_length=150, blank=True, null=True)
    ns_title = models.CharField(max_length=255, blank=True, null=True)
    process_id = models.CharField(max_length=25, blank=True, null=True)
    rec_no = models.BigIntegerField()
    rec_year = models.BigIntegerField()
    recv_email = models.CharField(max_length=99, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    pet_father_name = models.CharField(max_length=99, blank=True, null=True)
    pet_father_flag = models.CharField(max_length=2, blank=True, null=True)
    res_father_name = models.CharField(max_length=99, blank=True, null=True)
    res_father_flag = models.CharField(max_length=2, blank=True, null=True)
    court_no = models.IntegerField(blank=True, null=True)
    recv_state_id = models.IntegerField()
    recv_district_id = models.IntegerField()
    recv_taluka_id = models.IntegerField()
    recv_village_id = models.IntegerField()
    recv_village1_id = models.IntegerField()
    recv_village2_id = models.IntegerField()
    recv_town_id = models.IntegerField()
    recv_ward_id = models.IntegerField()
    police_st_code = models.IntegerField(blank=True, null=True)
    court_process_id = models.SmallIntegerField()
    recv_police_stn = models.CharField(max_length=100, blank=True, null=True)
    recv_state_census = models.IntegerField()
    recv_district_census = models.IntegerField()
    recv_taluka_census = models.IntegerField()
    recv_village_census = models.IntegerField()
    recv_town_census = models.IntegerField()
    recv_ward_census = models.IntegerField()
    recv_village1_census = models.IntegerField()
    recv_village2_census = models.IntegerField()
    recv_police_st_census = models.CharField(max_length=10, blank=True, null=True)
    srno = models.BigIntegerField(blank=True, null=True)
    year = models.BigIntegerField(blank=True, null=True)
    regcase_type = models.SmallIntegerField(blank=True, null=True)
    reg_no = models.IntegerField(blank=True, null=True)
    reg_year = models.SmallIntegerField(blank=True, null=True)
    filcase_type = models.SmallIntegerField(blank=True, null=True)
    fil_no = models.IntegerField(blank=True, null=True)
    fil_year = models.SmallIntegerField(blank=True, null=True)
    recv_father_flag = models.CharField(max_length=2, blank=True, null=True)
    label6 = models.CharField(max_length=150, blank=True, null=True)
    label7 = models.CharField(max_length=150, blank=True, null=True)
    label8 = models.CharField(max_length=150, blank=True, null=True)
    label9 = models.CharField(max_length=150, blank=True, null=True)
    label10 = models.CharField(max_length=150, blank=True, null=True)
    date1 = models.DateField(blank=True, null=True)
    date2 = models.DateField(blank=True, null=True)
    date3 = models.DateField(blank=True, null=True)
    date4 = models.DateField(blank=True, null=True)
    date5 = models.DateField(blank=True, null=True)
    lower_state_id = models.IntegerField(blank=True, null=True)
    lower_taluka_code = models.IntegerField(blank=True, null=True)
    lower_court_code = models.SmallIntegerField(blank=True, null=True)
    lower_trial = models.SmallIntegerField(blank=True, null=True)
    lower_cino = models.CharField(max_length=16, blank=True, null=True)
    lower_judge_name = models.CharField(max_length=100, blank=True, null=True)
    lower_court = models.CharField(max_length=40, blank=True, null=True)
    juri_value = models.CharField(max_length=25, blank=True, null=True)
    main_matter_cino = models.CharField(max_length=16, blank=True, null=True)
    police_private = models.SmallIntegerField(blank=True, null=True)
    police_state_id = models.SmallIntegerField(blank=True, null=True)
    police_dist_code = models.SmallIntegerField(blank=True, null=True)
    police_stn_code = models.IntegerField(blank=True, null=True)
    foot_note = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    nature_cd = models.CharField(max_length=25, blank=True, null=True)
    lower_state_census = models.IntegerField()
    lower_taluka_census = models.IntegerField()
    police_state_census = models.IntegerField()
    police_dist_census = models.IntegerField()
    police_st_census = models.IntegerField()
    process_no = models.SmallIntegerField()
    subprocess_no = models.SmallIntegerField()
    actcode1 = models.BigIntegerField()
    actcode2 = models.BigIntegerField()
    actcode3 = models.BigIntegerField()
    actcode4 = models.BigIntegerField()
    act_census1 = models.CharField(max_length=15, blank=True, null=True)
    act_census2 = models.CharField(max_length=15, blank=True, null=True)
    act_census3 = models.CharField(max_length=15, blank=True, null=True)
    act_census4 = models.CharField(max_length=15, blank=True, null=True)
    est_code = models.CharField(max_length=6, blank=True, null=True)
    delivery_status = models.TextField(blank=True, null=True)  # This field type is a guess.
    lang_flag = models.CharField(max_length=1, blank=True, null=True)
    sparty_name = models.CharField(max_length=100, blank=True, null=True)
    sparty_age = models.SmallIntegerField()
    sparty_sex = models.CharField(max_length=1, blank=True, null=True)
    sparty_relation = models.CharField(max_length=100, blank=True, null=True)
    sparty_relation_flag = models.CharField(max_length=2, blank=True, null=True)
    sparty_type = models.CharField(max_length=5, blank=True, null=True)
    sparty_address = models.TextField(blank=True, null=True)
    sparty_state = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_state_code = models.IntegerField(blank=True, null=True)
    sparty_state_code = models.SmallIntegerField()
    sparty_district = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_district_code = models.IntegerField(blank=True, null=True)
    sparty_district_code = models.SmallIntegerField()
    sparty_taluka = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_taluka_code = models.IntegerField(blank=True, null=True)
    sparty_taluka_code = models.SmallIntegerField()
    sparty_village = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_village_code = models.IntegerField(blank=True, null=True)
    sparty_village_code = models.IntegerField()
    sparty_town = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_town_code = models.IntegerField(blank=True, null=True)
    sparty_town_code = models.IntegerField()
    sparty_ward = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_ward_code = models.IntegerField(blank=True, null=True)
    sparty_ward_code = models.IntegerField()
    sparty_police_station = models.CharField(max_length=100, blank=True, null=True)
    sparty_national_police_station_code = models.IntegerField(blank=True, null=True)
    sparty_police_station_code = models.IntegerField(blank=True, null=True)
    sparty_advocate = models.CharField(max_length=100, blank=True, null=True)
    sparty_email = models.CharField(max_length=99, blank=True, null=True)
    sparty_mobile = models.CharField(max_length=15, blank=True, null=True)
    efield1 = models.IntegerField(blank=True, null=True)
    efield2 = models.IntegerField(blank=True, null=True)
    efield3 = models.IntegerField(blank=True, null=True)
    efield4 = models.TextField(blank=True, null=True)
    efield5 = models.TextField(blank=True, null=True)
    efield6 = models.TextField(blank=True, null=True)
    efield7 = models.DateField(blank=True, null=True)
    efield8 = models.DateField(blank=True, null=True)
    efield9 = models.DateField(blank=True, null=True)
    sparty_village1 = models.CharField(max_length=100, blank=True, null=True)
    sparty_village2 = models.CharField(max_length=100, blank=True, null=True)
    sparty_census_village1_code = models.IntegerField()
    sparty_census_village2_code = models.IntegerField()
    sparty_village1_code = models.IntegerField()
    sparty_village2_code = models.IntegerField()
    sparty_no = models.SmallIntegerField()
    upload_flag = models.CharField(max_length=1, blank=True, null=True)
    sparty_remark = models.TextField(blank=True, null=True)
    sparty_pincode = models.CharField(max_length=15, blank=True, null=True)
    sparty_address_type = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'criminal_process_a'


class CriminalT(models.Model):
    cino = models.CharField(primary_key=True, max_length=16)
    police_st_code = models.IntegerField()
    fir_no = models.CharField(max_length=100, blank=True, null=True)
    fir_type_code = models.SmallIntegerField()
    fir_year = models.SmallIntegerField()
    session_magistrate = models.SmallIntegerField()
    police_private = models.SmallIntegerField()
    offense_date = models.DateField(blank=True, null=True)
    dt_chargesheet = models.DateField(blank=True, null=True)
    investofficer = models.CharField(max_length=100, blank=True, null=True)
    linvestofficer = models.CharField(max_length=100, blank=True, null=True)
    beltno = models.CharField(max_length=50, blank=True, null=True)
    investofficer1 = models.CharField(max_length=100, blank=True, null=True)
    linvestofficer1 = models.CharField(max_length=100, blank=True, null=True)
    beltno1 = models.CharField(max_length=50, blank=True, null=True)
    police_state_id = models.SmallIntegerField(blank=True, null=True)
    police_dist_code = models.SmallIntegerField(blank=True, null=True)
    causeofaction = models.TextField(blank=True, null=True)
    lcauseofaction = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    inv_agency_code = models.SmallIntegerField()
    fir_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'criminal_t'


class CriminalTA(models.Model):
    cino = models.CharField(primary_key=True, max_length=16)
    police_st_code = models.IntegerField()
    fir_no = models.CharField(max_length=100, blank=True, null=True)
    fir_type_code = models.SmallIntegerField()
    fir_year = models.SmallIntegerField()
    session_magistrate = models.SmallIntegerField()
    police_private = models.SmallIntegerField()
    offense_date = models.DateField(blank=True, null=True)
    dt_chargesheet = models.DateField(blank=True, null=True)
    investofficer = models.CharField(max_length=100, blank=True, null=True)
    linvestofficer = models.CharField(max_length=100, blank=True, null=True)
    beltno = models.CharField(max_length=50, blank=True, null=True)
    investofficer1 = models.CharField(max_length=100, blank=True, null=True)
    linvestofficer1 = models.CharField(max_length=100, blank=True, null=True)
    beltno1 = models.CharField(max_length=50, blank=True, null=True)
    police_state_id = models.SmallIntegerField(blank=True, null=True)
    police_dist_code = models.SmallIntegerField(blank=True, null=True)
    causeofaction = models.TextField(blank=True, null=True)
    lcauseofaction = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    inv_agency_code = models.SmallIntegerField()
    fir_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'criminal_t_a'


class DailyAppearance(models.Model):
    pk = models.CompositePrimaryKey('cino', 'sr_no')
    cino = models.CharField(max_length=16)
    date_of_issue = models.DateField(blank=True, null=True)
    party_no = models.IntegerField()
    type = models.SmallIntegerField(blank=True, null=True)
    process_issue = models.IntegerField(blank=True, null=True)
    sr_no = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'daily_appearance'


class DailyCrpc(models.Model):
    pk = models.CompositePrimaryKey('cino', 'sr_no')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    cino = models.CharField(max_length=16)
    todays_date = models.DateField(blank=True, null=True)
    party_no = models.IntegerField()
    examination = models.TextField()  # This field type is a guess.
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    sr_no = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'daily_crpc'


class DailyCrpcA(models.Model):
    pk = models.CompositePrimaryKey('cino', 'sr_no')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    cino = models.CharField(max_length=16)
    todays_date = models.DateField(blank=True, null=True)
    party_no = models.IntegerField()
    examination = models.TextField()  # This field type is a guess.
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    sr_no = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'daily_crpc_a'


class DailyProc(models.Model):
    pk = models.CompositePrimaryKey('cino', 'srno')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    next_date = models.DateField()
    time_slot = models.CharField(max_length=10, blank=True, null=True)
    estimate_time = models.CharField(max_length=10, blank=True, null=True)
    purpose_code = models.SmallIntegerField()
    subpurpose_id = models.BigIntegerField()
    order_code = models.SmallIntegerField()
    order_remark = models.TextField(blank=True, null=True)
    todays_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    court_no = models.IntegerField()
    present = models.TextField(blank=True, null=True)
    exhibit = models.TextField(blank=True, null=True)
    depositby = models.CharField(max_length=99, blank=True, null=True)
    deposit = models.DecimalField(max_digits=17, decimal_places=2)
    deposit_rem = models.CharField(max_length=255, blank=True, null=True)
    deposit_a = models.CharField(max_length=255, blank=True, null=True)
    paymentby = models.CharField(max_length=99, blank=True, null=True)
    payment = models.DecimalField(max_digits=17, decimal_places=2)
    payment_rem = models.CharField(max_length=255, blank=True, null=True)
    payment_a = models.CharField(max_length=255, blank=True, null=True)
    hearing_start_time = models.CharField(max_length=20, blank=True, null=True)
    hearing_end_time = models.CharField(max_length=20, blank=True, null=True)
    adjcode = models.SmallIntegerField()
    lorder_remark = models.TextField(blank=True, null=True)
    lexhibit = models.TextField(blank=True, null=True)
    no_exibits_marked = models.IntegerField()
    no_mos_marked = models.IntegerField()
    no_witnesses_ex = models.IntegerField()
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    desig_code = models.CharField(max_length=50, blank=True, null=True)
    incharge = models.CharField(max_length=1, blank=True, null=True)
    lpresent = models.TextField(blank=True, null=True)
    recall = models.CharField(max_length=1, blank=True, null=True)
    jocode = models.CharField(max_length=150, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    dormant_sinedie = models.CharField(max_length=1, blank=True, null=True)
    cino = models.CharField(max_length=16)
    cause_list_type = models.IntegerField(blank=True, null=True)
    sr_no = models.IntegerField(blank=True, null=True)
    causelist_type = models.IntegerField(blank=True, null=True)
    next_date_check = models.CharField(max_length=1, blank=True, null=True)
    status_id = models.IntegerField(blank=True, null=True)
    case_remark = models.TextField(blank=True, null=True)
    otherpresent = models.TextField(blank=True, null=True)
    takenonboard = models.CharField(max_length=2, blank=True, null=True)
    old_next_date = models.DateField(blank=True, null=True)
    old_purpose_code = models.SmallIntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    oldbenchid = models.IntegerField(blank=True, null=True)
    srno = models.IntegerField()
    vc_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    auto_date = models.DateField(blank=True, null=True)
    auto_date_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    issue_charge = models.CharField(max_length=1, blank=True, null=True)
    witness_examined = models.CharField(max_length=1, blank=True, null=True)
    no_of_pages = models.IntegerField(blank=True, null=True)
    crpc = models.CharField(max_length=1, blank=True, null=True)
    written_examined = models.CharField(max_length=99, blank=True, null=True)
    appearance_examined = models.CharField(max_length=99, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'daily_proc'


class DailyProcA(models.Model):
    pk = models.CompositePrimaryKey('cino', 'srno')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    next_date = models.DateField()
    time_slot = models.CharField(max_length=10, blank=True, null=True)
    estimate_time = models.CharField(max_length=10, blank=True, null=True)
    purpose_code = models.SmallIntegerField()
    subpurpose_id = models.BigIntegerField()
    order_code = models.SmallIntegerField()
    order_remark = models.TextField(blank=True, null=True)
    todays_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    court_no = models.IntegerField()
    present = models.TextField(blank=True, null=True)
    exhibit = models.TextField(blank=True, null=True)
    depositby = models.CharField(max_length=99, blank=True, null=True)
    deposit = models.DecimalField(max_digits=17, decimal_places=2)
    deposit_rem = models.CharField(max_length=255, blank=True, null=True)
    deposit_a = models.CharField(max_length=255, blank=True, null=True)
    paymentby = models.CharField(max_length=99, blank=True, null=True)
    payment = models.DecimalField(max_digits=17, decimal_places=2)
    payment_rem = models.CharField(max_length=255, blank=True, null=True)
    payment_a = models.CharField(max_length=255, blank=True, null=True)
    hearing_start_time = models.CharField(max_length=20, blank=True, null=True)
    hearing_end_time = models.CharField(max_length=20, blank=True, null=True)
    adjcode = models.SmallIntegerField()
    lorder_remark = models.TextField(blank=True, null=True)
    lexhibit = models.TextField(blank=True, null=True)
    no_exibits_marked = models.IntegerField()
    no_mos_marked = models.IntegerField()
    no_witnesses_ex = models.IntegerField()
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    desig_code = models.CharField(max_length=50, blank=True, null=True)
    incharge = models.CharField(max_length=1, blank=True, null=True)
    lpresent = models.TextField(blank=True, null=True)
    recall = models.CharField(max_length=1, blank=True, null=True)
    jocode = models.CharField(max_length=150, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    dormant_sinedie = models.CharField(max_length=1, blank=True, null=True)
    cino = models.CharField(max_length=16)
    cause_list_type = models.IntegerField(blank=True, null=True)
    sr_no = models.IntegerField(blank=True, null=True)
    causelist_type = models.IntegerField(blank=True, null=True)
    next_date_check = models.CharField(max_length=1, blank=True, null=True)
    status_id = models.IntegerField(blank=True, null=True)
    case_remark = models.TextField(blank=True, null=True)
    otherpresent = models.TextField(blank=True, null=True)
    takenonboard = models.CharField(max_length=2, blank=True, null=True)
    old_next_date = models.DateField(blank=True, null=True)
    old_purpose_code = models.SmallIntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    oldbenchid = models.IntegerField(blank=True, null=True)
    srno = models.IntegerField()
    vc_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    auto_date = models.DateField(blank=True, null=True)
    auto_date_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    issue_charge = models.CharField(max_length=1, blank=True, null=True)
    witness_examined = models.CharField(max_length=1, blank=True, null=True)
    no_of_pages = models.IntegerField(blank=True, null=True)
    crpc = models.CharField(max_length=1, blank=True, null=True)
    written_examined = models.CharField(max_length=99, blank=True, null=True)
    appearance_examined = models.CharField(max_length=99, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'daily_proc_a'


class DailyProcFiling(models.Model):
    pk = models.CompositePrimaryKey('cino', 'srno')
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    next_date = models.DateField()
    order_code = models.SmallIntegerField()
    order_remark = models.TextField(blank=True, null=True)
    todays_date = models.DateField(blank=True, null=True)
    court_no = models.IntegerField()
    purpose_code = models.SmallIntegerField()
    cino = models.CharField(max_length=16)
    sr_no = models.IntegerField(blank=True, null=True)
    causelist_type = models.IntegerField(blank=True, null=True)
    next_date_check = models.CharField(max_length=1, blank=True, null=True)
    status_id = models.IntegerField(blank=True, null=True)
    present = models.TextField(blank=True, null=True)
    jocode = models.CharField(max_length=150, blank=True, null=True)
    desig_code = models.CharField(max_length=50, blank=True, null=True)
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    case_remark = models.TextField(blank=True, null=True)
    otherpresent = models.TextField(blank=True, null=True)
    takenonboard = models.CharField(max_length=2, blank=True, null=True)
    old_next_date = models.DateField(blank=True, null=True)
    old_purpose_code = models.SmallIntegerField(blank=True, null=True)
    oldbenchid = models.IntegerField(blank=True, null=True)
    srno = models.IntegerField()
    subpurpose_id = models.SmallIntegerField()
    lorder_remark = models.TextField(blank=True, null=True)
    auto_date = models.DateField(blank=True, null=True)
    auto_date_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'daily_proc_filing'


class DailyWitness(models.Model):
    pk = models.CompositePrimaryKey('cino', 'sr_no')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    cino = models.CharField(max_length=16)
    todays_date = models.DateField(blank=True, null=True)
    witness_no = models.IntegerField()
    witness_name = models.CharField(max_length=99, blank=True, null=True)
    witness_for = models.TextField()  # This field type is a guess.
    examination = models.TextField()  # This field type is a guess.
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    sr_no = models.IntegerField()
    present = models.CharField(max_length=1, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'daily_witness'


class DailyWitnessA(models.Model):
    pk = models.CompositePrimaryKey('cino', 'sr_no')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    cino = models.CharField(max_length=16)
    todays_date = models.DateField(blank=True, null=True)
    witness_no = models.IntegerField()
    witness_name = models.CharField(max_length=99, blank=True, null=True)
    witness_for = models.TextField()  # This field type is a guess.
    examination = models.TextField()  # This field type is a guess.
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    sr_no = models.IntegerField()
    present = models.CharField(max_length=1, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'daily_witness_a'


class Dashboard(models.Model):
    groupid = models.IntegerField(blank=True, null=True)
    itemid = models.IntegerField(blank=True, null=True)
    userroleid = models.CharField(max_length=100, blank=True, null=True)
    dboarddate = models.DateField(blank=True, null=True)
    courtno = models.IntegerField(blank=True, null=True)
    element1 = models.IntegerField(blank=True, null=True)
    element2 = models.IntegerField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    section_id = models.IntegerField(blank=True, null=True)
    jocode = models.CharField(max_length=150, blank=True, null=True)
    cause_list_type_id = models.SmallIntegerField(blank=True, null=True)
    writ_count = models.BigIntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dashboard'


class DashboardBench(models.Model):
    groupid = models.IntegerField(blank=True, null=True)
    itemid = models.IntegerField(blank=True, null=True)
    userroleid = models.CharField(max_length=100, blank=True, null=True)
    dboarddate = models.DateField(blank=True, null=True)
    courtno = models.IntegerField(blank=True, null=True)
    element1 = models.IntegerField(blank=True, null=True)
    element2 = models.IntegerField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    section_id = models.IntegerField(blank=True, null=True)
    jocode = models.CharField(max_length=150, blank=True, null=True)
    cause_list_type_id = models.SmallIntegerField(blank=True, null=True)
    writ_count = models.BigIntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dashboard_bench'


class DdoMast(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    trea_cd = models.CharField(max_length=4, blank=True, null=True)
    ddo_cd = models.CharField(max_length=6, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_add = models.TextField(blank=True, null=True)
    code_no = models.CharField(max_length=10, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    lbank_name = models.CharField(max_length=100, blank=True, null=True)
    lbank_add = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ddo_mast'


class DelayMaster(models.Model):
    delay_id = models.SmallIntegerField(primary_key=True)
    delay_name = models.CharField(max_length=100, blank=True, null=True)
    ldelay_name = models.CharField(max_length=100, blank=True, null=True)
    ci_cri = models.SmallIntegerField()
    hc_sc = models.SmallIntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'delay_master'


class DelayTrans(models.Model):
    pk = models.CompositePrimaryKey('cino', 'sr_no')
    cino = models.CharField(max_length=16)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    regcase_type = models.SmallIntegerField()
    reg_no = models.IntegerField()
    reg_year = models.SmallIntegerField()
    delay_id = models.SmallIntegerField()
    hc_sc = models.SmallIntegerField()
    app_casetype = models.SmallIntegerField()
    app_caseno = models.IntegerField()
    app_caseyear = models.SmallIntegerField()
    from_date = models.DateField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    app_casetype_name = models.CharField(max_length=250, blank=True, null=True)
    dc_oc = models.CharField(max_length=1, blank=True, null=True)
    court_name = models.CharField(max_length=100, blank=True, null=True)
    oth_crt_case_no = models.CharField(max_length=100, blank=True, null=True)
    courtno = models.IntegerField(blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    document_type = models.IntegerField(blank=True, null=True)
    witness_count = models.IntegerField(blank=True, null=True)
    record_reason = models.IntegerField(blank=True, null=True)
    delay_colsed = models.TextField(blank=True, null=True)  # This field type is a guess.
    delay_date = models.DateField(blank=True, null=True)
    delayclosed_date = models.DateField(blank=True, null=True)
    sr_no = models.IntegerField()
    counsel = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'delay_trans'


class DelayTransA(models.Model):
    pk = models.CompositePrimaryKey('cino', 'sr_no')
    cino = models.CharField(max_length=16)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    regcase_type = models.SmallIntegerField()
    reg_no = models.IntegerField()
    reg_year = models.SmallIntegerField()
    delay_id = models.SmallIntegerField()
    hc_sc = models.SmallIntegerField()
    app_casetype = models.SmallIntegerField()
    app_caseno = models.IntegerField()
    app_caseyear = models.SmallIntegerField()
    from_date = models.DateField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    app_casetype_name = models.CharField(max_length=250, blank=True, null=True)
    dc_oc = models.CharField(max_length=1, blank=True, null=True)
    court_name = models.CharField(max_length=100, blank=True, null=True)
    oth_crt_case_no = models.CharField(max_length=100, blank=True, null=True)
    courtno = models.IntegerField(blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    document_type = models.IntegerField(blank=True, null=True)
    witness_count = models.IntegerField(blank=True, null=True)
    record_reason = models.IntegerField(blank=True, null=True)
    delay_colsed = models.TextField(blank=True, null=True)  # This field type is a guess.
    delay_date = models.DateField(blank=True, null=True)
    delayclosed_date = models.DateField(blank=True, null=True)
    sr_no = models.IntegerField()
    counsel = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'delay_trans_a'


class DeletedCases(models.Model):
    case_no = models.CharField(max_length=15, blank=True, null=True)
    pet_name = models.CharField(max_length=100, blank=True, null=True)
    res_name = models.CharField(max_length=100, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    cino = models.CharField(primary_key=True, max_length=16)
    ipaddress = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    date_time = models.DateTimeField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'deleted_cases'


class DepositRegister(models.Model):
    pk = models.CompositePrimaryKey('register_type', 'posting_date', 'deposit_reg_no')
    deposit_sl_no = models.IntegerField()
    form_a_sl_no = models.IntegerField()
    form_a_order_no = models.IntegerField()
    form_a_order_type = models.SmallIntegerField()
    form_a_order_date = models.DateField(blank=True, null=True)
    form_a_case_no = models.CharField(max_length=15, blank=True, null=True)
    form_a_pet_res_name = models.CharField(max_length=255, blank=True, null=True)
    form_a_pet_res_id = models.SmallIntegerField()
    form_a_pet_res_type = models.CharField(max_length=1, blank=True, null=True)
    form_a_address = models.TextField(blank=True, null=True)
    form_a_repr_name = models.CharField(max_length=255, blank=True, null=True)
    form_a_subject = models.CharField(max_length=255, blank=True, null=True)
    form_a_amount = models.DecimalField(max_digits=17, decimal_places=2)
    form_a_paymode = models.CharField(max_length=1, blank=True, null=True)
    form_a_receipt_date = models.DateField(blank=True, null=True)
    form_a_book_no = models.SmallIntegerField()
    form_a_serial_no = models.SmallIntegerField()
    form_a_receipt_type = models.SmallIntegerField()
    form_a_receipt_no = models.IntegerField()
    deposit_received_by = models.CharField(max_length=255, blank=True, null=True)
    form_a_ch_real_date = models.DateField(blank=True, null=True)
    form_a_ro_no = models.IntegerField()
    form_a_account_purpose = models.SmallIntegerField()
    register_type = models.SmallIntegerField()
    posting_date = models.DateField()
    deposit_reg_no = models.IntegerField()
    payment_reg_no = models.CharField(max_length=255, blank=True, null=True)
    attachment = models.CharField(max_length=255, blank=True, null=True)
    attachment_flag = models.TextField()  # This field type is a guess.
    attachment_date = models.DateField(blank=True, null=True)
    cancel_entry = models.TextField()  # This field type is a guess.
    date_time = models.DateTimeField()
    lpet_res_name = models.CharField(max_length=100, blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    lrepr_name = models.CharField(max_length=100, blank=True, null=True)
    lsubject = models.CharField(max_length=255, blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'deposit_register'


class DepositRegisterMaster(models.Model):
    depreg_id = models.SmallIntegerField(primary_key=True)
    depreg_name = models.CharField(max_length=100, blank=True, null=True)
    payreg_name = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    type = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'deposit_register_master'


class DesgT(models.Model):
    desgcode = models.BigIntegerField(primary_key=True)
    desgname = models.CharField(max_length=150, blank=True, null=True)
    ldesgname = models.CharField(max_length=150, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    national_code = models.BigIntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'desg_t'


class DispTypeT(models.Model):
    disp_type = models.SmallIntegerField(primary_key=True)
    disp_name = models.CharField(max_length=100, blank=True, null=True)
    ldisp_name = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    national_code = models.BigIntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'disp_type_t'


class DisposalProc(models.Model):
    case_no = models.CharField(max_length=15, blank=True, null=True)
    order_remark = models.TextField(blank=True, null=True)
    todays_date = models.DateField(blank=True, null=True)
    court_no = models.IntegerField()
    exhibit = models.TextField(blank=True, null=True)
    lorder_remark = models.TextField(blank=True, null=True)
    lexhibit = models.TextField(blank=True, null=True)
    present = models.TextField(blank=True, null=True)
    desig_code = models.CharField(max_length=50, blank=True, null=True)
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    incharge = models.CharField(max_length=1, blank=True, null=True)
    lpresent = models.TextField(blank=True, null=True)
    jocode = models.CharField(max_length=150, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    cino = models.CharField(primary_key=True, max_length=16)
    otherpresent = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    status_id = models.IntegerField(blank=True, null=True)
    bench_type = models.IntegerField(blank=True, null=True)
    crtstat = models.CharField(max_length=1, blank=True, null=True)
    convicted_allowed = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'disposal_proc'


class DisposalProcFiling(models.Model):
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    order_remark = models.TextField(blank=True, null=True)
    todays_date = models.DateField(blank=True, null=True)
    court_no = models.IntegerField()
    date_of_decision = models.DateField(blank=True, null=True)
    disp_nature = models.SmallIntegerField()
    cino = models.CharField(primary_key=True, max_length=16)
    present = models.TextField(blank=True, null=True)
    jocode = models.CharField(max_length=150, blank=True, null=True)
    desig_code = models.CharField(max_length=50, blank=True, null=True)
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    otherpresent = models.TextField(blank=True, null=True)
    lorder_remark = models.TextField(blank=True, null=True)
    status_id = models.IntegerField(blank=True, null=True)
    bench_type = models.IntegerField(blank=True, null=True)
    crtstat = models.CharField(max_length=1, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'disposal_proc_filing'


class DisposedProceeding(models.Model):
    pk = models.CompositePrimaryKey('todays_date', 'cino')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    business = models.TextField(blank=True, null=True)
    todays_date = models.DateField()
    court_no = models.IntegerField()
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    desig_code = models.CharField(max_length=50, blank=True, null=True)
    jocode = models.CharField(max_length=150, blank=True, null=True)
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'disposed_proceeding'


class DistrictT(models.Model):
    pk = models.CompositePrimaryKey('state_id', 'dist_code')
    dist_code = models.SmallIntegerField()
    dist_name = models.CharField(max_length=50, blank=True, null=True)
    ldist_name = models.CharField(max_length=50, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    national_code = models.BigIntegerField(blank=True, null=True)
    state_id = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'district_t'


class DocFiling(models.Model):
    case_doc = models.CharField(max_length=1, blank=True, null=True)
    court_no = models.IntegerField()
    case_fr = models.SmallIntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    doc_no = models.CharField(max_length=12, blank=True, null=True)
    doc_year = models.SmallIntegerField()
    doc_type = models.CharField(max_length=150, blank=True, null=True)
    doc_desc = models.CharField(max_length=150, blank=True, null=True)
    date_of_doc_submit = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    ia_no = models.CharField(max_length=12, blank=True, null=True)
    ia_registrationo = models.CharField(max_length=12, blank=True, null=True)
    party_applying = models.CharField(max_length=2, blank=True, null=True)
    party_applying_code = models.CharField(max_length=50, blank=True, null=True)
    appotherparty = models.CharField(max_length=150, blank=True, null=True)
    appotheradv = models.CharField(max_length=99, blank=True, null=True)
    purpose_code = models.BigIntegerField()
    relief_offense = models.TextField(blank=True, null=True)
    date_of_ia_filing = models.DateField(blank=True, null=True)
    date_of_ia_registration = models.DateField(blank=True, null=True)
    date_of_serving_notice = models.DateField(blank=True, null=True)
    date_of_hearing = models.DateField(blank=True, null=True)
    date_of_order = models.DateField(blank=True, null=True)
    disposal_date = models.DateField(blank=True, null=True)
    disp_nature = models.IntegerField()
    order_code = models.SmallIntegerField()
    court_fee = models.IntegerField()
    act_code = models.IntegerField()
    under_sec = models.CharField(max_length=100, blank=True, null=True)
    unit = models.DecimalField(max_digits=17, decimal_places=2)
    goshwara_no = models.SmallIntegerField()
    order_remark = models.TextField(blank=True, null=True)
    exhibit = models.TextField(blank=True, null=True)
    dt_of_entry = models.DateTimeField()
    objcompl_date = models.DateField(blank=True, null=True)
    obj_flag = models.CharField(max_length=1, blank=True, null=True)
    objreceipt_dt = models.DateField(blank=True, null=True)
    objreturn_dt = models.DateField(blank=True, null=True)
    objprepare_dt = models.DateField(blank=True, null=True)
    objection = models.CharField(max_length=250, blank=True, null=True)
    objdescription = models.TextField(blank=True, null=True)
    lobjection = models.CharField(max_length=250, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    date_filing_disp = models.DateField(blank=True, null=True)
    reason_for_rej = models.TextField(blank=True, null=True)
    lreason_for_rej = models.TextField(blank=True, null=True)
    date_of_decision_o = models.DateField(blank=True, null=True)
    date_of_revoke = models.DateField(blank=True, null=True)
    doc_recd_dt = models.DateField(blank=True, null=True)
    doc_return_dt = models.DateField(blank=True, null=True)
    doc_representation_dt = models.DateField(blank=True, null=True)
    doc_put_tofile_dt = models.DateField(blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'doc_filing'


class DockInward(models.Model):
    cino = models.CharField(primary_key=True, max_length=16)
    filing_no = models.CharField(max_length=16, blank=True, null=True)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    receiver_user_id = models.IntegerField(blank=True, null=True)
    receiver_user_name = models.CharField(max_length=100, blank=True, null=True)
    receive_date = models.DateTimeField(blank=True, null=True)
    accept = models.TextField(blank=True, null=True)  # This field type is a guess.
    accept_date = models.DateField(blank=True, null=True)
    not_accept_reason = models.TextField(blank=True, null=True)
    current_task_sr_no = models.IntegerField(blank=True, null=True)
    current_task_code = models.IntegerField(blank=True, null=True)
    current_task_comp_date = models.DateField(blank=True, null=True)
    current_task_disp_date = models.DateField(blank=True, null=True)
    current_task_remarks = models.TextField(blank=True, null=True)
    sender_date = models.DateField(blank=True, null=True)
    sender_user_id = models.IntegerField(blank=True, null=True)
    sender_user_name = models.CharField(max_length=100, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dock_inward'


class DockInwardHis(models.Model):
    pk = models.CompositePrimaryKey('cino', 'srno')
    cino = models.CharField(max_length=16)
    filing_no = models.CharField(max_length=16, blank=True, null=True)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    receiver_user_id = models.IntegerField(blank=True, null=True)
    receiver_user_name = models.CharField(max_length=100, blank=True, null=True)
    receive_date = models.DateTimeField(blank=True, null=True)
    accept = models.TextField(blank=True, null=True)  # This field type is a guess.
    accept_date = models.DateField(blank=True, null=True)
    not_accept_reason = models.TextField(blank=True, null=True)
    current_task_sr_no = models.IntegerField(blank=True, null=True)
    current_task_code = models.IntegerField(blank=True, null=True)
    current_task_comp_date = models.DateField(blank=True, null=True)
    current_task_disp_date = models.DateField(blank=True, null=True)
    current_task_remarks = models.TextField(blank=True, null=True)
    sender_date = models.DateField(blank=True, null=True)
    sender_user_id = models.IntegerField(blank=True, null=True)
    sender_user_name = models.CharField(max_length=100, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    srno = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dock_inward_his'


class DocuTypeT(models.Model):
    docu_type = models.SmallIntegerField(primary_key=True)
    docu_name = models.CharField(max_length=100, blank=True, null=True)
    ldocu_name = models.CharField(max_length=100, blank=True, null=True)
    order_by_court = models.TextField()  # This field type is a guess.
    display = models.TextField()  # This field type is a guess.
    national_code = models.BigIntegerField()
    judgedecree = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'docu_type_t'


class EcivAddressT(models.Model):
    pk = models.CompositePrimaryKey('party_no', 'efilno')
    party_no = models.SmallIntegerField()
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    orgid = models.SmallIntegerField()
    name = models.CharField(max_length=100, blank=True, null=True)
    lname = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    altaddress = models.TextField(blank=True, null=True)
    altladdress = models.TextField(blank=True, null=True)
    pet_age = models.SmallIntegerField()
    father_name = models.CharField(max_length=100, blank=True, null=True)
    lfather_name = models.CharField(max_length=100, blank=True, null=True)
    father_flag = models.CharField(max_length=2)
    pet_caste = models.CharField(max_length=20, blank=True, null=True)
    type = models.SmallIntegerField()
    adv_name = models.CharField(max_length=100, blank=True, null=True)
    ladv_name = models.CharField(max_length=100, blank=True, null=True)
    adv_cd = models.BigIntegerField()
    pet_occu = models.CharField(max_length=30, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    legal_heir = models.TextField()  # This field type is a guess.
    pet_nationality = models.CharField(max_length=99, blank=True, null=True)
    pet_email = models.CharField(max_length=254, blank=True, null=True)
    pet_mobile = models.CharField(max_length=15, blank=True, null=True)
    pet_phone = models.CharField(max_length=15, blank=True, null=True)
    pet_fax = models.CharField(max_length=15, blank=True, null=True)
    parentid = models.SmallIntegerField(blank=True, null=True)
    pet_sex = models.CharField(max_length=1, blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    altdist_code = models.SmallIntegerField()
    alttaluka_code = models.SmallIntegerField()
    altvillage_code = models.IntegerField()
    altvillage1_code = models.IntegerField(blank=True, null=True)
    altvillage2_code = models.IntegerField(blank=True, null=True)
    alttown_code = models.IntegerField()
    altward_code = models.IntegerField()
    passportno = models.CharField(max_length=25, blank=True, null=True)
    pincode = models.IntegerField(blank=True, null=True)
    country = models.CharField(max_length=99, blank=True, null=True)
    uid_no = models.BigIntegerField(blank=True, null=True)
    performaresflag = models.CharField(max_length=1)
    panno = models.CharField(max_length=10, blank=True, null=True)
    hide_partyname = models.CharField(max_length=1)
    police_st_code = models.IntegerField()
    party_id = models.TextField(blank=True, null=True)
    ph = models.TextField()  # This field type is a guess.
    split_case_refno = models.CharField(max_length=15, blank=True, null=True)
    split_case_flag = models.TextField()  # This field type is a guess.
    old_party_no = models.CharField(max_length=11, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    extra_inperson = models.CharField(max_length=1, blank=True, null=True)
    party_status = models.IntegerField()
    lpet_occu = models.CharField(max_length=50, blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    efilno = models.CharField(max_length=99)
    econfirm = models.CharField(max_length=1, blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    altstate_id = models.IntegerField(blank=True, null=True)
    pet_gender = models.CharField(max_length=1, blank=True, null=True)
    name_salutation = models.SmallIntegerField(blank=True, null=True)
    ref_m_efiled_type_id = models.IntegerField(blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    create_by_ip = models.CharField(max_length=30, blank=True, null=True)
    efiling_year = models.CharField(max_length=10, blank=True, null=True)
    create_on = models.DateTimeField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    proposed_fine = models.DecimalField(max_digits=17, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'eciv_address_t'


class EcivilT(models.Model):
    case_no = models.CharField(max_length=15, blank=True, null=True)
    pet_name = models.CharField(max_length=100, blank=True, null=True)
    lpet_name = models.CharField(max_length=100, blank=True, null=True)
    pet_sex = models.CharField(max_length=1, blank=True, null=True)
    res_name = models.CharField(max_length=100, blank=True, null=True)
    lres_name = models.CharField(max_length=100, blank=True, null=True)
    res_sex = models.CharField(max_length=1, blank=True, null=True)
    court_no = models.IntegerField()
    file_before = models.IntegerField()
    date_of_filing = models.DateField(blank=True, null=True)
    time_of_filing = models.TimeField(blank=True, null=True)
    date_of_present = models.DateField(blank=True, null=True)
    date_first_list = models.DateField(blank=True, null=True)
    date_next_list = models.DateField(blank=True, null=True)
    date_last_list = models.DateField(blank=True, null=True)
    date_of_decision = models.DateField(blank=True, null=True)
    dec_jud_name = models.CharField(max_length=100, blank=True, null=True)
    pet_adv = models.CharField(max_length=100, blank=True, null=True)
    pet_adv_cd = models.BigIntegerField()
    lpet_adv = models.CharField(max_length=100, blank=True, null=True)
    res_adv = models.CharField(max_length=100, blank=True, null=True)
    res_adv_cd = models.BigIntegerField()
    lres_adv = models.CharField(max_length=100, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2)
    juri_value = models.CharField(max_length=25)
    purpose_prev = models.SmallIntegerField()
    purpose_next = models.SmallIntegerField()
    purpose_filing = models.CharField(max_length=255, blank=True, null=True)
    under_sec1 = models.CharField(max_length=100, blank=True, null=True)
    under_act1 = models.IntegerField()
    under_sec2 = models.CharField(max_length=100, blank=True, null=True)
    under_act2 = models.IntegerField()
    under_sec3 = models.CharField(max_length=100, blank=True, null=True)
    under_act3 = models.IntegerField()
    under_sec4 = models.CharField(max_length=100, blank=True, null=True)
    under_act4 = models.IntegerField()
    subject = models.CharField(max_length=255, blank=True, null=True)
    subject1 = models.CharField(max_length=255, blank=True, null=True)
    subject2 = models.CharField(max_length=255, blank=True, null=True)
    subject3 = models.CharField(max_length=255, blank=True, null=True)
    caveat = models.CharField(max_length=255, blank=True, null=True)
    order_passed = models.IntegerField()
    order_passed1 = models.CharField(max_length=255, blank=True, null=True)
    unit = models.DecimalField(max_digits=17, decimal_places=2)
    goshwara_no = models.SmallIntegerField()
    lower_court_code = models.SmallIntegerField()
    filing_case = models.SmallIntegerField()
    lower_court = models.CharField(max_length=40, blank=True, null=True)
    lower_court_dec_dt = models.DateField(blank=True, null=True)
    deleted = models.CharField(max_length=1, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    dt_of_mod = models.DateTimeField(blank=True, null=True)
    petadd = models.TextField(blank=True, null=True)
    lpetadd = models.TextField(blank=True, null=True)
    resadd = models.TextField(blank=True, null=True)
    lresadd = models.TextField(blank=True, null=True)
    disp_nature = models.SmallIntegerField()
    tr_from_court = models.SmallIntegerField()
    tr_date = models.DateField(blank=True, null=True)
    pet_father_name = models.CharField(max_length=100, blank=True, null=True)
    lpet_father_name = models.CharField(max_length=100, blank=True, null=True)
    pet_father_flag = models.CharField(max_length=2, blank=True, null=True)
    pet_nationality = models.CharField(max_length=99, blank=True, null=True)
    pet_caste = models.CharField(max_length=2, blank=True, null=True)
    pet_age = models.SmallIntegerField()
    pet_email = models.CharField(max_length=254, blank=True, null=True)
    pet_mobile = models.CharField(max_length=15, blank=True, null=True)
    pet_phone = models.CharField(max_length=15, blank=True, null=True)
    pet_fax = models.CharField(max_length=15, blank=True, null=True)
    pet_occu = models.CharField(max_length=50, blank=True, null=True)
    res_father_name = models.CharField(max_length=100, blank=True, null=True)
    lres_father_name = models.CharField(max_length=100, blank=True, null=True)
    res_father_flag = models.CharField(max_length=2, blank=True, null=True)
    res_nationality = models.CharField(max_length=99, blank=True, null=True)
    res_caste = models.CharField(max_length=2, blank=True, null=True)
    res_age = models.SmallIntegerField()
    res_email = models.CharField(max_length=254, blank=True, null=True)
    res_mobile = models.CharField(max_length=15, blank=True, null=True)
    res_phone = models.CharField(max_length=15, blank=True, null=True)
    res_fax = models.CharField(max_length=15, blank=True, null=True)
    res_occu = models.CharField(max_length=50, blank=True, null=True)
    dt_regis = models.DateField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    date_filing_disp = models.DateField(blank=True, null=True)
    pet_legal_heir = models.TextField()  # This field type is a guess.
    res_legal_heir = models.TextField()  # This field type is a guess.
    update_date = models.DateTimeField(blank=True, null=True)
    pet_occupation = models.CharField(max_length=50, blank=True, null=True)
    res_occupation = models.CharField(max_length=50, blank=True, null=True)
    police_st_code = models.IntegerField()
    fir_no = models.CharField(max_length=15, blank=True, null=True)
    fir_type_code = models.SmallIntegerField()
    fir_year = models.SmallIntegerField()
    session_magistrate = models.SmallIntegerField()
    police_private = models.SmallIntegerField()
    ci_cri = models.SmallIntegerField()
    offense_date = models.DateField(blank=True, null=True)
    dt_chargesheet = models.DateField(blank=True, null=True)
    link_code = models.CharField(max_length=15, blank=True, null=True)
    reason_for_rej = models.TextField(blank=True, null=True)
    lreason_for_rej = models.TextField(blank=True, null=True)
    not_before_me = models.CharField(max_length=50, blank=True, null=True)
    before_me = models.CharField(max_length=50, blank=True, null=True)
    obj_redate = models.DateField(blank=True, null=True)
    obj_flag = models.TextField()  # This field type is a guess.
    objreceipt_dt = models.DateField(blank=True, null=True)
    objreturn_dt = models.DateField(blank=True, null=True)
    objprepare_dt = models.DateField(blank=True, null=True)
    objection = models.TextField(blank=True, null=True)
    objdescription = models.TextField(blank=True, null=True)
    lobjection = models.CharField(max_length=250, blank=True, null=True)
    date_filing_disp_o = models.DateField(blank=True, null=True)
    date_filing_restore = models.DateField(blank=True, null=True)
    date_of_decision_o = models.DateField(blank=True, null=True)
    date_of_revoke = models.DateField(blank=True, null=True)
    urgent = models.TextField()  # This field type is a guess.
    main_case_no = models.CharField(max_length=15, blank=True, null=True)
    pet_add2 = models.CharField(max_length=255, blank=True, null=True)
    lpet_add2 = models.CharField(max_length=255, blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    res_dist = models.SmallIntegerField()
    res_taluka = models.SmallIntegerField()
    res_village = models.IntegerField()
    res_village1 = models.IntegerField()
    res_village2 = models.IntegerField()
    res_town_code = models.IntegerField()
    res_ward_code = models.IntegerField()
    res_add2 = models.CharField(max_length=255, blank=True, null=True)
    lres_add2 = models.CharField(max_length=255, blank=True, null=True)
    dist_code3 = models.SmallIntegerField()
    taluka_code3 = models.SmallIntegerField()
    village_code3 = models.IntegerField()
    village1_code3 = models.IntegerField()
    village2_code3 = models.IntegerField()
    town_code3 = models.IntegerField()
    ward_code3 = models.IntegerField()
    dist_code4 = models.SmallIntegerField()
    taluka_code4 = models.SmallIntegerField()
    village_code4 = models.IntegerField()
    village1_code4 = models.IntegerField()
    village2_code4 = models.IntegerField()
    town_code4 = models.IntegerField()
    ward_code4 = models.IntegerField()
    chk = models.CharField(max_length=50, blank=True, null=True)
    pet_passportno = models.CharField(max_length=25, blank=True, null=True)
    pet_country = models.CharField(max_length=99, blank=True, null=True)
    pet_pincode = models.IntegerField(blank=True, null=True)
    res_passportno = models.CharField(max_length=25, blank=True, null=True)
    res_country = models.CharField(max_length=99, blank=True, null=True)
    res_pincode = models.IntegerField(blank=True, null=True)
    reg_pl = models.CharField(max_length=1, blank=True, null=True)
    orgid = models.SmallIntegerField(blank=True, null=True)
    resorgid = models.SmallIntegerField(blank=True, null=True)
    pet_dob = models.DateField(blank=True, null=True)
    res_dob = models.DateField(blank=True, null=True)
    plead_guilty = models.TextField()  # This field type is a guess.
    nature_cd = models.CharField(max_length=25, blank=True, null=True)
    relief_offense = models.TextField(blank=True, null=True)
    lrelief_offence = models.TextField(blank=True, null=True)
    causeofaction = models.TextField(blank=True, null=True)
    lcauseofaction = models.TextField(blank=True, null=True)
    legacy_flag = models.TextField()  # This field type is a guess.
    pet_extracount = models.IntegerField()
    res_extracount = models.IntegerField()
    order_sect_kar = models.TextField(blank=True, null=True)
    nature_kar = models.TextField(blank=True, null=True)
    allocation_dt = models.DateField(blank=True, null=True)
    rej_sr_no = models.IntegerField()
    unit_type = models.CharField(max_length=150, blank=True, null=True)
    unit_type_value = models.CharField(max_length=150, blank=True, null=True)
    transfer_est = models.TextField()  # This field type is a guess.
    imprisonment = models.SmallIntegerField()
    bal_fee_date = models.DateField(blank=True, null=True)
    pet_uid = models.BigIntegerField(blank=True, null=True)
    res_uid = models.BigIntegerField(blank=True, null=True)
    reasonregisdate = models.TextField(blank=True, null=True)
    oldcase_no = models.CharField(max_length=16, blank=True, null=True)
    performaresflag = models.TextField()  # This field type is a guess.
    petpanno = models.CharField(max_length=10, blank=True, null=True)
    respanno = models.CharField(max_length=10, blank=True, null=True)
    reasonfilingdate = models.CharField(max_length=255, blank=True, null=True)
    oldfiling_no = models.CharField(max_length=16, blank=True, null=True)
    hide_pet_name = models.CharField(max_length=1)
    hide_res_name = models.CharField(max_length=1)
    hide_partyname = models.CharField(max_length=1)
    petpolice_st_code = models.IntegerField()
    respolice_st_code = models.IntegerField()
    investofficer = models.CharField(max_length=100, blank=True, null=True)
    linvestofficer = models.CharField(max_length=100, blank=True, null=True)
    beltno = models.CharField(max_length=50, blank=True, null=True)
    investofficer1 = models.CharField(max_length=100, blank=True, null=True)
    linvestofficer1 = models.CharField(max_length=100, blank=True, null=True)
    beltno1 = models.CharField(max_length=50, blank=True, null=True)
    pet_org_contact_person = models.CharField(max_length=100, blank=True, null=True)
    petorg_person = models.CharField(max_length=100, blank=True, null=True)
    res_org_contact_person = models.CharField(max_length=100, blank=True, null=True)
    resorg_person = models.CharField(max_length=100, blank=True, null=True)
    filcase_type = models.SmallIntegerField(blank=True, null=True)
    fil_no = models.IntegerField(blank=True, null=True)
    fil_year = models.SmallIntegerField(blank=True, null=True)
    regcase_type = models.SmallIntegerField(blank=True, null=True)
    reg_no = models.IntegerField(blank=True, null=True)
    reg_year = models.SmallIntegerField(blank=True, null=True)
    goshwara_no_o = models.SmallIntegerField()
    disp_nature_o = models.SmallIntegerField()
    archive = models.TextField()  # This field type is a guess.
    tab_status = models.CharField(max_length=15, blank=True, null=True)
    lsubject1 = models.CharField(max_length=255, blank=True, null=True)
    pending_ia = models.TextField()  # This field type is a guess.
    ia_next_date = models.DateField(blank=True, null=True)
    time_slot = models.IntegerField(blank=True, null=True)
    pet_ph = models.TextField()  # This field type is a guess.
    res_ph = models.TextField()  # This field type is a guess.
    purpose_today = models.SmallIntegerField()
    subpurpose_today = models.SmallIntegerField()
    main_matter_cino = models.CharField(max_length=16, blank=True, null=True)
    lcc_applied_date = models.DateField(blank=True, null=True)
    lcc_received_date = models.DateField(blank=True, null=True)
    split_case_refno = models.CharField(max_length=15, blank=True, null=True)
    split_case_flag = models.TextField()  # This field type is a guess.
    jocode = models.CharField(max_length=150, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    dormant_sinedie = models.CharField(max_length=1, blank=True, null=True)
    pet_inperson = models.CharField(max_length=1, blank=True, null=True)
    res_inperson = models.CharField(max_length=1, blank=True, null=True)
    pet_status = models.IntegerField()
    res_status = models.IntegerField()
    lower_judge_name = models.CharField(max_length=100, blank=True, null=True)
    lowerjocode = models.CharField(max_length=150, blank=True, null=True)
    grouped = models.CharField(max_length=1, blank=True, null=True)
    lpet_occu = models.CharField(max_length=50, blank=True, null=True)
    lres_occu = models.CharField(max_length=50, blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    lower_cino = models.CharField(max_length=16, blank=True, null=True)
    efilno = models.CharField(primary_key=True, max_length=99)
    econfirm = models.CharField(max_length=1, blank=True, null=True)
    efil_dt = models.DateField(blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    res_state_id = models.IntegerField(blank=True, null=True)
    state_id3 = models.IntegerField(blank=True, null=True)
    state_id4 = models.IntegerField(blank=True, null=True)
    lower_state_id = models.IntegerField(blank=True, null=True)
    link_criteria = models.CharField(max_length=1, blank=True, null=True)
    subnature_cd1 = models.CharField(max_length=25, blank=True, null=True)
    subnature_cd2 = models.CharField(max_length=25, blank=True, null=True)
    branch_id = models.IntegerField(blank=True, null=True)
    bench_type = models.IntegerField(blank=True, null=True)
    sr_no = models.IntegerField(blank=True, null=True)
    causelist_type = models.IntegerField(blank=True, null=True)
    next_date_check = models.CharField(max_length=1, blank=True, null=True)
    status_id = models.IntegerField(blank=True, null=True)
    lower_dist_code = models.IntegerField(blank=True, null=True)
    lregis_date = models.DateField(blank=True, null=True)
    lower_taluka_code = models.IntegerField(blank=True, null=True)
    c_subject = models.IntegerField(blank=True, null=True)
    cs_subject = models.IntegerField(blank=True, null=True)
    css_subject = models.IntegerField(blank=True, null=True)
    police_state_id = models.IntegerField(blank=True, null=True)
    police_dist_code = models.IntegerField(blank=True, null=True)
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    desig_code = models.CharField(max_length=50, blank=True, null=True)
    case_state_code = models.IntegerField(blank=True, null=True)
    case_dist_code = models.IntegerField(blank=True, null=True)
    pet_gender = models.CharField(max_length=1, blank=True, null=True)
    res_gender = models.CharField(max_length=1, blank=True, null=True)
    pet_salutation = models.SmallIntegerField(blank=True, null=True)
    res_salutation = models.SmallIntegerField(blank=True, null=True)
    ref_m_efiled_type_id = models.IntegerField(blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    create_by_ip = models.CharField(max_length=30, blank=True, null=True)
    efiling_year = models.CharField(max_length=10, blank=True, null=True)
    create_on = models.DateTimeField(blank=True, null=True)
    eflag = models.CharField(max_length=1, blank=True, null=True)
    adv_mobile = models.CharField(max_length=15, blank=True, null=True)
    adv_email = models.CharField(max_length=254, blank=True, null=True)
    bar_code = models.CharField(max_length=20, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    case_taluka_code = models.SmallIntegerField(blank=True, null=True)
    case_village_code = models.SmallIntegerField(blank=True, null=True)
    efiling_type = models.CharField(max_length=1, blank=True, null=True)
    proposed_fine = models.DecimalField(max_digits=17, decimal_places=2)
    fir_date = models.DateField(blank=True, null=True)
    inv_agency_code = models.SmallIntegerField()
    vcourt_cnr = models.CharField(max_length=16)

    class Meta:
        managed = False
        db_table = 'ecivil_t'


class EcivilTRejected(models.Model):
    pk = models.CompositePrimaryKey('efilno', 'create_modify')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    pet_name = models.CharField(max_length=100, blank=True, null=True)
    lpet_name = models.CharField(max_length=100, blank=True, null=True)
    pet_sex = models.CharField(max_length=1, blank=True, null=True)
    res_name = models.CharField(max_length=100, blank=True, null=True)
    lres_name = models.CharField(max_length=100, blank=True, null=True)
    res_sex = models.CharField(max_length=1, blank=True, null=True)
    court_no = models.IntegerField()
    file_before = models.IntegerField()
    date_of_filing = models.DateField(blank=True, null=True)
    time_of_filing = models.TimeField(blank=True, null=True)
    date_of_present = models.DateField(blank=True, null=True)
    date_first_list = models.DateField(blank=True, null=True)
    date_next_list = models.DateField(blank=True, null=True)
    date_last_list = models.DateField(blank=True, null=True)
    date_of_decision = models.DateField(blank=True, null=True)
    dec_jud_name = models.CharField(max_length=100, blank=True, null=True)
    pet_adv = models.CharField(max_length=100, blank=True, null=True)
    pet_adv_cd = models.BigIntegerField()
    lpet_adv = models.CharField(max_length=100, blank=True, null=True)
    res_adv = models.CharField(max_length=100, blank=True, null=True)
    res_adv_cd = models.BigIntegerField()
    lres_adv = models.CharField(max_length=100, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2)
    juri_value = models.CharField(max_length=25)
    purpose_prev = models.SmallIntegerField()
    purpose_next = models.SmallIntegerField()
    purpose_filing = models.CharField(max_length=255, blank=True, null=True)
    under_sec1 = models.CharField(max_length=100, blank=True, null=True)
    under_act1 = models.IntegerField()
    under_sec2 = models.CharField(max_length=100, blank=True, null=True)
    under_act2 = models.IntegerField()
    under_sec3 = models.CharField(max_length=100, blank=True, null=True)
    under_act3 = models.IntegerField()
    under_sec4 = models.CharField(max_length=100, blank=True, null=True)
    under_act4 = models.IntegerField()
    subject = models.CharField(max_length=255, blank=True, null=True)
    subject1 = models.CharField(max_length=255, blank=True, null=True)
    subject2 = models.CharField(max_length=255, blank=True, null=True)
    subject3 = models.CharField(max_length=255, blank=True, null=True)
    caveat = models.CharField(max_length=255, blank=True, null=True)
    order_passed = models.IntegerField()
    order_passed1 = models.CharField(max_length=255, blank=True, null=True)
    unit = models.DecimalField(max_digits=17, decimal_places=2)
    goshwara_no = models.SmallIntegerField()
    lower_court_code = models.SmallIntegerField()
    filing_case = models.SmallIntegerField()
    lower_court = models.CharField(max_length=40, blank=True, null=True)
    lower_court_dec_dt = models.DateField(blank=True, null=True)
    deleted = models.CharField(max_length=1, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    dt_of_mod = models.DateTimeField(blank=True, null=True)
    petadd = models.TextField(blank=True, null=True)
    lpetadd = models.TextField(blank=True, null=True)
    resadd = models.TextField(blank=True, null=True)
    lresadd = models.TextField(blank=True, null=True)
    disp_nature = models.SmallIntegerField()
    tr_from_court = models.SmallIntegerField()
    tr_date = models.DateField(blank=True, null=True)
    pet_father_name = models.CharField(max_length=100, blank=True, null=True)
    lpet_father_name = models.CharField(max_length=100, blank=True, null=True)
    pet_father_flag = models.CharField(max_length=2, blank=True, null=True)
    pet_nationality = models.CharField(max_length=99, blank=True, null=True)
    pet_caste = models.CharField(max_length=2, blank=True, null=True)
    pet_age = models.SmallIntegerField()
    pet_email = models.CharField(max_length=254, blank=True, null=True)
    pet_mobile = models.CharField(max_length=15, blank=True, null=True)
    pet_phone = models.CharField(max_length=15, blank=True, null=True)
    pet_fax = models.CharField(max_length=15, blank=True, null=True)
    pet_occu = models.CharField(max_length=50, blank=True, null=True)
    res_father_name = models.CharField(max_length=100, blank=True, null=True)
    lres_father_name = models.CharField(max_length=100, blank=True, null=True)
    res_father_flag = models.CharField(max_length=2, blank=True, null=True)
    res_nationality = models.CharField(max_length=99, blank=True, null=True)
    res_caste = models.CharField(max_length=2, blank=True, null=True)
    res_age = models.SmallIntegerField()
    res_email = models.CharField(max_length=254, blank=True, null=True)
    res_mobile = models.CharField(max_length=15, blank=True, null=True)
    res_phone = models.CharField(max_length=15, blank=True, null=True)
    res_fax = models.CharField(max_length=15, blank=True, null=True)
    res_occu = models.CharField(max_length=50, blank=True, null=True)
    dt_regis = models.DateField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    date_filing_disp = models.DateField(blank=True, null=True)
    pet_legal_heir = models.TextField()  # This field type is a guess.
    res_legal_heir = models.TextField()  # This field type is a guess.
    update_date = models.DateTimeField(blank=True, null=True)
    pet_occupation = models.CharField(max_length=50, blank=True, null=True)
    res_occupation = models.CharField(max_length=50, blank=True, null=True)
    police_st_code = models.IntegerField()
    fir_no = models.CharField(max_length=15, blank=True, null=True)
    fir_type_code = models.SmallIntegerField()
    fir_year = models.SmallIntegerField()
    session_magistrate = models.SmallIntegerField()
    police_private = models.SmallIntegerField()
    ci_cri = models.SmallIntegerField()
    offense_date = models.DateField(blank=True, null=True)
    dt_chargesheet = models.DateField(blank=True, null=True)
    link_code = models.CharField(max_length=15, blank=True, null=True)
    reason_for_rej = models.TextField(blank=True, null=True)
    lreason_for_rej = models.TextField(blank=True, null=True)
    not_before_me = models.CharField(max_length=50, blank=True, null=True)
    before_me = models.CharField(max_length=50, blank=True, null=True)
    obj_redate = models.DateField(blank=True, null=True)
    obj_flag = models.TextField()  # This field type is a guess.
    objreceipt_dt = models.DateField(blank=True, null=True)
    objreturn_dt = models.DateField(blank=True, null=True)
    objprepare_dt = models.DateField(blank=True, null=True)
    objection = models.TextField(blank=True, null=True)
    objdescription = models.TextField(blank=True, null=True)
    lobjection = models.CharField(max_length=250, blank=True, null=True)
    date_filing_disp_o = models.DateField(blank=True, null=True)
    date_filing_restore = models.DateField(blank=True, null=True)
    date_of_decision_o = models.DateField(blank=True, null=True)
    date_of_revoke = models.DateField(blank=True, null=True)
    urgent = models.TextField()  # This field type is a guess.
    main_case_no = models.CharField(max_length=15, blank=True, null=True)
    pet_add2 = models.CharField(max_length=255, blank=True, null=True)
    lpet_add2 = models.CharField(max_length=255, blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    res_dist = models.SmallIntegerField()
    res_taluka = models.SmallIntegerField()
    res_village = models.IntegerField()
    res_village1 = models.IntegerField()
    res_village2 = models.IntegerField()
    res_town_code = models.IntegerField()
    res_ward_code = models.IntegerField()
    res_add2 = models.CharField(max_length=255, blank=True, null=True)
    lres_add2 = models.CharField(max_length=255, blank=True, null=True)
    dist_code3 = models.SmallIntegerField()
    taluka_code3 = models.SmallIntegerField()
    village_code3 = models.IntegerField()
    village1_code3 = models.IntegerField()
    village2_code3 = models.IntegerField()
    town_code3 = models.IntegerField()
    ward_code3 = models.IntegerField()
    dist_code4 = models.SmallIntegerField()
    taluka_code4 = models.SmallIntegerField()
    village_code4 = models.IntegerField()
    village1_code4 = models.IntegerField()
    village2_code4 = models.IntegerField()
    town_code4 = models.IntegerField()
    ward_code4 = models.IntegerField()
    chk = models.CharField(max_length=50, blank=True, null=True)
    pet_passportno = models.CharField(max_length=25, blank=True, null=True)
    pet_country = models.CharField(max_length=99, blank=True, null=True)
    pet_pincode = models.IntegerField(blank=True, null=True)
    res_passportno = models.CharField(max_length=25, blank=True, null=True)
    res_country = models.CharField(max_length=99, blank=True, null=True)
    res_pincode = models.IntegerField(blank=True, null=True)
    reg_pl = models.CharField(max_length=1, blank=True, null=True)
    orgid = models.SmallIntegerField(blank=True, null=True)
    resorgid = models.SmallIntegerField(blank=True, null=True)
    pet_dob = models.DateField(blank=True, null=True)
    res_dob = models.DateField(blank=True, null=True)
    plead_guilty = models.TextField()  # This field type is a guess.
    nature_cd = models.CharField(max_length=25, blank=True, null=True)
    relief_offense = models.TextField(blank=True, null=True)
    lrelief_offence = models.TextField(blank=True, null=True)
    causeofaction = models.TextField(blank=True, null=True)
    lcauseofaction = models.TextField(blank=True, null=True)
    legacy_flag = models.TextField()  # This field type is a guess.
    pet_extracount = models.IntegerField()
    res_extracount = models.IntegerField()
    order_sect_kar = models.TextField(blank=True, null=True)
    nature_kar = models.TextField(blank=True, null=True)
    allocation_dt = models.DateField(blank=True, null=True)
    rej_sr_no = models.IntegerField()
    unit_type = models.CharField(max_length=150, blank=True, null=True)
    unit_type_value = models.CharField(max_length=150, blank=True, null=True)
    transfer_est = models.TextField()  # This field type is a guess.
    imprisonment = models.SmallIntegerField()
    bal_fee_date = models.DateField(blank=True, null=True)
    pet_uid = models.BigIntegerField(blank=True, null=True)
    res_uid = models.BigIntegerField(blank=True, null=True)
    reasonregisdate = models.TextField(blank=True, null=True)
    oldcase_no = models.CharField(max_length=16, blank=True, null=True)
    performaresflag = models.TextField()  # This field type is a guess.
    petpanno = models.CharField(max_length=10, blank=True, null=True)
    respanno = models.CharField(max_length=10, blank=True, null=True)
    reasonfilingdate = models.CharField(max_length=255, blank=True, null=True)
    oldfiling_no = models.CharField(max_length=16, blank=True, null=True)
    hide_pet_name = models.CharField(max_length=1)
    hide_res_name = models.CharField(max_length=1)
    hide_partyname = models.CharField(max_length=1)
    petpolice_st_code = models.IntegerField()
    respolice_st_code = models.IntegerField()
    investofficer = models.CharField(max_length=100, blank=True, null=True)
    linvestofficer = models.CharField(max_length=100, blank=True, null=True)
    beltno = models.CharField(max_length=50, blank=True, null=True)
    investofficer1 = models.CharField(max_length=100, blank=True, null=True)
    linvestofficer1 = models.CharField(max_length=100, blank=True, null=True)
    beltno1 = models.CharField(max_length=50, blank=True, null=True)
    pet_org_contact_person = models.CharField(max_length=100, blank=True, null=True)
    petorg_person = models.CharField(max_length=100, blank=True, null=True)
    res_org_contact_person = models.CharField(max_length=100, blank=True, null=True)
    resorg_person = models.CharField(max_length=100, blank=True, null=True)
    filcase_type = models.SmallIntegerField(blank=True, null=True)
    fil_no = models.IntegerField(blank=True, null=True)
    fil_year = models.SmallIntegerField(blank=True, null=True)
    regcase_type = models.SmallIntegerField(blank=True, null=True)
    reg_no = models.IntegerField(blank=True, null=True)
    reg_year = models.SmallIntegerField(blank=True, null=True)
    goshwara_no_o = models.SmallIntegerField()
    disp_nature_o = models.SmallIntegerField()
    archive = models.TextField()  # This field type is a guess.
    tab_status = models.CharField(max_length=15, blank=True, null=True)
    lsubject1 = models.CharField(max_length=255, blank=True, null=True)
    pending_ia = models.TextField()  # This field type is a guess.
    ia_next_date = models.DateField(blank=True, null=True)
    time_slot = models.IntegerField(blank=True, null=True)
    pet_ph = models.TextField()  # This field type is a guess.
    res_ph = models.TextField()  # This field type is a guess.
    purpose_today = models.SmallIntegerField()
    subpurpose_today = models.SmallIntegerField()
    main_matter_cino = models.CharField(max_length=16, blank=True, null=True)
    lcc_applied_date = models.DateField(blank=True, null=True)
    lcc_received_date = models.DateField(blank=True, null=True)
    split_case_refno = models.CharField(max_length=15, blank=True, null=True)
    split_case_flag = models.TextField()  # This field type is a guess.
    jocode = models.CharField(max_length=150, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    dormant_sinedie = models.CharField(max_length=1, blank=True, null=True)
    pet_inperson = models.CharField(max_length=1, blank=True, null=True)
    res_inperson = models.CharField(max_length=1, blank=True, null=True)
    pet_status = models.IntegerField()
    res_status = models.IntegerField()
    lower_judge_name = models.CharField(max_length=100, blank=True, null=True)
    lowerjocode = models.CharField(max_length=150, blank=True, null=True)
    grouped = models.CharField(max_length=1, blank=True, null=True)
    lpet_occu = models.CharField(max_length=50, blank=True, null=True)
    lres_occu = models.CharField(max_length=50, blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    lower_cino = models.CharField(max_length=16, blank=True, null=True)
    efilno = models.CharField(max_length=99)
    econfirm = models.CharField(max_length=1, blank=True, null=True)
    efil_dt = models.DateField(blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    res_state_id = models.IntegerField(blank=True, null=True)
    state_id3 = models.IntegerField(blank=True, null=True)
    state_id4 = models.IntegerField(blank=True, null=True)
    lower_state_id = models.IntegerField(blank=True, null=True)
    link_criteria = models.CharField(max_length=1, blank=True, null=True)
    subnature_cd1 = models.CharField(max_length=25, blank=True, null=True)
    subnature_cd2 = models.CharField(max_length=25, blank=True, null=True)
    branch_id = models.IntegerField(blank=True, null=True)
    bench_type = models.IntegerField(blank=True, null=True)
    sr_no = models.IntegerField(blank=True, null=True)
    causelist_type = models.IntegerField(blank=True, null=True)
    next_date_check = models.CharField(max_length=1, blank=True, null=True)
    status_id = models.IntegerField(blank=True, null=True)
    lower_dist_code = models.IntegerField(blank=True, null=True)
    lregis_date = models.DateField(blank=True, null=True)
    lower_taluka_code = models.IntegerField(blank=True, null=True)
    c_subject = models.IntegerField(blank=True, null=True)
    cs_subject = models.IntegerField(blank=True, null=True)
    css_subject = models.IntegerField(blank=True, null=True)
    police_state_id = models.IntegerField(blank=True, null=True)
    police_dist_code = models.IntegerField(blank=True, null=True)
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    desig_code = models.CharField(max_length=50, blank=True, null=True)
    case_state_code = models.IntegerField(blank=True, null=True)
    case_dist_code = models.IntegerField(blank=True, null=True)
    pet_gender = models.CharField(max_length=1, blank=True, null=True)
    res_gender = models.CharField(max_length=1, blank=True, null=True)
    pet_salutation = models.SmallIntegerField(blank=True, null=True)
    res_salutation = models.SmallIntegerField(blank=True, null=True)
    ref_m_efiled_type_id = models.IntegerField(blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    create_by_ip = models.CharField(max_length=30, blank=True, null=True)
    efiling_year = models.CharField(max_length=10, blank=True, null=True)
    create_on = models.DateTimeField(blank=True, null=True)
    eflag = models.CharField(max_length=1, blank=True, null=True)
    adv_mobile = models.CharField(max_length=15, blank=True, null=True)
    adv_email = models.CharField(max_length=254, blank=True, null=True)
    bar_code = models.CharField(max_length=20, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField()
    case_taluka_code = models.SmallIntegerField(blank=True, null=True)
    case_village_code = models.SmallIntegerField(blank=True, null=True)
    efiling_type = models.CharField(max_length=1, blank=True, null=True)
    proposed_fine = models.DecimalField(max_digits=17, decimal_places=2)
    fir_date = models.DateField(blank=True, null=True)
    inv_agency_code = models.SmallIntegerField()
    vcourt_cnr = models.CharField(max_length=16)

    class Meta:
        managed = False
        db_table = 'ecivil_t_rejected'


class EextraactT(models.Model):
    pk = models.CompositePrimaryKey('efilno', 'serialno')
    serialno = models.SmallIntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    acts = models.BigIntegerField()
    section = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    cino = models.CharField(max_length=16, blank=True, null=True)
    efilno = models.CharField(max_length=99)
    econfirm = models.CharField(max_length=1, blank=True, null=True)
    create_on = models.DateTimeField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eextraact_t'


class EfeesT(models.Model):
    pk = models.CompositePrimaryKey('todays_date', 'receipt_no', 'item_no', 'efilno')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    court_no = models.IntegerField()
    pet_res = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2)
    fees_type = models.SmallIntegerField(blank=True, null=True)
    document_type = models.SmallIntegerField()
    todays_date = models.DateField()
    display = models.TextField()  # This field type is a guess.
    filing = models.CharField(max_length=1, blank=True, null=True)
    type = models.SmallIntegerField()
    bank_code = models.CharField(max_length=15, blank=True, null=True)
    paymode = models.SmallIntegerField()
    dd_num = models.CharField(max_length=25, blank=True, null=True)
    dd_date = models.DateField(blank=True, null=True)
    receipt_no = models.IntegerField()
    casenotype = models.CharField(max_length=1, blank=True, null=True)
    receipt_status = models.CharField(max_length=1)
    item_no = models.SmallIntegerField()
    party_no = models.SmallIntegerField()
    cino = models.CharField(max_length=16, blank=True, null=True)
    cause_list_type = models.IntegerField(blank=True, null=True)
    court_fee = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    aff_fee = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    vak_fee = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    other = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    ia_no = models.CharField(max_length=12, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    efilno = models.CharField(max_length=20)
    create_on = models.DateTimeField(blank=True, null=True)
    econfirm = models.CharField(max_length=1, blank=True, null=True)
    reason_for_rej = models.TextField(blank=True, null=True)
    lreason_for_rej = models.TextField(blank=True, null=True)
    efiling_receipt_no = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'efees_t'


class EfeesTRejected(models.Model):
    pk = models.CompositePrimaryKey('efilno', 'create_modify')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    court_no = models.IntegerField()
    pet_res = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2)
    fees_type = models.SmallIntegerField(blank=True, null=True)
    document_type = models.SmallIntegerField()
    todays_date = models.DateField()
    display = models.TextField()  # This field type is a guess.
    filing = models.CharField(max_length=1, blank=True, null=True)
    type = models.SmallIntegerField()
    bank_code = models.CharField(max_length=15, blank=True, null=True)
    paymode = models.SmallIntegerField()
    dd_num = models.CharField(max_length=25, blank=True, null=True)
    dd_date = models.DateField(blank=True, null=True)
    receipt_no = models.IntegerField()
    casenotype = models.CharField(max_length=1, blank=True, null=True)
    receipt_status = models.CharField(max_length=1)
    item_no = models.SmallIntegerField()
    party_no = models.SmallIntegerField()
    cino = models.CharField(max_length=16, blank=True, null=True)
    cause_list_type = models.IntegerField(blank=True, null=True)
    court_fee = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    aff_fee = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    vak_fee = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    other = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    ia_no = models.CharField(max_length=12, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField()
    efilno = models.CharField(max_length=20)
    create_on = models.DateTimeField(blank=True, null=True)
    econfirm = models.CharField(max_length=1, blank=True, null=True)
    reason_for_rej = models.TextField(blank=True, null=True)
    lreason_for_rej = models.TextField(blank=True, null=True)
    efiling_receipt_no = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'efees_t_rejected'


class EfilingConfig(models.Model):
    euserid = models.CharField(max_length=150, blank=True, null=True)
    epassword = models.CharField(max_length=150, blank=True, null=True)
    efiling_url = models.TextField(blank=True, null=True)
    nuserid = models.CharField(max_length=150, blank=True, null=True)
    npassword = models.CharField(max_length=150, blank=True, null=True)
    nstep_url = models.TextField(blank=True, null=True)
    est_code = models.CharField(primary_key=True, max_length=6)
    efiling_vd_userid = models.CharField(max_length=150, blank=True, null=True)
    efiling_vd_password = models.CharField(max_length=150, blank=True, null=True)
    efiling_vd_url = models.TextField(blank=True, null=True)
    appellate_userid = models.CharField(max_length=150, blank=True, null=True)
    appellate_password = models.CharField(max_length=150, blank=True, null=True)
    appellate_url = models.TextField(blank=True, null=True)
    plead_guilty_userid = models.CharField(max_length=150, blank=True, null=True)
    plead_guilty_password = models.CharField(max_length=150, blank=True, null=True)
    plead_guilty_url = models.TextField(blank=True, null=True)
    fir_userid = models.CharField(max_length=150, blank=True, null=True)
    fir_password = models.CharField(max_length=150, blank=True, null=True)
    fir_url = models.TextField(blank=True, null=True)
    rto_userid = models.CharField(max_length=150, blank=True, null=True)
    rto_password = models.CharField(max_length=150, blank=True, null=True)
    rto_url = models.TextField(blank=True, null=True)
    other_userid = models.CharField(max_length=150, blank=True, null=True)
    other_password = models.CharField(max_length=150, blank=True, null=True)
    other_url = models.TextField(blank=True, null=True)
    other1_userid = models.CharField(max_length=150, blank=True, null=True)
    other1_password = models.CharField(max_length=150, blank=True, null=True)
    other1_url = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    pdf_userid = models.CharField(max_length=150, blank=True, null=True)
    pdf_password = models.CharField(max_length=150, blank=True, null=True)
    pdf_url = models.TextField(blank=True, null=True)
    nstep_date = models.DateTimeField(blank=True, null=True)
    last_nstep_date = models.DateTimeField(blank=True, null=True)
    vc_pull_date = models.DateTimeField(blank=True, null=True)
    appleat_key = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'efiling_config'


class EgrassT(models.Model):
    pk = models.CompositePrimaryKey('department_id', 'grn')
    department_id = models.CharField(max_length=40)
    grn = models.CharField(max_length=30)
    amount = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    bankcode = models.CharField(max_length=10, blank=True, null=True)
    bankcin = models.CharField(max_length=20, blank=True, null=True)
    prn = models.CharField(max_length=40, blank=True, null=True)
    transcompletiondatetime = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    partyname = models.CharField(max_length=75, blank=True, null=True)
    taxid = models.CharField(max_length=25, blank=True, null=True)
    bankname = models.CharField(max_length=250, blank=True, null=True)
    entry_date = models.DateField(blank=True, null=True)
    efiling_no = models.CharField(max_length=20, blank=True, null=True)
    efiling_year = models.IntegerField(blank=True, null=True)
    create_on = models.DateTimeField(blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    reason_for_rej = models.TextField(blank=True, null=True)
    lreason_for_rej = models.TextField(blank=True, null=True)
    econfirm = models.CharField(max_length=1, blank=True, null=True)
    eflag = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'egrass_t'


class EgrassTRejected(models.Model):
    pk = models.CompositePrimaryKey('create_modify', 'efiling_no')
    department_id = models.CharField(max_length=40)
    grn = models.CharField(max_length=30)
    amount = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    bankcode = models.CharField(max_length=10, blank=True, null=True)
    bankcin = models.CharField(max_length=20, blank=True, null=True)
    prn = models.CharField(max_length=40, blank=True, null=True)
    transcompletiondatetime = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    partyname = models.CharField(max_length=75, blank=True, null=True)
    taxid = models.CharField(max_length=25, blank=True, null=True)
    bankname = models.CharField(max_length=250, blank=True, null=True)
    entry_date = models.DateField(blank=True, null=True)
    efiling_no = models.CharField(max_length=20)
    efiling_year = models.IntegerField(blank=True, null=True)
    create_on = models.DateTimeField(blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    reason_for_rej = models.TextField(blank=True, null=True)
    lreason_for_rej = models.TextField(blank=True, null=True)
    econfirm = models.CharField(max_length=1, blank=True, null=True)
    eflag = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'egrass_t_rejected'


class EiaExtraAdvT(models.Model):
    pk = models.CompositePrimaryKey('party_no', 'efilia_no')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    ia_no = models.CharField(max_length=12, blank=True, null=True)
    pet_res = models.CharField(max_length=99, blank=True, null=True)
    lpet_res = models.CharField(max_length=99, blank=True, null=True)
    type = models.SmallIntegerField()
    adv_name = models.CharField(max_length=500, blank=True, null=True)
    ladv_name = models.CharField(max_length=100, blank=True, null=True)
    adv_code = models.BigIntegerField()
    party_no = models.SmallIntegerField()
    sr_no = models.SmallIntegerField(blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.IntegerField()
    ia_case_type = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    efilno = models.CharField(max_length=20)
    efilia_no = models.CharField(max_length=20)
    efildt = models.DateField(blank=True, null=True)
    econfirm = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eia_extra_adv_t'


class EiaFiling(models.Model):
    court_no = models.IntegerField()
    case_fr = models.SmallIntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    ia_no = models.CharField(max_length=12, blank=True, null=True)
    ia_registrationo = models.CharField(max_length=12, blank=True, null=True)
    party_applying = models.CharField(max_length=10, blank=True, null=True)
    party_applying_code = models.TextField(blank=True, null=True)
    appotherparty = models.CharField(max_length=99, blank=True, null=True)
    appotheradv = models.CharField(max_length=99, blank=True, null=True)
    against_whom = models.CharField(max_length=10, blank=True, null=True)
    against_whom_code = models.TextField(blank=True, null=True)
    againotherparty = models.CharField(max_length=99, blank=True, null=True)
    againotheradv = models.CharField(max_length=99, blank=True, null=True)
    purpose_code = models.BigIntegerField()
    relief_offense = models.TextField(blank=True, null=True)
    date_of_ia_filing = models.DateField(blank=True, null=True)
    date_of_ia_registration = models.DateField(blank=True, null=True)
    date_of_serving_notice = models.DateField(blank=True, null=True)
    date_of_hearing = models.DateField(blank=True, null=True)
    date_of_order = models.DateField(blank=True, null=True)
    disposal_date = models.DateField(blank=True, null=True)
    disp_nature = models.IntegerField()
    order_code = models.SmallIntegerField()
    court_fee = models.IntegerField()
    act_code = models.IntegerField()
    under_sec = models.CharField(max_length=100, blank=True, null=True)
    unit = models.DecimalField(max_digits=17, decimal_places=2)
    goshwara_no = models.SmallIntegerField()
    order_remark = models.TextField(blank=True, null=True)
    exhibit = models.TextField(blank=True, null=True)
    dt_of_entry = models.DateTimeField()
    objcompl_date = models.DateField(blank=True, null=True)
    obj_flag = models.CharField(max_length=1, blank=True, null=True)
    objreceipt_dt = models.DateField(blank=True, null=True)
    objreturn_dt = models.DateField(blank=True, null=True)
    objprepare_dt = models.DateField(blank=True, null=True)
    objection = models.CharField(max_length=500, blank=True, null=True)
    objdescription = models.TextField(blank=True, null=True)
    lobjection = models.CharField(max_length=500, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    date_filing_disp = models.DateField(blank=True, null=True)
    reason_for_rej = models.TextField(blank=True, null=True)
    lreason_for_rej = models.TextField(blank=True, null=True)
    date_of_decision_o = models.DateField(blank=True, null=True)
    date_of_revoke = models.DateField(blank=True, null=True)
    unit_type = models.SmallIntegerField()
    nature_cd = models.SmallIntegerField()
    ia_filno = models.IntegerField(blank=True, null=True)
    ia_filyear = models.SmallIntegerField(blank=True, null=True)
    ia_regno = models.IntegerField(blank=True, null=True)
    ia_regyear = models.SmallIntegerField(blank=True, null=True)
    filcasetype = models.SmallIntegerField(blank=True, null=True)
    fil_no = models.IntegerField(blank=True, null=True)
    fil_year = models.SmallIntegerField(blank=True, null=True)
    regcasetype = models.SmallIntegerField(blank=True, null=True)
    reg_no = models.IntegerField(blank=True, null=True)
    reg_year = models.SmallIntegerField(blank=True, null=True)
    app_extra_adv = models.TextField(blank=True, null=True)
    again_extra_adv = models.TextField(blank=True, null=True)
    subpurpose_code = models.IntegerField()
    oldiafiling_no = models.CharField(max_length=15, blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    old_ia_no = models.CharField(max_length=16, blank=True, null=True)
    old_ia_registrationo = models.CharField(max_length=16, blank=True, null=True)
    indispose = models.CharField(max_length=1, blank=True, null=True)
    jocode = models.CharField(max_length=150, blank=True, null=True)
    desig_code = models.CharField(max_length=50, blank=True, null=True)
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    case_remark = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    dangling_ia_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    appotheradv_code = models.BigIntegerField(blank=True, null=True)
    againotheradv_code = models.BigIntegerField(blank=True, null=True)
    app_extra_adv_code = models.CharField(max_length=250, blank=True, null=True)
    again_extra_adv_code = models.CharField(max_length=250, blank=True, null=True)
    afidvt = models.IntegerField(blank=True, null=True)
    revoke_remark = models.TextField(blank=True, null=True)
    no_of_leaves = models.IntegerField(blank=True, null=True)
    ia_case_type = models.IntegerField()
    lorder_remark = models.TextField(blank=True, null=True)
    lexhibit = models.TextField(blank=True, null=True)
    short_order = models.CharField(max_length=50, blank=True, null=True)
    efilno = models.CharField(max_length=20)
    efilia_no = models.CharField(primary_key=True, max_length=20)
    efildt = models.DateField(blank=True, null=True)
    econfirm = models.CharField(max_length=1, blank=True, null=True)
    filing_counter_flag = models.TextField()  # This field type is a guess.
    create_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eia_filing'


class EiaFilingRejected(models.Model):
    pk = models.CompositePrimaryKey('efilia_no', 'create_modify')
    court_no = models.IntegerField()
    case_fr = models.SmallIntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    ia_no = models.CharField(max_length=12, blank=True, null=True)
    ia_registrationo = models.CharField(max_length=12, blank=True, null=True)
    party_applying = models.CharField(max_length=10, blank=True, null=True)
    party_applying_code = models.TextField(blank=True, null=True)
    appotherparty = models.CharField(max_length=99, blank=True, null=True)
    appotheradv = models.CharField(max_length=99, blank=True, null=True)
    against_whom = models.CharField(max_length=10, blank=True, null=True)
    against_whom_code = models.TextField(blank=True, null=True)
    againotherparty = models.CharField(max_length=99, blank=True, null=True)
    againotheradv = models.CharField(max_length=99, blank=True, null=True)
    purpose_code = models.BigIntegerField()
    relief_offense = models.TextField(blank=True, null=True)
    date_of_ia_filing = models.DateField(blank=True, null=True)
    date_of_ia_registration = models.DateField(blank=True, null=True)
    date_of_serving_notice = models.DateField(blank=True, null=True)
    date_of_hearing = models.DateField(blank=True, null=True)
    date_of_order = models.DateField(blank=True, null=True)
    disposal_date = models.DateField(blank=True, null=True)
    disp_nature = models.IntegerField()
    order_code = models.SmallIntegerField()
    court_fee = models.IntegerField()
    act_code = models.IntegerField()
    under_sec = models.CharField(max_length=100, blank=True, null=True)
    unit = models.DecimalField(max_digits=17, decimal_places=2)
    goshwara_no = models.SmallIntegerField()
    order_remark = models.TextField(blank=True, null=True)
    exhibit = models.TextField(blank=True, null=True)
    dt_of_entry = models.DateTimeField()
    objcompl_date = models.DateField(blank=True, null=True)
    obj_flag = models.CharField(max_length=1, blank=True, null=True)
    objreceipt_dt = models.DateField(blank=True, null=True)
    objreturn_dt = models.DateField(blank=True, null=True)
    objprepare_dt = models.DateField(blank=True, null=True)
    objection = models.CharField(max_length=500, blank=True, null=True)
    objdescription = models.TextField(blank=True, null=True)
    lobjection = models.CharField(max_length=500, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    date_filing_disp = models.DateField(blank=True, null=True)
    reason_for_rej = models.TextField(blank=True, null=True)
    lreason_for_rej = models.TextField(blank=True, null=True)
    date_of_decision_o = models.DateField(blank=True, null=True)
    date_of_revoke = models.DateField(blank=True, null=True)
    unit_type = models.SmallIntegerField()
    nature_cd = models.SmallIntegerField()
    ia_filno = models.IntegerField(blank=True, null=True)
    ia_filyear = models.SmallIntegerField(blank=True, null=True)
    ia_regno = models.IntegerField(blank=True, null=True)
    ia_regyear = models.SmallIntegerField(blank=True, null=True)
    filcasetype = models.SmallIntegerField(blank=True, null=True)
    fil_no = models.IntegerField(blank=True, null=True)
    fil_year = models.SmallIntegerField(blank=True, null=True)
    regcasetype = models.SmallIntegerField(blank=True, null=True)
    reg_no = models.IntegerField(blank=True, null=True)
    reg_year = models.SmallIntegerField(blank=True, null=True)
    app_extra_adv = models.TextField(blank=True, null=True)
    again_extra_adv = models.TextField(blank=True, null=True)
    subpurpose_code = models.IntegerField()
    oldiafiling_no = models.CharField(max_length=15, blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    old_ia_no = models.CharField(max_length=16, blank=True, null=True)
    old_ia_registrationo = models.CharField(max_length=16, blank=True, null=True)
    indispose = models.CharField(max_length=1, blank=True, null=True)
    jocode = models.CharField(max_length=150, blank=True, null=True)
    desig_code = models.CharField(max_length=50, blank=True, null=True)
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    case_remark = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField()
    dangling_ia_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    appotheradv_code = models.BigIntegerField(blank=True, null=True)
    againotheradv_code = models.BigIntegerField(blank=True, null=True)
    app_extra_adv_code = models.CharField(max_length=250, blank=True, null=True)
    again_extra_adv_code = models.CharField(max_length=250, blank=True, null=True)
    afidvt = models.IntegerField(blank=True, null=True)
    revoke_remark = models.TextField(blank=True, null=True)
    no_of_leaves = models.IntegerField(blank=True, null=True)
    ia_case_type = models.IntegerField()
    lorder_remark = models.TextField(blank=True, null=True)
    lexhibit = models.TextField(blank=True, null=True)
    short_order = models.CharField(max_length=50, blank=True, null=True)
    efilno = models.CharField(max_length=20)
    efilia_no = models.CharField(max_length=20)
    efildt = models.DateField(blank=True, null=True)
    econfirm = models.CharField(max_length=1, blank=True, null=True)
    filing_counter_flag = models.TextField()  # This field type is a guess.
    create_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eia_filing_rejected'


class EiaOtherParty(models.Model):
    pk = models.CompositePrimaryKey('party_no', 'efilia_no')
    party_no = models.SmallIntegerField()
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    lname = models.CharField(max_length=100, blank=True, null=True)
    pet_age = models.SmallIntegerField()
    type = models.SmallIntegerField()
    adv_name = models.CharField(max_length=100, blank=True, null=True)
    ladv_name = models.CharField(max_length=100, blank=True, null=True)
    adv_cd = models.BigIntegerField()
    display = models.TextField()  # This field type is a guess.
    pet_sex = models.CharField(max_length=1, blank=True, null=True)
    party_id = models.TextField(blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    cino = models.CharField(max_length=16)
    pet_gender = models.CharField(max_length=1, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    ia_no = models.CharField(max_length=12)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    ia_case_type = models.IntegerField(blank=True, null=True)
    efilno = models.CharField(max_length=20)
    efilia_no = models.CharField(max_length=20)
    efildt = models.DateField(blank=True, null=True)
    econfirm = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eia_other_party'


class EindexRegister(models.Model):
    pk = models.CompositePrimaryKey('srno', 'efilno')
    caseno = models.CharField(max_length=15, blank=True, null=True)
    srno = models.BigIntegerField()
    description = models.CharField(max_length=150, blank=True, null=True)
    paperdate = models.DateField(blank=True, null=True)
    noofparts = models.CharField(max_length=5, blank=True, null=True)
    alphabetical = models.CharField(max_length=150, blank=True, null=True)
    remarks = models.CharField(max_length=100, blank=True, null=True)
    lalphabetical = models.CharField(max_length=150, blank=True, null=True)
    lremarks = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    upload_date = models.DateTimeField(blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    doc_year = models.IntegerField(blank=True, null=True)
    doc_no = models.IntegerField(blank=True, null=True)
    filing_no = models.CharField(max_length=16, blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    type = models.TextField(blank=True, null=True)  # This field type is a guess.
    party_no = models.IntegerField()
    adv_name = models.CharField(max_length=100, blank=True, null=True)
    adv_cd = models.IntegerField(blank=True, null=True)
    extra_party = models.CharField(max_length=250, blank=True, null=True)
    objection = models.TextField(blank=True, null=True)  # This field type is a guess.
    oldnumber = models.CharField(max_length=16, blank=True, null=True)
    remarks1 = models.CharField(max_length=100, blank=True, null=True)
    advname1 = models.CharField(max_length=100, blank=True, null=True)
    advcd1 = models.IntegerField(blank=True, null=True)
    efil_dt = models.DateField()
    econfirm = models.CharField(max_length=1, blank=True, null=True)
    efilno = models.CharField(max_length=99)
    create_on = models.DateTimeField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    reason_for_rej = models.TextField(blank=True, null=True)
    lreason_for_rej = models.TextField(blank=True, null=True)
    in_person = models.CharField(max_length=1, blank=True, null=True)
    verified_on = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eindex_register'


class EindexRegisterRejected(models.Model):
    pk = models.CompositePrimaryKey('create_modify', 'efilno')
    caseno = models.CharField(max_length=15, blank=True, null=True)
    srno = models.BigIntegerField()
    description = models.CharField(max_length=150, blank=True, null=True)
    paperdate = models.DateField(blank=True, null=True)
    noofparts = models.CharField(max_length=5, blank=True, null=True)
    alphabetical = models.CharField(max_length=150, blank=True, null=True)
    remarks = models.CharField(max_length=100, blank=True, null=True)
    lalphabetical = models.CharField(max_length=150, blank=True, null=True)
    lremarks = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    upload_date = models.DateTimeField(blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    doc_year = models.IntegerField(blank=True, null=True)
    doc_no = models.IntegerField(blank=True, null=True)
    filing_no = models.CharField(max_length=16, blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    type = models.TextField(blank=True, null=True)  # This field type is a guess.
    party_no = models.IntegerField()
    adv_name = models.CharField(max_length=100, blank=True, null=True)
    adv_cd = models.IntegerField(blank=True, null=True)
    extra_party = models.CharField(max_length=250, blank=True, null=True)
    objection = models.TextField(blank=True, null=True)  # This field type is a guess.
    oldnumber = models.CharField(max_length=16, blank=True, null=True)
    remarks1 = models.CharField(max_length=100, blank=True, null=True)
    advname1 = models.CharField(max_length=100, blank=True, null=True)
    advcd1 = models.IntegerField(blank=True, null=True)
    efil_dt = models.DateField()
    econfirm = models.CharField(max_length=1, blank=True, null=True)
    efilno = models.CharField(max_length=99)
    create_on = models.DateTimeField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField()
    reason_for_rej = models.TextField(blank=True, null=True)
    lreason_for_rej = models.TextField(blank=True, null=True)
    in_person = models.CharField(max_length=1, blank=True, null=True)
    verified_on = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eindex_register_rejected'


class EmvcT(models.Model):
    pk = models.CompositePrimaryKey('item_no', 'efilno')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    item_no = models.SmallIntegerField()
    police_stn_code = models.IntegerField()
    other_police_stn = models.CharField(max_length=200, blank=True, null=True)
    fir_no = models.CharField(max_length=15, blank=True, null=True)
    year = models.SmallIntegerField()
    accident_date = models.DateField(blank=True, null=True)
    accident_place = models.CharField(max_length=200, blank=True, null=True)
    compensation = models.CharField(max_length=200, blank=True, null=True)
    insurance_company = models.CharField(max_length=200, blank=True, null=True)
    vehicle_type = models.CharField(max_length=100, blank=True, null=True)
    vehicle_regn_no = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    accident_time = models.TimeField(blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    fir_type_code = models.SmallIntegerField()
    driving_license = models.CharField(max_length=100, blank=True, null=True)
    issuing_authority = models.CharField(max_length=100, blank=True, null=True)
    owner_name = models.CharField(max_length=99, blank=True, null=True)
    lowner_name = models.CharField(max_length=99, blank=True, null=True)
    lissuing_authority = models.CharField(max_length=100, blank=True, null=True)
    laccident_place = models.CharField(max_length=200, blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    efilno = models.CharField(max_length=99)
    econfirm = models.CharField(max_length=1, blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    create_on = models.DateTimeField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    efiling_no = models.CharField(max_length=20, blank=True, null=True)
    efiling_year = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'emvc_t'


class EpartyExtraactT(models.Model):
    pk = models.CompositePrimaryKey('efilno', 'party_no', 'serialno')
    serialno = models.SmallIntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    acts = models.BigIntegerField(blank=True, null=True)
    section = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    cino = models.CharField(max_length=16, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    party_no = models.SmallIntegerField()
    type = models.SmallIntegerField(blank=True, null=True)
    efilno = models.CharField(max_length=99)
    efil_dt = models.DateField(blank=True, null=True)
    econfirm = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eparty_extraact_t'


class EpleadGuilty(models.Model):
    case_no = models.CharField(max_length=15, blank=True, null=True)
    pet_name = models.CharField(max_length=100, blank=True, null=True)
    lpet_name = models.CharField(max_length=100, blank=True, null=True)
    res_name = models.CharField(max_length=100, blank=True, null=True)
    lres_name = models.CharField(max_length=100, blank=True, null=True)
    res_sex = models.CharField(max_length=1, blank=True, null=True)
    res_adv = models.CharField(max_length=500, blank=True, null=True)
    res_adv_cd = models.BigIntegerField(blank=True, null=True)
    lres_adv = models.CharField(max_length=100, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    under_sec1 = models.CharField(max_length=100, blank=True, null=True)
    under_act1 = models.IntegerField(blank=True, null=True)
    goshwara_no = models.SmallIntegerField(blank=True, null=True)
    petadd = models.TextField(blank=True, null=True)
    lpetadd = models.TextField(blank=True, null=True)
    resadd = models.TextField(blank=True, null=True)
    lresadd = models.TextField(blank=True, null=True)
    res_age = models.SmallIntegerField(blank=True, null=True)
    res_email = models.CharField(max_length=254, blank=True, null=True)
    res_mobile = models.CharField(max_length=15, blank=True, null=True)
    police_st_code = models.IntegerField(blank=True, null=True)
    fir_no = models.CharField(max_length=100, blank=True, null=True)
    fir_type_code = models.SmallIntegerField(blank=True, null=True)
    fir_year = models.SmallIntegerField(blank=True, null=True)
    offense_date = models.DateField(blank=True, null=True)
    dt_chargesheet = models.DateField(blank=True, null=True)
    causeofaction = models.TextField(blank=True, null=True)
    lcauseofaction = models.TextField(blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    econfirm = models.CharField(max_length=1, blank=True, null=True)
    efilno = models.CharField(primary_key=True, max_length=99)
    efil_dt = models.DateField()
    res_gender = models.CharField(max_length=1, blank=True, null=True)
    create_on = models.DateTimeField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eplead_guilty'


class EstTransfer(models.Model):
    pk = models.CompositePrimaryKey('cur_db', 'transfer_date', 'cino', 'transfer_receive')
    cur_db = models.CharField(max_length=50)
    cur_case_no = models.CharField(max_length=15, blank=True, null=True)
    cur_filing_no = models.CharField(max_length=15, blank=True, null=True)
    transfer_date = models.DateField()
    trans_db = models.CharField(max_length=50, blank=True, null=True)
    trans_case_no = models.CharField(max_length=15, blank=True, null=True)
    trans_filing_no = models.CharField(max_length=15, blank=True, null=True)
    transfer_receive = models.SmallIntegerField()
    targetcino = models.CharField(max_length=16, blank=True, null=True)
    cino = models.CharField(max_length=16)
    remark = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'est_transfer'


class Establishments(models.Model):
    est_code = models.SmallIntegerField(primary_key=True)
    est_name = models.CharField(max_length=255, blank=True, null=True)
    est_db = models.CharField(max_length=255, blank=True, null=True)
    est_ipaddress = models.CharField(max_length=255, blank=True, null=True)
    est_user = models.CharField(max_length=255, blank=True, null=True)
    est_password = models.CharField(max_length=255, blank=True, null=True)
    transferor_court = models.TextField()  # This field type is a guess.
    display = models.TextField()  # This field type is a guess.
    mediation = models.TextField()  # This field type is a guess.
    est_national_cd = models.CharField(max_length=6, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'establishments'


class EstcodeChange(models.Model):
    pk = models.CompositePrimaryKey('srcest_code', 'tarest_code')
    srcest_code = models.CharField(max_length=6)
    tarest_code = models.CharField(max_length=6)
    ipaddress = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    date_time = models.DateTimeField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'estcode_change'


class EtrialLowerCourt(models.Model):
    pk = models.CompositePrimaryKey('lower_trial', 'efilno')
    lower_court_code = models.SmallIntegerField(blank=True, null=True)
    lower_court = models.CharField(max_length=40, blank=True, null=True)
    lower_court_dec_dt = models.DateField(blank=True, null=True)
    lcc_applied_date = models.DateField(blank=True, null=True)
    lcc_received_date = models.DateField(blank=True, null=True)
    lower_cino = models.CharField(max_length=16, blank=True, null=True)
    lower_judge_name = models.CharField(max_length=100, blank=True, null=True)
    lower_dist_code = models.IntegerField(blank=True, null=True)
    lregis_date = models.DateField(blank=True, null=True)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    lowerjocode = models.CharField(max_length=150, blank=True, null=True)
    filing_case = models.IntegerField(blank=True, null=True)
    lower_taluka_code = models.IntegerField(blank=True, null=True)
    lower_state_id = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    qjnumber = models.CharField(max_length=255, blank=True, null=True)
    case_ref_no = models.CharField(max_length=15, blank=True, null=True)
    date_of_order = models.DateField(blank=True, null=True)
    ljudid = models.IntegerField(blank=True, null=True)
    judg_local_lang = models.TextField(blank=True, null=True)  # This field type is a guess.
    langflag = models.TextField(blank=True, null=True)  # This field type is a guess.
    oagainst = models.CharField(max_length=1, blank=True, null=True)
    lower_trial = models.TextField()  # This field type is a guess.
    sub_qj_high = models.TextField()  # This field type is a guess.
    efilno = models.CharField(max_length=20)
    efiling_year = models.IntegerField(blank=True, null=True)
    create_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'etrial_lower_court'


class EunderTrial(models.Model):
    pk = models.CompositePrimaryKey('srno', 'efilno')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    pet_res = models.CharField(max_length=99, blank=True, null=True)
    lpet_res = models.CharField(max_length=99, blank=True, null=True)
    arrest_date = models.DateField(blank=True, null=True)
    bail_date = models.DateField(blank=True, null=True)
    custody_type = models.CharField(max_length=1, blank=True, null=True)
    name1 = models.CharField(max_length=100, blank=True, null=True)
    lname1 = models.CharField(max_length=100, blank=True, null=True)
    amount1 = models.DecimalField(max_digits=17, decimal_places=2)
    property1 = models.CharField(max_length=255, blank=True, null=True)
    lproperty1 = models.CharField(max_length=250, blank=True, null=True)
    name2 = models.CharField(max_length=100, blank=True, null=True)
    lname2 = models.CharField(max_length=100, blank=True, null=True)
    amount2 = models.DecimalField(max_digits=17, decimal_places=2)
    property2 = models.CharField(max_length=255, blank=True, null=True)
    lproperty2 = models.CharField(max_length=250, blank=True, null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    prison_id = models.SmallIntegerField()
    landphone1 = models.CharField(max_length=15, blank=True, null=True)
    landphone2 = models.CharField(max_length=15, blank=True, null=True)
    age1 = models.SmallIntegerField()
    age2 = models.SmallIntegerField()
    mobile1 = models.CharField(max_length=15, blank=True, null=True)
    mobile2 = models.CharField(max_length=15, blank=True, null=True)
    address1 = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    street1 = models.CharField(max_length=100, blank=True, null=True)
    street2 = models.CharField(max_length=100, blank=True, null=True)
    pincode1 = models.IntegerField()
    pincode2 = models.IntegerField()
    dist_code1 = models.SmallIntegerField()
    dist_code2 = models.SmallIntegerField()
    taluka_code1 = models.SmallIntegerField()
    taluka_code2 = models.SmallIntegerField()
    hobli1 = models.IntegerField()
    hobli2 = models.IntegerField()
    hamlet1 = models.IntegerField()
    hamlet2 = models.BigIntegerField()
    village_code1 = models.IntegerField()
    village_code2 = models.IntegerField()
    town_code1 = models.IntegerField()
    town_code2 = models.BigIntegerField()
    ward_code1 = models.IntegerField()
    ward_code2 = models.IntegerField()
    father_name1 = models.CharField(max_length=100, blank=True, null=True)
    father_name2 = models.CharField(max_length=100, blank=True, null=True)
    org_name1 = models.CharField(max_length=100, blank=True, null=True)
    org_name2 = models.CharField(max_length=100, blank=True, null=True)
    uid1 = models.BigIntegerField()
    uid2 = models.BigIntegerField()
    release_date = models.DateField(blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.IntegerField()
    max_act_national_code = models.CharField(max_length=15, blank=True, null=True)
    max_section = models.CharField(max_length=100, blank=True, null=True)
    max_imprisonment = models.IntegerField(blank=True, null=True)
    life_death = models.CharField(max_length=1, blank=True, null=True)
    state_id1 = models.IntegerField(blank=True, null=True)
    state_id2 = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    efilno = models.CharField(max_length=99)
    efil_dt = models.DateField(blank=True, null=True)
    econfirm = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eunder_trial'


class EvictimT(models.Model):
    pk = models.CompositePrimaryKey('efilno', 'party_no')
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    lname = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    pet_age = models.SmallIntegerField()
    father_name = models.CharField(max_length=100, blank=True, null=True)
    lfather_name = models.CharField(max_length=100, blank=True, null=True)
    father_flag = models.CharField(max_length=2)
    pet_caste = models.SmallIntegerField(blank=True, null=True)
    type = models.SmallIntegerField()
    adv_name = models.CharField(max_length=100, blank=True, null=True)
    ladv_name = models.CharField(max_length=100, blank=True, null=True)
    adv_cd = models.BigIntegerField()
    pet_occu = models.CharField(max_length=30, blank=True, null=True)
    pet_nationality = models.CharField(max_length=99, blank=True, null=True)
    pet_email = models.CharField(max_length=254, blank=True, null=True)
    pet_mobile = models.CharField(max_length=15, blank=True, null=True)
    pet_phone = models.CharField(max_length=15, blank=True, null=True)
    pet_fax = models.CharField(max_length=15, blank=True, null=True)
    pet_sex = models.CharField(max_length=1, blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    passportno = models.CharField(max_length=25, blank=True, null=True)
    pincode = models.IntegerField(blank=True, null=True)
    country = models.CharField(max_length=99, blank=True, null=True)
    uid_no = models.BigIntegerField(blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    efil_dt = models.DateField()
    econfirm = models.CharField(max_length=1, blank=True, null=True)
    efilno = models.CharField(max_length=99)
    pet_gender = models.CharField(max_length=1, blank=True, null=True)
    create_on = models.DateTimeField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    party_no = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'evictim_t'


class EwitnessInfoT(models.Model):
    pk = models.CompositePrimaryKey('efilno', 'party_no', 'witness_no')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    witness_name = models.CharField(max_length=100, blank=True, null=True)
    witness_flag = models.SmallIntegerField()
    occupation = models.TextField(blank=True, null=True)
    lfather_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    witness_language = models.CharField(max_length=100, blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    date_of_examination = models.DateField(blank=True, null=True)
    age = models.SmallIntegerField()
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    father_name = models.CharField(max_length=100, blank=True, null=True)
    loccupation = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=254, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    father_flag = models.CharField(max_length=2)
    pincode = models.IntegerField(blank=True, null=True)
    uid_no = models.BigIntegerField(blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    econfirm = models.CharField(max_length=1, blank=True, null=True)
    efilno = models.CharField(max_length=99)
    efil_dt = models.DateField()
    create_on = models.DateTimeField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    witness_no = models.SmallIntegerField()
    party_no = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'ewitness_info_t'


class ExtraAdvT(models.Model):
    case_no = models.CharField(max_length=15, blank=True, null=True)
    pet_res = models.CharField(max_length=99, blank=True, null=True)
    lpet_res = models.CharField(max_length=99, blank=True, null=True)
    type = models.SmallIntegerField()
    adv_name = models.CharField(max_length=500, blank=True, null=True)
    ladv_name = models.CharField(max_length=100, blank=True, null=True)
    adv_code = models.BigIntegerField()
    party_no = models.SmallIntegerField()
    sr_no = models.SmallIntegerField(blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'extra_adv_t'


class ExtraactT(models.Model):
    pk = models.CompositePrimaryKey('serialno', 'cino')
    serialno = models.SmallIntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    acts = models.BigIntegerField()
    section = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    cino = models.CharField(max_length=16)
    party_no = models.SmallIntegerField()
    type = models.SmallIntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'extraact_t'


class ExtraactTA(models.Model):
    pk = models.CompositePrimaryKey('serialno', 'cino')
    serialno = models.SmallIntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    acts = models.BigIntegerField()
    section = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    cino = models.CharField(max_length=16)
    party_no = models.SmallIntegerField()
    type = models.SmallIntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'extraact_t_a'


class FeesT(models.Model):
    pk = models.CompositePrimaryKey('cino', 'todays_date', 'receipt_no', 'item_no')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    court_no = models.IntegerField()
    pet_res = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2)
    fees_type = models.SmallIntegerField(blank=True, null=True)
    document_type = models.SmallIntegerField()
    todays_date = models.DateField()
    display = models.TextField()  # This field type is a guess.
    filing = models.CharField(max_length=1, blank=True, null=True)
    type = models.SmallIntegerField()
    bank_code = models.CharField(max_length=15, blank=True, null=True)
    paymode = models.SmallIntegerField()
    dd_num = models.CharField(max_length=25, blank=True, null=True)
    dd_date = models.DateField(blank=True, null=True)
    receipt_no = models.IntegerField()
    casenotype = models.CharField(max_length=1, blank=True, null=True)
    receipt_status = models.CharField(max_length=1)
    item_no = models.SmallIntegerField()
    party_no = models.SmallIntegerField()
    cino = models.CharField(max_length=16)
    cause_list_type = models.IntegerField(blank=True, null=True)
    court_fee = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    aff_fee = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    vak_fee = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    other = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    ia_no = models.CharField(max_length=12, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fees_t'


class FeesTypeT(models.Model):
    fees_type = models.SmallIntegerField(primary_key=True)
    fees_name = models.CharField(max_length=100, blank=True, null=True)
    lfees_name = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    flag = models.CharField(max_length=1, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fees_type_t'


class FiirAccusedT(models.Model):
    pk = models.CompositePrimaryKey('accusedno', 'police_stn_code', 'fir_no', 'fir_year')
    accusedno = models.BigIntegerField()
    police_stn_code = models.BigIntegerField()
    fir_no = models.CharField(max_length=15)
    fir_year = models.SmallIntegerField()
    accusedname = models.CharField(max_length=100, blank=True, null=True)
    age = models.SmallIntegerField()
    sex = models.CharField(max_length=1, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    laccusedname = models.CharField(max_length=100, blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    charge = models.CharField(max_length=1, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    fir_type_code = models.SmallIntegerField()
    gender = models.CharField(max_length=1, blank=True, null=True)
    accusedname_salutation = models.SmallIntegerField(blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    crno = models.CharField(max_length=17, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    efilno = models.CharField(max_length=99, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fiir_accused_t'


class FiirAccusedTA(models.Model):
    pk = models.CompositePrimaryKey('accusedno', 'police_stn_code', 'fir_no', 'fir_year')
    accusedno = models.BigIntegerField()
    police_stn_code = models.BigIntegerField()
    fir_no = models.CharField(max_length=15)
    fir_year = models.SmallIntegerField()
    accusedname = models.CharField(max_length=100, blank=True, null=True)
    age = models.SmallIntegerField()
    sex = models.CharField(max_length=1, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    laccusedname = models.CharField(max_length=100, blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    charge = models.CharField(max_length=1, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    fir_type_code = models.SmallIntegerField()
    gender = models.CharField(max_length=1, blank=True, null=True)
    accusedname_salutation = models.SmallIntegerField(blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    crno = models.CharField(max_length=17, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    efilno = models.CharField(max_length=99, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fiir_accused_t_a'


class FiirAccusedTRejected(models.Model):
    pk = models.CompositePrimaryKey('accusedno', 'police_stn_code', 'fir_no', 'fir_year')
    accusedno = models.BigIntegerField()
    police_stn_code = models.BigIntegerField()
    fir_no = models.CharField(max_length=15)
    fir_year = models.SmallIntegerField()
    accusedname = models.CharField(max_length=100, blank=True, null=True)
    age = models.SmallIntegerField()
    sex = models.CharField(max_length=1, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    laccusedname = models.CharField(max_length=100, blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    charge = models.CharField(max_length=1, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    state_id = models.IntegerField(blank=True, null=True)
    fir_type_code = models.SmallIntegerField()
    accusedname_salutation = models.SmallIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    crno = models.CharField(max_length=17, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    efilno = models.CharField(max_length=99, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fiir_accused_t_rejected'


class FilingAllocation(models.Model):
    pk = models.CompositePrimaryKey('hearing_dt', 'cino')
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    court_no = models.IntegerField(blank=True, null=True)
    hearing_dt = models.DateField()
    order_passed = models.TextField(blank=True, null=True)
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'filing_allocation'


class FineNazaratT(models.Model):
    pk = models.CompositePrimaryKey('receipt_no', 'cino')
    case_no = models.CharField(max_length=15)
    date = models.DateField(blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)
    parties_names = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2)
    realized = models.CharField(max_length=1, blank=True, null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    balance = models.DecimalField(max_digits=17, decimal_places=2)
    paymode = models.CharField(max_length=1, blank=True, null=True)
    chdetails = models.CharField(max_length=255, blank=True, null=True)
    book_no = models.SmallIntegerField()
    serial_no = models.SmallIntegerField()
    receipt_no = models.SmallIntegerField()
    receivedby = models.CharField(max_length=255, blank=True, null=True)
    register_type = models.SmallIntegerField()
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fine_nazarat_t'


class FinePenaltyRegister(models.Model):
    pk = models.CompositePrimaryKey('deposit_sl_no', 'posting_date')
    deposit_sl_no = models.IntegerField()
    form_a_sl_no = models.IntegerField()
    form_a_order_no = models.SmallIntegerField()
    form_a_order_type = models.SmallIntegerField()
    form_a_order_date = models.DateField(blank=True, null=True)
    form_a_case_no = models.CharField(max_length=15, blank=True, null=True)
    form_a_pet_res_name = models.CharField(max_length=255, blank=True, null=True)
    form_a_pet_res_id = models.SmallIntegerField()
    form_a_pet_res_type = models.CharField(max_length=1, blank=True, null=True)
    form_a_address = models.TextField(blank=True, null=True)
    form_a_repr_name = models.CharField(max_length=100, blank=True, null=True)
    form_a_subject = models.CharField(max_length=255, blank=True, null=True)
    form_a_amount = models.DecimalField(max_digits=17, decimal_places=2)
    form_a_paymode = models.CharField(max_length=1, blank=True, null=True)
    form_a_receipt_date = models.DateField(blank=True, null=True)
    form_a_book_no = models.SmallIntegerField()
    form_a_serial_no = models.SmallIntegerField()
    form_a_receipt_type = models.SmallIntegerField()
    form_a_receipt_no = models.IntegerField()
    deposit_received_by = models.CharField(max_length=99, blank=True, null=True)
    form_a_ch_real_date = models.DateField(blank=True, null=True)
    form_a_ro_no = models.IntegerField()
    form_a_account_purpose = models.SmallIntegerField()
    register_type = models.SmallIntegerField()
    posting_date = models.DateField()
    deposit_reg_no = models.IntegerField()
    nazart_order_punishment = models.DecimalField(max_digits=17, decimal_places=2)
    nazarat_punishment_section = models.CharField(max_length=255, blank=True, null=True)
    write_off_fine = models.TextField()  # This field type is a guess.
    write_off_date = models.DateField(blank=True, null=True)
    write_off_reason = models.CharField(max_length=255, blank=True, null=True)
    write_off_amount = models.DecimalField(max_digits=17, decimal_places=2)
    payment_reg_no = models.CharField(max_length=255, blank=True, null=True)
    cancel_entry = models.TextField()  # This field type is a guess.
    date_time = models.DateTimeField()
    lpet_res_name = models.CharField(max_length=100, blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    lrepr_name = models.CharField(max_length=100, blank=True, null=True)
    lsubject = models.CharField(max_length=255, blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fine_penalty_register'


class FirAccusedActs(models.Model):
    pk = models.CompositePrimaryKey('serialno', 'crno')
    serialno = models.SmallIntegerField()
    crno = models.CharField(max_length=17)
    police_stn_code = models.IntegerField()
    fir_no = models.CharField(max_length=15, blank=True, null=True)
    fir_year = models.SmallIntegerField()
    fir_type_code = models.SmallIntegerField()
    acts = models.BigIntegerField()
    section = models.CharField(max_length=100, blank=True, null=True)
    party_no = models.SmallIntegerField()
    type = models.SmallIntegerField()
    fir_date = models.DateField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    efilno = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fir_accused_acts'


class FirAccusedActsA(models.Model):
    pk = models.CompositePrimaryKey('serialno', 'crno')
    serialno = models.SmallIntegerField()
    crno = models.CharField(max_length=17)
    police_stn_code = models.IntegerField()
    fir_no = models.CharField(max_length=15, blank=True, null=True)
    fir_year = models.SmallIntegerField()
    fir_type_code = models.SmallIntegerField()
    acts = models.BigIntegerField()
    section = models.CharField(max_length=100, blank=True, null=True)
    party_no = models.SmallIntegerField()
    type = models.SmallIntegerField()
    fir_date = models.DateField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    efilno = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fir_accused_acts_a'


class FirSummaryT(models.Model):
    fir_summary_id = models.SmallIntegerField(primary_key=True)
    fir_summary = models.CharField(max_length=100, blank=True, null=True)
    lfir_summary = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fir_summary_t'


class FirTypeT(models.Model):
    fir_type_code = models.SmallIntegerField(primary_key=True)
    fir_type_name = models.CharField(max_length=100, blank=True, null=True)
    lfir_type_name = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fir_type_t'


class FirextraactT(models.Model):
    pk = models.CompositePrimaryKey('serialno', 'crno', 'acts')
    serialno = models.SmallIntegerField()
    crno = models.CharField(max_length=17)
    police_stn_code = models.IntegerField()
    fir_no = models.CharField(max_length=15)
    fir_year = models.SmallIntegerField()
    acts = models.BigIntegerField()
    section = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    efilno = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'firextraact_t'


class FirextraactTA(models.Model):
    pk = models.CompositePrimaryKey('serialno', 'crno', 'acts')
    serialno = models.SmallIntegerField()
    crno = models.CharField(max_length=17)
    police_stn_code = models.IntegerField()
    fir_no = models.CharField(max_length=15)
    fir_year = models.SmallIntegerField()
    acts = models.BigIntegerField()
    section = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    efilno = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'firextraact_t_a'


class FirextraactTRejected(models.Model):
    pk = models.CompositePrimaryKey('serialno', 'crno', 'acts')
    serialno = models.SmallIntegerField()
    crno = models.CharField(max_length=17)
    police_stn_code = models.IntegerField()
    fir_no = models.CharField(max_length=15)
    fir_year = models.SmallIntegerField()
    acts = models.BigIntegerField()
    section = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    efilno = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'firextraact_t_rejected'


class FormFieldsT(models.Model):
    pk = models.CompositePrimaryKey('link_id', 'form_field_id', 'tab_id')
    formfieldid = models.CharField(max_length=50, blank=True, null=True)
    form_field_name = models.CharField(max_length=100, blank=True, null=True)
    bilingual = models.CharField(blank=True, null=True)
    link_id = models.IntegerField()
    form_field_mandatory = models.CharField()
    table_field_name = models.CharField(max_length=255, blank=True, null=True)
    form_field_length = models.IntegerField()
    tab_id = models.IntegerField()
    form_label = models.CharField(max_length=100, blank=True, null=True)
    form_label_desc = models.TextField(blank=True, null=True)
    html_type = models.IntegerField(blank=True, null=True)
    form_field_id = models.IntegerField()
    form_field_type = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'form_fields_t'


class FormaNazaratT(models.Model):
    pk = models.CompositePrimaryKey('sl_no', 'receipt_date')
    sl_no = models.IntegerField()
    order_no = models.SmallIntegerField()
    order_date = models.DateField(blank=True, null=True)
    order_type = models.SmallIntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    pet_res_name = models.CharField(max_length=255, blank=True, null=True)
    pet_res_id = models.SmallIntegerField()
    pet_res_type = models.CharField(max_length=1, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    repr_name = models.CharField(max_length=255, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2)
    paymode = models.CharField(max_length=1, blank=True, null=True)
    cheque_details = models.CharField(max_length=255, blank=True, null=True)
    receipt_date = models.DateField()
    book_no = models.SmallIntegerField()
    serial_no = models.IntegerField(blank=True, null=True)
    receipt_type = models.SmallIntegerField()
    receipt_no = models.IntegerField()
    received_by = models.CharField(max_length=255, blank=True, null=True)
    posting = models.CharField(max_length=1, blank=True, null=True)
    ch_real_date = models.DateField(blank=True, null=True)
    register_type = models.SmallIntegerField()
    bank_code = models.CharField(max_length=15, blank=True, null=True)
    dd_chk_date = models.DateField(blank=True, null=True)
    ro_no = models.IntegerField()
    account_purpose = models.SmallIntegerField()
    cancel_receipt_ro = models.TextField()  # This field type is a guess.
    cancel_date = models.DateField(blank=True, null=True)
    cancel_reason = models.CharField(max_length=255, blank=True, null=True)
    cheque_not_realized = models.TextField()  # This field type is a guess.
    date_time_stamp = models.DateTimeField()
    otherpurpose = models.SmallIntegerField()
    remarks = models.CharField(max_length=255, blank=True, null=True)
    branchname = models.CharField(max_length=250, blank=True, null=True)
    lapse = models.TextField()  # This field type is a guess.
    lapse_date = models.DateField(blank=True, null=True)
    lapse_ro = models.CharField(max_length=5, blank=True, null=True)
    old_ro_date = models.DateField(blank=True, null=True)
    lpet_res_name = models.CharField(max_length=100, blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    lrepr_name = models.CharField(max_length=100, blank=True, null=True)
    lsubject = models.CharField(max_length=255, blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    transid1 = models.CharField(max_length=30, blank=True, null=True)
    transid2 = models.CharField(max_length=30, blank=True, null=True)
    transid3 = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'forma_nazarat_t'


class GjAssessmentCriteria(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    inst_code = models.CharField(max_length=10, blank=True, null=True)
    cr_dispsrno = models.CharField(max_length=3, blank=True, null=True)
    cr_name = models.CharField(max_length=250, blank=True, null=True)
    report = models.CharField(max_length=5, blank=True, null=True)
    casetype = models.CharField(max_length=50, blank=True, null=True)
    case_subtype = models.CharField(max_length=50, blank=True, null=True)
    disposaltype = models.CharField(max_length=50, blank=True, null=True)
    ex_disposaltype = models.CharField(max_length=50, blank=True, null=True)
    sentence_code = models.SmallIntegerField(blank=True, null=True)
    classification_codes = models.CharField(max_length=150, blank=True, null=True)
    suit_value = models.CharField(max_length=10, blank=True, null=True)
    cr_weightage = models.CharField(max_length=5, blank=True, null=True)
    ex_classification_codes = models.CharField(max_length=150, blank=True, null=True)
    ccode_i_l = models.CharField(max_length=10, blank=True, null=True)
    ismain = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gj_assessment_criteria'


class GjCadreDesignationT(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    edesc = models.CharField(max_length=60, blank=True, null=True)
    gdesc = models.CharField(max_length=60, blank=True, null=True)
    cadreid = models.IntegerField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    lastupdatedby = models.CharField(max_length=40, blank=True, null=True)
    lastupdatedtime = models.DateTimeField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gj_cadre_designation_t'


class GjCadreT(models.Model):
    id = models.BigIntegerField(primary_key=True)
    cader = models.CharField(max_length=50, blank=True, null=True)
    datecreated = models.DateField()
    usercreated = models.CharField(max_length=30)
    parent = models.BigIntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gj_cadre_t'


class GjJudgeCodeT(models.Model):
    code = models.CharField(primary_key=True, max_length=10)
    title = models.CharField(max_length=7)
    fname = models.CharField(max_length=50)
    mname = models.CharField(max_length=50, blank=True, null=True)
    lname = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=50)
    dob = models.DateField(blank=True, null=True)
    doj = models.DateField(blank=True, null=True)
    doct = models.DateField(blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    lastupdatedby = models.CharField(max_length=40)
    lastupdatedtime = models.DateTimeField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gj_judge_code_t'


class GjReporttypeT(models.Model):
    pk = models.CompositePrimaryKey('esttype', 'reportlabel', 'reportvalue')
    esttype = models.CharField(max_length=15)
    reportlabel = models.CharField(max_length=100)
    reportvalue = models.CharField(max_length=25)
    formname = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=6, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gj_reporttype_t'


class GuardianInfo(models.Model):
    pk = models.CompositePrimaryKey('guardian_name', 'guardian_type', 'extraparty_no', 'guardian_flag', 'cino')
    guardian_name = models.CharField(max_length=100)
    guardian_age = models.SmallIntegerField()
    guardian_type = models.CharField(max_length=1)
    guardian_nationality = models.CharField(max_length=99, blank=True, null=True)
    guardian_email = models.CharField(max_length=254, blank=True, null=True)
    guardian_mobile = models.CharField(max_length=15, blank=True, null=True)
    guardian_display = models.TextField()  # This field type is a guess.
    guardian_add1 = models.TextField(blank=True, null=True)
    guardian_add2 = models.TextField(blank=True, null=True)
    lguardian_name = models.CharField(max_length=100, blank=True, null=True)
    guardian_flag = models.CharField(max_length=2)
    extraparty_no = models.SmallIntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    guardian_gender = models.CharField(max_length=1, blank=True, null=True)
    police_st_code = models.SmallIntegerField()
    lguardian_add1 = models.TextField(blank=True, null=True)
    lguardian_add2 = models.TextField(blank=True, null=True)
    cino = models.CharField(max_length=16)
    guardian_salutation = models.SmallIntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'guardian_info'


class HearingStatusT(models.Model):
    case_no = models.CharField(max_length=15, blank=True, null=True)
    hearing_date = models.DateField(blank=True, null=True)
    hearing_start = models.CharField(max_length=15, blank=True, null=True)
    hearing_end = models.CharField(max_length=15, blank=True, null=True)
    called_start = models.CharField(max_length=15, blank=True, null=True)
    court_no = models.IntegerField()
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    cause_list_type = models.IntegerField()
    cause_list_sr_no = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    ia_no = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hearing_status_t'


class HearingStatusTA(models.Model):
    case_no = models.CharField(max_length=15, blank=True, null=True)
    hearing_date = models.DateField(blank=True, null=True)
    hearing_start = models.CharField(max_length=15, blank=True, null=True)
    hearing_end = models.CharField(max_length=15, blank=True, null=True)
    called_start = models.CharField(max_length=15, blank=True, null=True)
    court_no = models.IntegerField()
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    cause_list_type = models.IntegerField()
    cause_list_sr_no = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    ia_no = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hearing_status_t_a'


class HelpForm(models.Model):
    pk = models.CompositePrimaryKey('form_id', 'label_id')
    form_id = models.SmallIntegerField()
    label_id = models.SmallIntegerField()
    field_name = models.TextField(blank=True, null=True)
    field_type = models.CharField(max_length=15, blank=True, null=True)
    field_size = models.SmallIntegerField()
    label_desc = models.CharField(max_length=300, blank=True, null=True)
    l_label_desc = models.CharField(max_length=300, blank=True, null=True)
    table_name = models.CharField(max_length=15, blank=True, null=True)
    mandatory_field = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'help_form'


class HelpT(models.Model):
    pk = models.CompositePrimaryKey('link_id', 'tab_id')
    link_id = models.IntegerField()
    tab_id = models.IntegerField()
    form_desc = models.TextField(blank=True, null=True)
    l_form_desc = models.TextField(blank=True, null=True)
    gen_desc = models.TextField(blank=True, null=True)
    l_gen_desc = models.TextField(blank=True, null=True)
    legal_desc = models.TextField(blank=True, null=True)
    l_legal_desc = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    l_note = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'help_t'


class HolidayT(models.Model):
    pk = models.CompositePrimaryKey('holidaycode', 'holidayid')
    holidaycode = models.SmallIntegerField()
    holidayid = models.SmallIntegerField()
    holidaydate = models.DateField(blank=True, null=True)
    holidayname = models.TextField(blank=True, null=True)
    lholidayname = models.TextField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    sat_sun = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'holiday_t'


class IaCaseTypeT(models.Model):
    ia_case_type = models.SmallIntegerField(primary_key=True)
    ia_type_name = models.CharField(max_length=50, blank=True, null=True)
    ia_ltype_name = models.CharField(max_length=50, blank=True, null=True)
    ia_full_form = models.CharField(max_length=100, blank=True, null=True)
    ia_lfull_form = models.CharField(max_length=100, blank=True, null=True)
    ia_filing_no = models.IntegerField()
    ia_filing_year = models.SmallIntegerField()
    ia_reg_no = models.IntegerField()
    ia_reg_year = models.SmallIntegerField()
    display = models.TextField()  # This field type is a guess.
    national_code = models.BigIntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ia_case_type_t'


class IaExtraAdvT(models.Model):
    case_no = models.CharField(max_length=15, blank=True, null=True)
    ia_no = models.CharField(max_length=12, blank=True, null=True)
    pet_res = models.CharField(max_length=99, blank=True, null=True)
    lpet_res = models.CharField(max_length=99, blank=True, null=True)
    type = models.SmallIntegerField()
    adv_name = models.CharField(max_length=500, blank=True, null=True)
    ladv_name = models.CharField(max_length=100, blank=True, null=True)
    adv_code = models.BigIntegerField()
    party_no = models.SmallIntegerField()
    sr_no = models.SmallIntegerField(blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    ia_case_type = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    efilno = models.CharField(max_length=20, blank=True, null=True)
    efilia_no = models.CharField(max_length=20, blank=True, null=True)
    efildt = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ia_extra_adv_t'


class IaFiling(models.Model):
    pk = models.CompositePrimaryKey('ia_no', 'cino', 'ia_case_type')
    court_no = models.IntegerField()
    case_fr = models.SmallIntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    ia_no = models.CharField(max_length=12)
    ia_registrationo = models.CharField(max_length=12, blank=True, null=True)
    party_applying = models.CharField(max_length=10, blank=True, null=True)
    party_applying_code = models.TextField(blank=True, null=True)
    appotherparty = models.CharField(max_length=99, blank=True, null=True)
    appotheradv = models.CharField(max_length=99, blank=True, null=True)
    against_whom = models.CharField(max_length=10, blank=True, null=True)
    against_whom_code = models.TextField(blank=True, null=True)
    againotherparty = models.CharField(max_length=99, blank=True, null=True)
    againotheradv = models.CharField(max_length=99, blank=True, null=True)
    purpose_code = models.BigIntegerField()
    relief_offense = models.TextField(blank=True, null=True)
    date_of_ia_filing = models.DateField(blank=True, null=True)
    date_of_ia_registration = models.DateField(blank=True, null=True)
    date_of_serving_notice = models.DateField(blank=True, null=True)
    date_of_hearing = models.DateField(blank=True, null=True)
    date_of_order = models.DateField(blank=True, null=True)
    disposal_date = models.DateField(blank=True, null=True)
    disp_nature = models.IntegerField()
    order_code = models.SmallIntegerField()
    court_fee = models.IntegerField()
    act_code = models.IntegerField()
    under_sec = models.CharField(max_length=100, blank=True, null=True)
    unit = models.DecimalField(max_digits=17, decimal_places=2)
    goshwara_no = models.SmallIntegerField()
    order_remark = models.TextField(blank=True, null=True)
    exhibit = models.TextField(blank=True, null=True)
    dt_of_entry = models.DateTimeField()
    objcompl_date = models.DateField(blank=True, null=True)
    obj_flag = models.CharField(max_length=1, blank=True, null=True)
    objreceipt_dt = models.DateField(blank=True, null=True)
    objreturn_dt = models.DateField(blank=True, null=True)
    objprepare_dt = models.DateField(blank=True, null=True)
    objection = models.CharField(max_length=500, blank=True, null=True)
    objdescription = models.TextField(blank=True, null=True)
    lobjection = models.CharField(max_length=500, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    date_filing_disp = models.DateField(blank=True, null=True)
    reason_for_rej = models.TextField(blank=True, null=True)
    lreason_for_rej = models.TextField(blank=True, null=True)
    date_of_decision_o = models.DateField(blank=True, null=True)
    date_of_revoke = models.DateField(blank=True, null=True)
    unit_type = models.SmallIntegerField()
    nature_cd = models.SmallIntegerField()
    ia_filno = models.IntegerField(blank=True, null=True)
    ia_filyear = models.SmallIntegerField(blank=True, null=True)
    ia_regno = models.IntegerField(blank=True, null=True)
    ia_regyear = models.SmallIntegerField(blank=True, null=True)
    filcasetype = models.SmallIntegerField(blank=True, null=True)
    fil_no = models.IntegerField(blank=True, null=True)
    fil_year = models.SmallIntegerField(blank=True, null=True)
    regcasetype = models.SmallIntegerField(blank=True, null=True)
    reg_no = models.IntegerField(blank=True, null=True)
    reg_year = models.SmallIntegerField(blank=True, null=True)
    app_extra_adv = models.TextField(blank=True, null=True)
    again_extra_adv = models.TextField(blank=True, null=True)
    subpurpose_code = models.IntegerField()
    oldiafiling_no = models.CharField(max_length=15, blank=True, null=True)
    old_ia_no = models.CharField(max_length=16, blank=True, null=True)
    old_ia_registrationo = models.CharField(max_length=16, blank=True, null=True)
    cino = models.CharField(max_length=16)
    indispose = models.CharField(max_length=1, blank=True, null=True)
    jocode = models.CharField(max_length=150, blank=True, null=True)
    desig_code = models.CharField(max_length=50, blank=True, null=True)
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    case_remark = models.TextField(blank=True, null=True)
    dangling_ia_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    appotheradv_code = models.BigIntegerField(blank=True, null=True)
    againotheradv_code = models.BigIntegerField(blank=True, null=True)
    app_extra_adv_code = models.CharField(max_length=250, blank=True, null=True)
    again_extra_adv_code = models.CharField(max_length=250, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    afidvt = models.IntegerField(blank=True, null=True)
    revoke_remark = models.TextField(blank=True, null=True)
    no_of_leaves = models.IntegerField(blank=True, null=True)
    ia_case_type = models.IntegerField()
    lorder_remark = models.TextField(blank=True, null=True)
    lexhibit = models.TextField(blank=True, null=True)
    short_order = models.CharField(max_length=50, blank=True, null=True)
    efilno = models.CharField(max_length=20, blank=True, null=True)
    efilia_no = models.CharField(max_length=20, blank=True, null=True)
    part_heard = models.CharField(max_length=50, blank=True, null=True)
    not_before = models.CharField(max_length=50, blank=True, null=True)
    dormant_sinedie = models.CharField(max_length=1, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    adjcode = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'ia_filing'


class IaFilingA(models.Model):
    pk = models.CompositePrimaryKey('ia_no', 'cino', 'ia_case_type')
    court_no = models.IntegerField()
    case_fr = models.SmallIntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    ia_no = models.CharField(max_length=12)
    ia_registrationo = models.CharField(max_length=12, blank=True, null=True)
    party_applying = models.CharField(max_length=10, blank=True, null=True)
    party_applying_code = models.TextField(blank=True, null=True)
    appotherparty = models.CharField(max_length=99, blank=True, null=True)
    appotheradv = models.CharField(max_length=99, blank=True, null=True)
    against_whom = models.CharField(max_length=10, blank=True, null=True)
    against_whom_code = models.TextField(blank=True, null=True)
    againotherparty = models.CharField(max_length=99, blank=True, null=True)
    againotheradv = models.CharField(max_length=99, blank=True, null=True)
    purpose_code = models.BigIntegerField()
    relief_offense = models.TextField(blank=True, null=True)
    date_of_ia_filing = models.DateField(blank=True, null=True)
    date_of_ia_registration = models.DateField(blank=True, null=True)
    date_of_serving_notice = models.DateField(blank=True, null=True)
    date_of_hearing = models.DateField(blank=True, null=True)
    date_of_order = models.DateField(blank=True, null=True)
    disposal_date = models.DateField(blank=True, null=True)
    disp_nature = models.IntegerField()
    order_code = models.SmallIntegerField()
    court_fee = models.IntegerField()
    act_code = models.IntegerField()
    under_sec = models.CharField(max_length=100, blank=True, null=True)
    unit = models.DecimalField(max_digits=17, decimal_places=2)
    goshwara_no = models.SmallIntegerField()
    order_remark = models.TextField(blank=True, null=True)
    exhibit = models.TextField(blank=True, null=True)
    dt_of_entry = models.DateTimeField()
    objcompl_date = models.DateField(blank=True, null=True)
    obj_flag = models.CharField(max_length=1, blank=True, null=True)
    objreceipt_dt = models.DateField(blank=True, null=True)
    objreturn_dt = models.DateField(blank=True, null=True)
    objprepare_dt = models.DateField(blank=True, null=True)
    objection = models.CharField(max_length=500, blank=True, null=True)
    objdescription = models.TextField(blank=True, null=True)
    lobjection = models.CharField(max_length=500, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    date_filing_disp = models.DateField(blank=True, null=True)
    reason_for_rej = models.TextField(blank=True, null=True)
    lreason_for_rej = models.TextField(blank=True, null=True)
    date_of_decision_o = models.DateField(blank=True, null=True)
    date_of_revoke = models.DateField(blank=True, null=True)
    unit_type = models.SmallIntegerField()
    nature_cd = models.SmallIntegerField()
    ia_filno = models.IntegerField(blank=True, null=True)
    ia_filyear = models.SmallIntegerField(blank=True, null=True)
    ia_regno = models.IntegerField(blank=True, null=True)
    ia_regyear = models.SmallIntegerField(blank=True, null=True)
    filcasetype = models.SmallIntegerField(blank=True, null=True)
    fil_no = models.IntegerField(blank=True, null=True)
    fil_year = models.SmallIntegerField(blank=True, null=True)
    regcasetype = models.SmallIntegerField(blank=True, null=True)
    reg_no = models.IntegerField(blank=True, null=True)
    reg_year = models.SmallIntegerField(blank=True, null=True)
    app_extra_adv = models.TextField(blank=True, null=True)
    again_extra_adv = models.TextField(blank=True, null=True)
    subpurpose_code = models.IntegerField()
    oldiafiling_no = models.CharField(max_length=15, blank=True, null=True)
    old_ia_no = models.CharField(max_length=16, blank=True, null=True)
    old_ia_registrationo = models.CharField(max_length=16, blank=True, null=True)
    cino = models.CharField(max_length=16)
    indispose = models.CharField(max_length=1, blank=True, null=True)
    jocode = models.CharField(max_length=150, blank=True, null=True)
    desig_code = models.CharField(max_length=50, blank=True, null=True)
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    case_remark = models.TextField(blank=True, null=True)
    dangling_ia_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    appotheradv_code = models.BigIntegerField(blank=True, null=True)
    againotheradv_code = models.BigIntegerField(blank=True, null=True)
    app_extra_adv_code = models.CharField(max_length=250, blank=True, null=True)
    again_extra_adv_code = models.CharField(max_length=250, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    afidvt = models.IntegerField(blank=True, null=True)
    revoke_remark = models.TextField(blank=True, null=True)
    no_of_leaves = models.IntegerField(blank=True, null=True)
    ia_case_type = models.IntegerField()
    lorder_remark = models.TextField(blank=True, null=True)
    lexhibit = models.TextField(blank=True, null=True)
    short_order = models.CharField(max_length=50, blank=True, null=True)
    efilno = models.CharField(max_length=20, blank=True, null=True)
    efilia_no = models.CharField(max_length=20, blank=True, null=True)
    part_heard = models.CharField(max_length=50, blank=True, null=True)
    not_before = models.CharField(max_length=50, blank=True, null=True)
    dormant_sinedie = models.CharField(max_length=1, blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    adjcode = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'ia_filing_a'


class IaNature(models.Model):
    iacls_code = models.SmallIntegerField(primary_key=True)
    iacls_name = models.CharField(max_length=100, blank=True, null=True)
    liacls_name = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    national_code = models.BigIntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'ia_nature'


class IaOtherParty(models.Model):
    pk = models.CompositePrimaryKey('cino', 'ia_no', 'party_no')
    party_no = models.SmallIntegerField()
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    lname = models.CharField(max_length=100, blank=True, null=True)
    pet_age = models.SmallIntegerField()
    type = models.SmallIntegerField()
    adv_name = models.CharField(max_length=100, blank=True, null=True)
    ladv_name = models.CharField(max_length=100, blank=True, null=True)
    adv_cd = models.BigIntegerField()
    display = models.TextField()  # This field type is a guess.
    pet_sex = models.CharField(max_length=1, blank=True, null=True)
    party_id = models.TextField(blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    cino = models.CharField(max_length=16)
    pet_gender = models.CharField(max_length=1, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    ia_no = models.CharField(max_length=12)
    ia_case_type = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    efilno = models.CharField(max_length=20, blank=True, null=True)
    efilia_no = models.CharField(max_length=20, blank=True, null=True)
    efildt = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ia_other_party'


class IaOtherPartyA(models.Model):
    pk = models.CompositePrimaryKey('cino', 'ia_no', 'party_no')
    party_no = models.SmallIntegerField()
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    lname = models.CharField(max_length=100, blank=True, null=True)
    pet_age = models.SmallIntegerField()
    type = models.SmallIntegerField()
    adv_name = models.CharField(max_length=100, blank=True, null=True)
    ladv_name = models.CharField(max_length=100, blank=True, null=True)
    adv_cd = models.BigIntegerField()
    display = models.TextField()  # This field type is a guess.
    pet_sex = models.CharField(max_length=1, blank=True, null=True)
    party_id = models.TextField(blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    cino = models.CharField(max_length=16)
    pet_gender = models.CharField(max_length=1, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    ia_no = models.CharField(max_length=12)
    ia_case_type = models.IntegerField(blank=True, null=True)
    efilno = models.CharField(max_length=20, blank=True, null=True)
    efilia_no = models.CharField(max_length=20, blank=True, null=True)
    efildt = models.DateField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ia_other_party_a'


class IaProceeding(models.Model):
    pk = models.CompositePrimaryKey('cino', 'ia_filing_no', 'srno')
    court_no = models.IntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    ia_no = models.CharField(max_length=12, blank=True, null=True)
    ia_filing_no = models.CharField(max_length=12)
    next_date = models.DateField()
    todays_date = models.DateField(blank=True, null=True)
    purpose_code = models.SmallIntegerField()
    order_remark = models.TextField(blank=True, null=True)
    exhibit = models.TextField(blank=True, null=True)
    subpurpose_code = models.IntegerField()
    lorder_remark = models.TextField(blank=True, null=True)
    lexhibit = models.TextField(blank=True, null=True)
    old_ia_no = models.CharField(max_length=12, blank=True, null=True)
    old_ia_filing_no = models.CharField(max_length=12, blank=True, null=True)
    cino = models.CharField(max_length=16)
    jocode = models.CharField(max_length=150, blank=True, null=True)
    desig_code = models.CharField(max_length=50, blank=True, null=True)
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    case_remark = models.TextField(blank=True, null=True)
    takenonboard = models.CharField(max_length=2, blank=True, null=True)
    old_next_date = models.DateField(blank=True, null=True)
    old_purpose_code = models.SmallIntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    oldbenchid = models.IntegerField(blank=True, null=True)
    srno = models.IntegerField()
    ia_case_type = models.IntegerField(blank=True, null=True)
    adjcode = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'ia_proceeding'
        unique_together = (('cino', 'ia_filing_no', 'next_date', 'todays_date', 'ia_case_type'),)


class IaProceedingA(models.Model):
    pk = models.CompositePrimaryKey('cino', 'ia_filing_no', 'srno')
    court_no = models.IntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    ia_no = models.CharField(max_length=12, blank=True, null=True)
    ia_filing_no = models.CharField(max_length=12)
    next_date = models.DateField()
    todays_date = models.DateField(blank=True, null=True)
    purpose_code = models.SmallIntegerField()
    order_remark = models.TextField(blank=True, null=True)
    exhibit = models.TextField(blank=True, null=True)
    subpurpose_code = models.IntegerField()
    lorder_remark = models.TextField(blank=True, null=True)
    lexhibit = models.TextField(blank=True, null=True)
    old_ia_no = models.CharField(max_length=12, blank=True, null=True)
    old_ia_filing_no = models.CharField(max_length=12, blank=True, null=True)
    cino = models.CharField(max_length=16)
    jocode = models.CharField(max_length=150, blank=True, null=True)
    desig_code = models.CharField(max_length=50, blank=True, null=True)
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    case_remark = models.TextField(blank=True, null=True)
    takenonboard = models.CharField(max_length=2, blank=True, null=True)
    old_next_date = models.DateField(blank=True, null=True)
    old_purpose_code = models.SmallIntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    oldbenchid = models.IntegerField(blank=True, null=True)
    srno = models.IntegerField()
    ia_case_type = models.IntegerField(blank=True, null=True)
    adjcode = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'ia_proceeding_a'
        unique_together = (('cino', 'ia_filing_no', 'next_date', 'todays_date', 'ia_case_type'),)


class IaobjectionHistory(models.Model):
    pk = models.CompositePrimaryKey('cino', 'ia_no', 'srno')
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    ia_no = models.CharField(max_length=12)
    objection = models.TextField(blank=True, null=True)
    objdescription = models.TextField(blank=True, null=True)
    lobjection = models.TextField(blank=True, null=True)
    obj_redate = models.DateField(blank=True, null=True)
    objreturn_dt = models.DateField(blank=True, null=True)
    objreceipt_dt = models.DateField(blank=True, null=True)
    objprepare_dt = models.DateField()
    cino = models.CharField(max_length=16)
    srno = models.IntegerField()
    ia_case_type = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'iaobjection_history'


class Icourtfee(models.Model):
    pk = models.CompositePrimaryKey('grn', 'cino')
    caseno = models.CharField(max_length=15, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    grn = models.CharField(max_length=18)
    amount = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    userid = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    officecode = models.CharField(max_length=6, blank=True, null=True)
    actioncode = models.CharField(max_length=100, blank=True, null=True)
    remark = models.CharField(max_length=100, blank=True, null=True)
    verificationno = models.CharField(max_length=16, blank=True, null=True)
    retstr_beforedeface = models.CharField(max_length=2000, blank=True, null=True)
    entry_dt = models.DateTimeField()
    defacenumber = models.CharField(max_length=16, blank=True, null=True)
    defacereqsent = models.TextField()  # This field type is a guess.
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    efiling_id = models.IntegerField(blank=True, null=True)
    efiling_no = models.CharField(max_length=20, blank=True, null=True)
    efiling_year = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'icourtfee'


class ImmovableSuit(models.Model):
    pk = models.CompositePrimaryKey('item_no', 'movable_flag', 'cino')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    item_no = models.SmallIntegerField()
    type = models.SmallIntegerField()
    property_name = models.CharField(max_length=255, blank=True, null=True)
    district_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    hobli_code = models.IntegerField()
    village_code = models.IntegerField()
    hamlet_code = models.IntegerField()
    house_site_survey = models.CharField(max_length=255, blank=True, null=True)
    door_sy_rs = models.CharField(max_length=255, blank=True, null=True)
    ward_no = models.CharField(max_length=255, blank=True, null=True)
    layout_subhissa = models.CharField(max_length=255, blank=True, null=True)
    stage_sub_sub_hissa = models.CharField(max_length=255, blank=True, null=True)
    main = models.CharField(max_length=255, blank=True, null=True)
    cross_type = models.CharField(max_length=255, blank=True, null=True)
    road = models.CharField(max_length=255, blank=True, null=True)
    loc_area = models.CharField(max_length=255, blank=True, null=True)
    area = models.TextField(blank=True, null=True)
    measuree_w = models.CharField(max_length=255, blank=True, null=True)
    measuren_s = models.CharField(max_length=255, blank=True, null=True)
    other_measure = models.CharField(max_length=255, blank=True, null=True)
    east_by = models.CharField(max_length=255, blank=True, null=True)
    west_by = models.CharField(max_length=255, blank=True, null=True)
    north_by = models.CharField(max_length=255, blank=True, null=True)
    south_by = models.CharField(max_length=255, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    suit_schedule = models.SmallIntegerField()
    movable_property = models.TextField(blank=True, null=True)
    movable_flag = models.TextField()  # This field type is a guess.
    cino = models.CharField(max_length=16)
    state_id = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'immovable_suit'


class IndexRegister(models.Model):
    pk = models.CompositePrimaryKey('srno', 'cino')
    caseno = models.CharField(max_length=15, blank=True, null=True)
    srno = models.BigIntegerField()
    description = models.CharField(max_length=150, blank=True, null=True)
    paperdate = models.DateField(blank=True, null=True)
    noofparts = models.CharField(max_length=5, blank=True, null=True)
    alphabetical = models.CharField(max_length=150, blank=True, null=True)
    remarks = models.CharField(max_length=100, blank=True, null=True)
    lalphabetical = models.CharField(max_length=150, blank=True, null=True)
    lremarks = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    upload_date = models.DateTimeField(blank=True, null=True)
    cino = models.CharField(max_length=16)
    doc_year = models.IntegerField(blank=True, null=True)
    doc_no = models.IntegerField(blank=True, null=True)
    filing_no = models.CharField(max_length=16, blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    type = models.TextField(blank=True, null=True)  # This field type is a guess.
    party_no = models.IntegerField()
    adv_name = models.CharField(max_length=100, blank=True, null=True)
    adv_cd = models.IntegerField(blank=True, null=True)
    extra_party = models.CharField(max_length=250, blank=True, null=True)
    objection = models.TextField(blank=True, null=True)  # This field type is a guess.
    oldnumber = models.CharField(max_length=16, blank=True, null=True)
    remarks1 = models.CharField(max_length=100, blank=True, null=True)
    advname1 = models.CharField(max_length=100, blank=True, null=True)
    advcd1 = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    verified_on = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'index_register'


class IssueMaster(models.Model):
    pk = models.CompositePrimaryKey('case_type_cd', 'nature_cd', 'issue_cd', 'type_flag')
    case_type_cd = models.CharField(max_length=1000)
    nature_cd = models.SmallIntegerField()
    issue_cd = models.SmallIntegerField()
    issue_desc = models.CharField(max_length=250, blank=True, null=True)
    lissue_desc = models.CharField(max_length=250, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    type_flag = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    issue_template = models.TextField(blank=True, null=True)
    lissue_template = models.TextField(blank=True, null=True)
    under_sec1 = models.CharField(max_length=100, blank=True, null=True)
    under_act1 = models.CharField(max_length=25)
    under_sec2 = models.CharField(max_length=100, blank=True, null=True)
    under_act2 = models.CharField(max_length=25)
    under_sec3 = models.CharField(max_length=100, blank=True, null=True)
    under_act3 = models.CharField(max_length=25)
    under_sec4 = models.CharField(max_length=100, blank=True, null=True)
    under_act4 = models.CharField(max_length=25)

    class Meta:
        managed = False
        db_table = 'issue_master'


class IssueTrans(models.Model):
    pk = models.CompositePrimaryKey('cino', 'issue_id')
    cino = models.CharField(max_length=16)
    issue_date = models.DateField(blank=True, null=True)
    issue_id = models.SmallIntegerField()
    issue = models.TextField(blank=True, null=True)
    disposal_date = models.DateField(blank=True, null=True)
    proved = models.CharField(max_length=1, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'issue_trans'


class IssueTransact(models.Model):
    pk = models.CompositePrimaryKey('todays_date', 'cino')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    issue_cd = models.CharField(max_length=40, blank=True, null=True)
    todays_date = models.DateField()
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'issue_transact'


class JhCaseSectionRule(models.Model):
    pk = models.CompositePrimaryKey('section_rule', 'entry_date', 'cino')
    oldfiling_no = models.CharField(max_length=15, blank=True, null=True)
    section_rule = models.CharField(max_length=50)
    entry_date = models.DateField()
    deal_cd = models.IntegerField(blank=True, null=True)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jh_case_section_rule'


class JudgeNameT(models.Model):
    judge_code = models.SmallIntegerField(primary_key=True)
    judge_name = models.CharField(max_length=100, blank=True, null=True)
    ljudge_name = models.CharField(max_length=100, blank=True, null=True)
    desg_code = models.SmallIntegerField()
    display = models.TextField()  # This field type is a guess.
    jocode = models.CharField(max_length=7, blank=True, null=True)
    state_code = models.CharField(max_length=3, blank=True, null=True)
    jto_dt = models.DateField(blank=True, null=True)
    jfrom_dt = models.DateField(blank=True, null=True)
    judge_priority = models.IntegerField(blank=True, null=True)
    short_judge_name = models.CharField(max_length=50, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)
    not_jocode = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'judge_name_t'


class JudgeT(models.Model):
    pk = models.CompositePrimaryKey('court_no', 'judge_code', 'from_dt')
    court_no = models.IntegerField()
    judge_code = models.SmallIntegerField()
    desg_code = models.SmallIntegerField(blank=True, null=True)
    from_dt = models.DateField()
    incharge = models.TextField()  # This field type is a guess.
    to_dt = models.DateField(blank=True, null=True)
    courtfiling = models.TextField()  # This field type is a guess.
    noprefix = models.SmallIntegerField()
    display = models.TextField()  # This field type is a guess.
    jocode = models.CharField(max_length=7, blank=True, null=True)
    successor_court = models.SmallIntegerField(blank=True, null=True)
    judge_priority = models.SmallIntegerField()
    notify_court_id = models.CharField(max_length=100, blank=True, null=True)
    link_court = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'judge_t'


class JudgeleaveT(models.Model):
    pk = models.CompositePrimaryKey('leave_id', 'court_no', 'judge_no')
    leave_id = models.SmallIntegerField()
    court_no = models.IntegerField()
    judge_no = models.SmallIntegerField()
    desg_no = models.SmallIntegerField()
    leave_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    leavetype = models.CharField(max_length=1)
    nodays = models.CharField(max_length=5, blank=True, null=True)
    halfday = models.TextField()  # This field type is a guess.
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    leave_type = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'judgeleave_t'


class JudgmentTemplate(models.Model):
    judgment_code = models.SmallIntegerField(primary_key=True)
    judgment_name = models.CharField(max_length=200, blank=True, null=True)
    template_name = models.CharField(max_length=200, blank=True, null=True)
    ljudgment_name = models.CharField(max_length=200, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'judgment_template'


class KioskLabels(models.Model):
    pk = models.CompositePrimaryKey('state_code', 'label_id')
    state_code = models.IntegerField()
    label_id = models.IntegerField()
    marathi_label = models.CharField(max_length=300, blank=True, null=True)
    english_label = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kiosk_labels'


class LabelT(models.Model):
    label_name = models.CharField(max_length=255)
    display = models.CharField()
    llabel_name = models.CharField(max_length=255, blank=True, null=True)
    labelid = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'label_t'


class LcaseTypeT(models.Model):
    lcase_type = models.SmallIntegerField(primary_key=True)
    type_name = models.CharField(max_length=50, blank=True, null=True)
    national_code = models.BigIntegerField()
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'lcase_type_t'


class LcourtT(models.Model):
    lower_court_code = models.SmallIntegerField()
    lower_court_name = models.CharField(max_length=100, blank=True, null=True)
    llower_court_name = models.CharField(max_length=100, blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    display = models.TextField()  # This field type is a guess.
    est_code = models.CharField(max_length=6, blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    tribunal_fora = models.TextField()  # This field type is a guess.
    srno = models.AutoField(primary_key=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'lcourt_t'


class LeaveType(models.Model):
    leave_type_code = models.IntegerField(primary_key=True)
    leave_type_name = models.CharField(max_length=250, blank=True, null=True)
    lleave_type_name = models.CharField(max_length=250, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'leave_type'


class LinkDetail(models.Model):
    alerts = models.TextField(blank=True, null=True)
    top_menu = models.CharField(max_length=100, blank=True, null=True)
    buttons = models.TextField(blank=True, null=True)
    labels = models.TextField(blank=True, null=True)
    linkid = models.IntegerField(primary_key=True)
    bottom_menu = models.CharField(max_length=100, blank=True, null=True)
    behaviours = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'link_detail'


class LinksT(models.Model):
    linkid = models.IntegerField(primary_key=True)
    linklang = models.CharField(max_length=200, blank=True, null=True)
    modified_dt = models.DateTimeField()
    reportflag = models.IntegerField(blank=True, null=True)
    display = models.CharField(blank=True, null=True)
    mode = models.IntegerField(blank=True, null=True)
    baselinkid = models.IntegerField(blank=True, null=True)
    level2 = models.IntegerField(blank=True, null=True)
    level3 = models.IntegerField(blank=True, null=True)
    helpeng = models.TextField(blank=True, null=True)
    table_name = models.CharField(max_length=100, blank=True, null=True)
    linkeng = models.CharField(max_length=200, blank=True, null=True)
    priority = models.IntegerField(blank=True, null=True)
    helplang = models.TextField(blank=True, null=True)
    level1 = models.IntegerField(blank=True, null=True)
    formname = models.CharField(max_length=100, blank=True, null=True)
    onlyenglish = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'links_t'


class LitigantStatusT(models.Model):
    code = models.BigIntegerField(primary_key=True)
    edesc = models.CharField(max_length=100, blank=True, null=True)
    ledesc = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'litigant_status_t'


class LokadalatCases(models.Model):
    pk = models.CompositePrimaryKey('lokadalat_id', 'cino', 'sr_no')
    lokadalat_id = models.IntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    cino = models.CharField(max_length=16)
    filing_no = models.CharField(max_length=16, blank=True, null=True)
    allocation_date = models.DateField(blank=True, null=True)
    pet_name = models.CharField(max_length=100, blank=True, null=True)
    res_name = models.CharField(max_length=100, blank=True, null=True)
    court_no = models.IntegerField()
    panel_id = models.IntegerField(blank=True, null=True)
    settlement = models.TextField(blank=True, null=True)  # This field type is a guess.
    date_of_settlement = models.DateField(blank=True, null=True)
    linkcase_no = models.CharField(max_length=15, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    sr_no = models.BigIntegerField()
    lpet_name = models.CharField(max_length=100, blank=True, null=True)
    lres_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lokadalat_cases'


class LokadalatCasesA(models.Model):
    pk = models.CompositePrimaryKey('lokadalat_id', 'cino', 'sr_no')
    lokadalat_id = models.IntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    cino = models.CharField(max_length=16)
    filing_no = models.CharField(max_length=16, blank=True, null=True)
    allocation_date = models.DateField(blank=True, null=True)
    pet_name = models.CharField(max_length=100, blank=True, null=True)
    res_name = models.CharField(max_length=100, blank=True, null=True)
    court_no = models.IntegerField()
    panel_id = models.IntegerField(blank=True, null=True)
    settlement = models.TextField(blank=True, null=True)  # This field type is a guess.
    date_of_settlement = models.DateField(blank=True, null=True)
    linkcase_no = models.CharField(max_length=15, blank=True, null=True)
    sr_no = models.BigIntegerField()
    lpet_name = models.CharField(max_length=100, blank=True, null=True)
    lres_name = models.CharField(max_length=100, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lokadalat_cases_a'


class LokadalatMaster(models.Model):
    lokadalat_id = models.IntegerField(primary_key=True)
    lokadalat_type = models.CharField(max_length=150, blank=True, null=True)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    type_of_lokadalat = models.SmallIntegerField()
    lokadalat_completion = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    archive = models.CharField(max_length=1, blank=True, null=True)
    llokadalat_type = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lokadalat_master'


class LokadalatMember(models.Model):
    member_id = models.IntegerField(primary_key=True)
    member_type = models.SmallIntegerField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    adv_bar = models.CharField(max_length=20, blank=True, null=True)
    adv_code = models.IntegerField()
    jocode = models.CharField(max_length=7, blank=True, null=True)
    judge_name = models.CharField(max_length=255, blank=True, null=True)
    other_name = models.CharField(max_length=255, blank=True, null=True)
    active = models.TextField(blank=True, null=True)  # This field type is a guess.
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    lname = models.CharField(max_length=255, blank=True, null=True)
    ljudge_name = models.CharField(max_length=255, blank=True, null=True)
    lother_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lokadalat_member'


class LokadalatPanels(models.Model):
    pk = models.CompositePrimaryKey('lokadalat_id', 'panel_id')
    lokadalat_id = models.IntegerField()
    panel_id = models.IntegerField()
    member_id = models.CharField(max_length=255, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lokadalat_panels'


class Mahagrass(models.Model):
    pk = models.CompositePrimaryKey('grass_off_cd', 'grass_uid', 'grass_ver_url', 'grass_def_url')
    grass_off_cd = models.CharField(max_length=6)
    grass_uid = models.CharField(max_length=50)
    grass_pwd = models.CharField(max_length=128, blank=True, null=True)
    grass_ver_url = models.CharField(max_length=200)
    grass_def_url = models.CharField(max_length=200)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mahagrass'


class MailinfoT(models.Model):
    sr_no = models.BigIntegerField(primary_key=True)
    from_user = models.CharField(max_length=20, blank=True, null=True)
    to_user = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    send_date = models.DateTimeField()
    subject = models.CharField(max_length=100, blank=True, null=True)
    checked = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mailinfo_t'


class MediationMember(models.Model):
    member_id = models.SmallIntegerField(primary_key=True)
    member_type = models.CharField(max_length=1, blank=True, null=True)
    member = models.CharField(max_length=100, blank=True, null=True)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    expertise = models.CharField(max_length=100, blank=True, null=True)
    jo_code = models.CharField(max_length=7, blank=True, null=True)
    adv_code = models.BigIntegerField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    lmember = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mediation_member'


class MediationProc(models.Model):
    pk = models.CompositePrimaryKey('cin', 'todays_date')
    cin = models.CharField(max_length=20)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    regn_no = models.CharField(max_length=15, blank=True, null=True)
    proc = models.TextField(blank=True, null=True)
    next_date = models.DateField(blank=True, null=True)
    todays_date = models.DateField()
    stage_id = models.SmallIntegerField(blank=True, null=True)
    disposal_date = models.DateField(blank=True, null=True)
    result = models.CharField(max_length=1, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mediation_proc'


class MediationRefer(models.Model):
    pk = models.CompositePrimaryKey('cin', 'member_id', 'ref_date')
    cin = models.CharField(max_length=20)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    regn_no = models.CharField(max_length=15, blank=True, null=True)
    member_id = models.SmallIntegerField()
    ref_date = models.DateField()
    disposal_date = models.DateField(blank=True, null=True)
    todays_date = models.DateField(blank=True, null=True)
    proc = models.TextField(blank=True, null=True)
    result = models.CharField(max_length=1, blank=True, null=True)
    allocation_date = models.DateField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mediation_refer'


class MediationStage(models.Model):
    stage_id = models.SmallIntegerField(primary_key=True)
    stage = models.CharField(max_length=100, blank=True, null=True)
    lstage = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mediation_stage'


class MvcT(models.Model):
    pk = models.CompositePrimaryKey('item_no', 'cino')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    item_no = models.SmallIntegerField()
    police_stn_code = models.IntegerField()
    other_police_stn = models.CharField(max_length=200, blank=True, null=True)
    fir_no = models.CharField(max_length=15, blank=True, null=True)
    year = models.SmallIntegerField()
    accident_date = models.DateField(blank=True, null=True)
    accident_place = models.CharField(max_length=200, blank=True, null=True)
    compensation = models.CharField(max_length=200, blank=True, null=True)
    insurance_company = models.CharField(max_length=200, blank=True, null=True)
    vehicle_type = models.CharField(max_length=100, blank=True, null=True)
    vehicle_regn_no = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    accident_time = models.TimeField(blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    fir_type_code = models.SmallIntegerField()
    driving_license = models.CharField(max_length=100, blank=True, null=True)
    issuing_authority = models.CharField(max_length=100, blank=True, null=True)
    owner_name = models.CharField(max_length=99, blank=True, null=True)
    lowner_name = models.CharField(max_length=99, blank=True, null=True)
    lissuing_authority = models.CharField(max_length=100, blank=True, null=True)
    laccident_place = models.CharField(max_length=200, blank=True, null=True)
    cino = models.CharField(max_length=16)
    state_id = models.IntegerField(blank=True, null=True)
    injury_type = models.SmallIntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mvc_t'


class NatureT(models.Model):
    pk = models.CompositePrimaryKey('case_type_cd', 'nature_cd')
    case_type_cd = models.SmallIntegerField()
    nature_cd = models.SmallIntegerField()
    nature_desc = models.CharField(max_length=100, blank=True, null=True)
    lnature_desc = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    res_disp = models.SmallIntegerField()
    national_code = models.BigIntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'nature_t'


class NazaratOrder(models.Model):
    order_no = models.SmallIntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    court_no = models.IntegerField()
    order_date = models.DateField(blank=True, null=True)
    depositby = models.CharField(max_length=500, blank=True, null=True)
    depositby_id = models.CharField(max_length=100, blank=True, null=True)
    depositby_party_type = models.CharField(max_length=100, blank=True, null=True)
    deposit_party_address = models.TextField(blank=True, null=True)
    ldepositby = models.CharField(max_length=500, blank=True, null=True)
    deposit = models.DecimalField(max_digits=17, decimal_places=2)
    deposit_rem = models.TextField(blank=True, null=True)
    paymentby = models.CharField(max_length=500, blank=True, null=True)
    paymentby_id = models.CharField(max_length=100, blank=True, null=True)
    paymentby_party_type = models.CharField(max_length=100, blank=True, null=True)
    lpaymentby = models.CharField(max_length=500, blank=True, null=True)
    payment = models.DecimalField(max_digits=17, decimal_places=2)
    payment_rem = models.CharField(max_length=255, blank=True, null=True)
    type = models.SmallIntegerField()
    punishment = models.SmallIntegerField()
    punishment_section = models.CharField(max_length=255, blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    proposed_fine = models.DecimalField(max_digits=17, decimal_places=2)
    imprisonment = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'nazarat_order'


class NeutralCitation(models.Model):
    pk = models.CompositePrimaryKey('cino', 'nc')
    cino = models.CharField(max_length=16)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    regcase_type = models.SmallIntegerField(blank=True, null=True)
    reg_no = models.IntegerField()
    reg_year = models.SmallIntegerField()
    filcase_type = models.SmallIntegerField(blank=True, null=True)
    fil_no = models.IntegerField()
    fil_year = models.SmallIntegerField()
    pet_name = models.CharField(max_length=100, blank=True, null=True)
    res_name = models.CharField(max_length=100, blank=True, null=True)
    filing_date = models.DateField(blank=True, null=True)
    reg_date = models.DateField(blank=True, null=True)
    disposal_date = models.DateField(blank=True, null=True)
    order_upload_date_time = models.DateTimeField(blank=True, null=True)
    order_no = models.SmallIntegerField()
    nc_court = models.CharField(max_length=9, blank=True, null=True)
    nc_no = models.IntegerField()
    nc_year = models.IntegerField()
    nc = models.CharField(max_length=25)
    benchtype = models.CharField(max_length=2, blank=True, null=True)
    ip_details = models.CharField(max_length=20, blank=True, null=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    userid = models.SmallIntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'neutral_citation'


class NotBeforeMe(models.Model):
    judge_code = models.IntegerField(primary_key=True)
    adv_code = models.TextField(blank=True, null=True)
    adv_bar_reg_no = models.TextField(blank=True, null=True)
    org_code = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'not_before_me'


class NoticeT(models.Model):
    noticecode = models.SmallIntegerField(primary_key=True)
    notice_title = models.CharField(max_length=255, blank=True, null=True)
    lnotice_title = models.CharField(max_length=255, blank=True, null=True)
    notice_detail = models.TextField(blank=True, null=True)
    lnotice_detail = models.TextField(blank=True, null=True)
    file_name = models.CharField(max_length=50, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    national_code = models.BigIntegerField(blank=True, null=True)
    label1 = models.CharField(max_length=150, blank=True, null=True)
    label2 = models.CharField(max_length=150, blank=True, null=True)
    label3 = models.CharField(max_length=150, blank=True, null=True)
    label4 = models.CharField(max_length=150, blank=True, null=True)
    label5 = models.CharField(max_length=150, blank=True, null=True)
    label1mar = models.CharField(max_length=150, blank=True, null=True)
    label2mar = models.CharField(max_length=150, blank=True, null=True)
    label3mar = models.CharField(max_length=150, blank=True, null=True)
    label4mar = models.CharField(max_length=150, blank=True, null=True)
    label5mar = models.CharField(max_length=150, blank=True, null=True)
    notice_priority = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notice_t'


class NotifyCourt(models.Model):
    notify_court_id = models.IntegerField(primary_key=True)
    notify_court = models.CharField(max_length=99, blank=True, null=True)
    lnotify_court = models.CharField(max_length=99, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notify_court'


class ObjectionHistory(models.Model):
    pk = models.CompositePrimaryKey('cino', 'srno')
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    objection = models.TextField(blank=True, null=True)
    objdescription = models.TextField(blank=True, null=True)
    lobjection = models.TextField(blank=True, null=True)
    obj_redate = models.DateField(blank=True, null=True)
    objreturn_dt = models.DateField(blank=True, null=True)
    objreceipt_dt = models.DateField(blank=True, null=True)
    objprepare_dt = models.DateField(blank=True, null=True)
    cino = models.CharField(max_length=16)
    srno = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'objection_history'


class ObjectionHistoryA(models.Model):
    pk = models.CompositePrimaryKey('cino', 'srno')
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    objection = models.TextField(blank=True, null=True)
    objdescription = models.TextField(blank=True, null=True)
    lobjection = models.TextField(blank=True, null=True)
    obj_redate = models.DateField(blank=True, null=True)
    objreturn_dt = models.DateField(blank=True, null=True)
    objreceipt_dt = models.DateField(blank=True, null=True)
    objprepare_dt = models.DateField(blank=True, null=True)
    cino = models.CharField(max_length=16)
    srno = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'objection_history_a'


class ObjectionT(models.Model):
    objcode = models.SmallIntegerField(primary_key=True)
    objtype = models.TextField(blank=True, null=True)
    lobjtype = models.TextField(blank=True, null=True)
    casetype_flag = models.SmallIntegerField()
    bool_type = models.SmallIntegerField()
    display = models.TextField()  # This field type is a guess.
    case_type = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'objection_t'


class OrderDetails(models.Model):
    pk = models.CompositePrimaryKey('order_no', 'cino')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    order_no = models.SmallIntegerField()
    order_dt = models.DateField(blank=True, null=True)
    download = models.TextField()  # This field type is a guess.
    upload = models.TextField()  # This field type is a guess.
    doc_type = models.SmallIntegerField()
    ordloc_lang = models.TextField()  # This field type is a guess.
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
        db_table = 'order_details'


class OrderDetailsA(models.Model):
    pk = models.CompositePrimaryKey('order_no', 'cino')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    order_no = models.SmallIntegerField()
    order_dt = models.DateField(blank=True, null=True)
    download = models.TextField()  # This field type is a guess.
    upload = models.TextField()  # This field type is a guess.
    doc_type = models.SmallIntegerField()
    ordloc_lang = models.TextField()  # This field type is a guess.
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
        db_table = 'order_details_a'


class OrderT(models.Model):
    order_code = models.SmallIntegerField(primary_key=True)
    order_name = models.CharField(max_length=100, blank=True, null=True)
    lorder_name = models.CharField(max_length=100, blank=True, null=True)
    orderdetail = models.TextField(blank=True, null=True)
    lorderdetail = models.TextField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    short_order_name = models.CharField(max_length=50, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    pretrial_flag = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'order_t'


class OrderTemplate(models.Model):
    order_id = models.IntegerField(primary_key=True)
    template_name = models.TextField(blank=True, null=True)
    case_type = models.TextField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    jud_ord_type = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_template'


class OrgnameT(models.Model):
    orgid = models.SmallIntegerField(primary_key=True)
    orgname = models.CharField(max_length=100, blank=True, null=True)
    lorgname = models.CharField(max_length=100, blank=True, null=True)
    orgtype = models.BigIntegerField()
    contactperson = models.CharField(max_length=100, blank=True, null=True)
    lcontactperson = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    email = models.CharField(max_length=254, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    fax = models.CharField(max_length=15, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    national_code = models.CharField(max_length=15, blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'orgname_t'


class OrgtypeT(models.Model):
    orgcode = models.BigIntegerField(primary_key=True)
    orgtype = models.CharField(max_length=100, blank=True, null=True)
    lorgtype = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    national_code = models.CharField(max_length=15, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orgtype_t'


class OriCourtMaster(models.Model):
    court_no = models.IntegerField(primary_key=True)
    court_name = models.CharField(max_length=50, blank=True, null=True)
    court_desc = models.CharField(max_length=50, blank=True, null=True)
    court_place = models.CharField(max_length=50, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ori_court_master'


class PartyAddress(models.Model):
    pk = models.CompositePrimaryKey('cino', 'party_no', 'type', 'address_type')
    cino = models.CharField(max_length=16)
    address = models.TextField(blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    state_id = models.SmallIntegerField(blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    pincode = models.IntegerField(blank=True, null=True)
    police_st_code = models.IntegerField()
    party_no = models.SmallIntegerField()
    type = models.SmallIntegerField()
    address_type = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'party_address'


class PartyAddressA(models.Model):
    pk = models.CompositePrimaryKey('cino', 'party_no', 'type', 'address_type')
    cino = models.CharField(max_length=16)
    address = models.TextField(blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    state_id = models.SmallIntegerField(blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    pincode = models.IntegerField(blank=True, null=True)
    police_st_code = models.IntegerField()
    party_no = models.SmallIntegerField()
    type = models.SmallIntegerField()
    address_type = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'party_address_a'


class PartyExtraInfo(models.Model):
    pk = models.CompositePrimaryKey('cino', 'party_no', 'type')
    cino = models.CharField(max_length=16)
    party_no = models.SmallIntegerField()
    type = models.SmallIntegerField()
    nationality = models.CharField(max_length=99, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    fax = models.CharField(max_length=15, blank=True, null=True)
    occupation = models.CharField(max_length=50, blank=True, null=True)
    passportno = models.CharField(max_length=25, blank=True, null=True)
    country = models.CharField(max_length=99, blank=True, null=True)
    panno = models.CharField(max_length=10, blank=True, null=True)
    ph = models.TextField()  # This field type is a guess.
    loccupation = models.CharField(max_length=50, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'party_extra_info'


class PartyExtraInfoA(models.Model):
    pk = models.CompositePrimaryKey('cino', 'party_no', 'type')
    cino = models.CharField(max_length=16)
    party_no = models.SmallIntegerField()
    type = models.SmallIntegerField()
    nationality = models.CharField(max_length=99, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    fax = models.CharField(max_length=15, blank=True, null=True)
    occupation = models.CharField(max_length=50, blank=True, null=True)
    passportno = models.CharField(max_length=25, blank=True, null=True)
    country = models.CharField(max_length=99, blank=True, null=True)
    panno = models.CharField(max_length=10, blank=True, null=True)
    ph = models.TextField()  # This field type is a guess.
    loccupation = models.CharField(max_length=50, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'party_extra_info_a'


class PartyExtraactT(models.Model):
    pk = models.CompositePrimaryKey('serialno', 'cino')
    serialno = models.SmallIntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    acts = models.BigIntegerField(blank=True, null=True)
    section = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    party_no = models.SmallIntegerField(blank=True, null=True)
    type = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'party_extraact_t'


class PartyExtraactTA(models.Model):
    pk = models.CompositePrimaryKey('serialno', 'cino')
    serialno = models.SmallIntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    acts = models.BigIntegerField(blank=True, null=True)
    section = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    party_no = models.SmallIntegerField(blank=True, null=True)
    type = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'party_extraact_t_a'


class Passover(models.Model):
    pk = models.CompositePrimaryKey('todays_date', 'passover_date')
    todays_date = models.DateField()
    passover_date = models.DateField()
    order_code = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'passover'


class PaymentFineRefund(models.Model):
    pk = models.CompositePrimaryKey('register_type', 'payment_reg_no', 'posting_date', 'cino')
    payment_sl_no = models.IntegerField()
    deposit_form_a_sl_no = models.IntegerField()
    nazarat_order_order_no = models.SmallIntegerField()
    nazarat_order_order_type = models.SmallIntegerField()
    nazarat_order_order_date = models.DateField(blank=True, null=True)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    pet_res_name = models.CharField(max_length=100, blank=True, null=True)
    pet_res_id = models.SmallIntegerField()
    pet_res_type = models.CharField(max_length=1, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    repr_name = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2)
    paymode = models.CharField(max_length=1, blank=True, null=True)
    cheque_details = models.CharField(max_length=255, blank=True, null=True)
    chk_date = models.DateField(blank=True, null=True)
    payment_made_by = models.CharField(db_column='payment_made__by', max_length=255, blank=True, null=True)  # Field renamed because it contained more than one '_' in a row.
    deposit_form_a_account_purpose = models.SmallIntegerField()
    deposit_form_a_subject = models.CharField(max_length=255, blank=True, null=True)
    register_type = models.SmallIntegerField()
    payment_date = models.DateField(blank=True, null=True)
    payment_reg_no = models.IntegerField()
    deposit_reg_no = models.CharField(max_length=255, blank=True, null=True)
    payment_to = models.CharField(max_length=255, blank=True, null=True)
    posting_date = models.DateField()
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment_fine_refund'


class PaymentRegister(models.Model):
    pk = models.CompositePrimaryKey('payment_date', 'payment_reg_no')
    payment_sl_no = models.IntegerField()
    deposit_form_a_sl_no = models.IntegerField()
    nazarat_order_order_no = models.SmallIntegerField()
    nazarat_order_order_type = models.SmallIntegerField()
    nazarat_order_order_date = models.DateField(blank=True, null=True)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    pet_res_name = models.CharField(max_length=100, blank=True, null=True)
    pet_res_id = models.SmallIntegerField()
    pet_res_type = models.CharField(max_length=1, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    repr_name = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=17, decimal_places=2)
    paymode = models.CharField(max_length=1, blank=True, null=True)
    cheque_details = models.CharField(max_length=255, blank=True, null=True)
    chk_date = models.DateField(blank=True, null=True)
    payment_made_by = models.CharField(db_column='payment_made__by', max_length=255, blank=True, null=True)  # Field renamed because it contained more than one '_' in a row.
    deposit_form_a_account_purpose = models.SmallIntegerField()
    deposit_form_a_subject = models.CharField(max_length=255, blank=True, null=True)
    register_type = models.SmallIntegerField()
    payment_date = models.DateField()
    payment_reg_no = models.IntegerField()
    deposit_reg_no = models.CharField(max_length=255, blank=True, null=True)
    posting_date = models.DateField(blank=True, null=True)
    fd_maturity_date = models.DateField(blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment_register'


class PoliceStatDetailsT(models.Model):
    case_no = models.CharField(max_length=15, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    crno = models.CharField(max_length=17, blank=True, null=True)
    court_no = models.IntegerField()
    police_stn_code = models.IntegerField()
    fir_type_code = models.SmallIntegerField()
    fir_no = models.CharField(max_length=15)
    fir_year = models.SmallIntegerField()
    fir_date = models.DateField(blank=True, null=True)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    from_time = models.CharField(max_length=10, blank=True, null=True)
    to_time = models.CharField(max_length=10, blank=True, null=True)
    paddress = models.TextField(blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    cname = models.CharField(max_length=100, blank=True, null=True)
    relation_flag = models.CharField(max_length=2)
    relation_name = models.CharField(max_length=100, blank=True, null=True)
    dateofbirth = models.DateField(blank=True, null=True)
    age = models.SmallIntegerField()
    passport_no = models.CharField(max_length=25, blank=True, null=True)
    dateofissue = models.DateField(blank=True, null=True)
    placeofissue = models.CharField(max_length=50, blank=True, null=True)
    occupation = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    name1 = models.CharField(max_length=100, blank=True, null=True)
    lname1 = models.CharField(max_length=100, blank=True, null=True)
    name2 = models.CharField(max_length=100, blank=True, null=True)
    lname2 = models.CharField(max_length=100, blank=True, null=True)
    name3 = models.CharField(max_length=100, blank=True, null=True)
    lname3 = models.CharField(max_length=100, blank=True, null=True)
    name4 = models.CharField(max_length=100, blank=True, null=True)
    lname4 = models.CharField(max_length=100, blank=True, null=True)
    name5 = models.CharField(max_length=100, blank=True, null=True)
    lname5 = models.CharField(max_length=100, blank=True, null=True)
    age1 = models.SmallIntegerField()
    age2 = models.SmallIntegerField()
    age3 = models.SmallIntegerField()
    age4 = models.SmallIntegerField()
    age5 = models.SmallIntegerField()
    sex1 = models.CharField(max_length=1, blank=True, null=True)
    sex2 = models.CharField(max_length=1, blank=True, null=True)
    sex3 = models.CharField(max_length=1, blank=True, null=True)
    sex4 = models.CharField(max_length=1, blank=True, null=True)
    sex5 = models.CharField(max_length=1, blank=True, null=True)
    charge1 = models.CharField(max_length=1, blank=True, null=True)
    charge2 = models.CharField(max_length=1, blank=True, null=True)
    charge3 = models.CharField(max_length=1, blank=True, null=True)
    charge4 = models.CharField(max_length=1, blank=True, null=True)
    charge5 = models.CharField(max_length=1, blank=True, null=True)
    investofficer = models.CharField(max_length=99, blank=True, null=True)
    linvestofficer = models.CharField(max_length=99, blank=True, null=True)
    beltno = models.CharField(max_length=50, blank=True, null=True)
    investofficer1 = models.CharField(max_length=99, blank=True, null=True)
    linvestofficer1 = models.CharField(max_length=99, blank=True, null=True)
    beltno1 = models.CharField(max_length=50, blank=True, null=True)
    rank = models.CharField(max_length=99)
    rank1 = models.CharField(max_length=99)
    fircontents = models.TextField(blank=True, null=True)
    lfircontents = models.TextField(blank=True, null=True)
    firreceiptdate = models.DateField(blank=True, null=True)
    firreceipttime = models.CharField(max_length=10, blank=True, null=True)
    lpaddress = models.TextField(blank=True, null=True)
    lcname = models.CharField(max_length=100, blank=True, null=True)
    lrelationname = models.CharField(max_length=150, blank=True, null=True)
    lplaceofissue = models.CharField(max_length=150, blank=True, null=True)
    loccupation = models.CharField(max_length=150, blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    summ_charge = models.SmallIntegerField()
    summary_id = models.SmallIntegerField()
    remarks = models.TextField(blank=True, null=True)
    lremarks = models.TextField(blank=True, null=True)
    receivedate = models.DateField(blank=True, null=True)
    receivetime = models.CharField(max_length=10, blank=True, null=True)
    address1 = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    address3 = models.TextField(blank=True, null=True)
    address4 = models.TextField(blank=True, null=True)
    address5 = models.TextField(blank=True, null=True)
    laddress1 = models.TextField(blank=True, null=True)
    laddress2 = models.TextField(blank=True, null=True)
    laddress3 = models.TextField(blank=True, null=True)
    laddress4 = models.TextField(blank=True, null=True)
    laddress5 = models.TextField(blank=True, null=True)
    crime_no = models.IntegerField()
    crime_year = models.SmallIntegerField()
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    gender1 = models.CharField(max_length=1, blank=True, null=True)
    gender2 = models.CharField(max_length=1, blank=True, null=True)
    gender3 = models.CharField(max_length=1, blank=True, null=True)
    gender4 = models.CharField(max_length=1, blank=True, null=True)
    gender5 = models.CharField(max_length=1, blank=True, null=True)
    cname_salutation = models.SmallIntegerField(blank=True, null=True)
    name1_salutation = models.SmallIntegerField(blank=True, null=True)
    name2_salutation = models.SmallIntegerField(blank=True, null=True)
    name3_salutation = models.SmallIntegerField(blank=True, null=True)
    name4_salutation = models.SmallIntegerField(blank=True, null=True)
    name5_salutation = models.SmallIntegerField(blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    efir_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    efir_date = models.DateTimeField(blank=True, null=True)
    econfirm = models.CharField(max_length=1, blank=True, null=True)
    eremark = models.TextField(blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    efilno = models.CharField(max_length=99)

    class Meta:
        managed = False
        db_table = 'police_stat_details_t'


class PoliceStatDetailsTA(models.Model):
    case_no = models.CharField(max_length=15, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    crno = models.CharField(max_length=17, blank=True, null=True)
    court_no = models.IntegerField()
    police_stn_code = models.IntegerField()
    fir_type_code = models.SmallIntegerField()
    fir_no = models.CharField(max_length=15)
    fir_year = models.SmallIntegerField()
    fir_date = models.DateField(blank=True, null=True)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    from_time = models.CharField(max_length=10, blank=True, null=True)
    to_time = models.CharField(max_length=10, blank=True, null=True)
    paddress = models.TextField(blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    cname = models.CharField(max_length=100, blank=True, null=True)
    relation_flag = models.CharField(max_length=2)
    relation_name = models.CharField(max_length=100, blank=True, null=True)
    dateofbirth = models.DateField(blank=True, null=True)
    age = models.SmallIntegerField()
    passport_no = models.CharField(max_length=25, blank=True, null=True)
    dateofissue = models.DateField(blank=True, null=True)
    placeofissue = models.CharField(max_length=50, blank=True, null=True)
    occupation = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    name1 = models.CharField(max_length=100, blank=True, null=True)
    lname1 = models.CharField(max_length=100, blank=True, null=True)
    name2 = models.CharField(max_length=100, blank=True, null=True)
    lname2 = models.CharField(max_length=100, blank=True, null=True)
    name3 = models.CharField(max_length=100, blank=True, null=True)
    lname3 = models.CharField(max_length=100, blank=True, null=True)
    name4 = models.CharField(max_length=100, blank=True, null=True)
    lname4 = models.CharField(max_length=100, blank=True, null=True)
    name5 = models.CharField(max_length=100, blank=True, null=True)
    lname5 = models.CharField(max_length=100, blank=True, null=True)
    age1 = models.SmallIntegerField()
    age2 = models.SmallIntegerField()
    age3 = models.SmallIntegerField()
    age4 = models.SmallIntegerField()
    age5 = models.SmallIntegerField()
    sex1 = models.CharField(max_length=1, blank=True, null=True)
    sex2 = models.CharField(max_length=1, blank=True, null=True)
    sex3 = models.CharField(max_length=1, blank=True, null=True)
    sex4 = models.CharField(max_length=1, blank=True, null=True)
    sex5 = models.CharField(max_length=1, blank=True, null=True)
    charge1 = models.CharField(max_length=1, blank=True, null=True)
    charge2 = models.CharField(max_length=1, blank=True, null=True)
    charge3 = models.CharField(max_length=1, blank=True, null=True)
    charge4 = models.CharField(max_length=1, blank=True, null=True)
    charge5 = models.CharField(max_length=1, blank=True, null=True)
    investofficer = models.CharField(max_length=99, blank=True, null=True)
    linvestofficer = models.CharField(max_length=99, blank=True, null=True)
    beltno = models.CharField(max_length=50, blank=True, null=True)
    investofficer1 = models.CharField(max_length=99, blank=True, null=True)
    linvestofficer1 = models.CharField(max_length=99, blank=True, null=True)
    beltno1 = models.CharField(max_length=50, blank=True, null=True)
    rank = models.CharField(max_length=99)
    rank1 = models.CharField(max_length=99)
    fircontents = models.TextField(blank=True, null=True)
    lfircontents = models.TextField(blank=True, null=True)
    firreceiptdate = models.DateField(blank=True, null=True)
    firreceipttime = models.CharField(max_length=10, blank=True, null=True)
    lpaddress = models.TextField(blank=True, null=True)
    lcname = models.CharField(max_length=100, blank=True, null=True)
    lrelationname = models.CharField(max_length=150, blank=True, null=True)
    lplaceofissue = models.CharField(max_length=150, blank=True, null=True)
    loccupation = models.CharField(max_length=150, blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    summ_charge = models.SmallIntegerField()
    summary_id = models.SmallIntegerField()
    remarks = models.TextField(blank=True, null=True)
    lremarks = models.TextField(blank=True, null=True)
    receivedate = models.DateField(blank=True, null=True)
    receivetime = models.CharField(max_length=10, blank=True, null=True)
    address1 = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    address3 = models.TextField(blank=True, null=True)
    address4 = models.TextField(blank=True, null=True)
    address5 = models.TextField(blank=True, null=True)
    laddress1 = models.TextField(blank=True, null=True)
    laddress2 = models.TextField(blank=True, null=True)
    laddress3 = models.TextField(blank=True, null=True)
    laddress4 = models.TextField(blank=True, null=True)
    laddress5 = models.TextField(blank=True, null=True)
    crime_no = models.IntegerField()
    crime_year = models.SmallIntegerField()
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    state_id = models.IntegerField(blank=True, null=True)
    cname_salutation = models.SmallIntegerField(blank=True, null=True)
    name1_salutation = models.SmallIntegerField(blank=True, null=True)
    name2_salutation = models.SmallIntegerField(blank=True, null=True)
    name3_salutation = models.SmallIntegerField(blank=True, null=True)
    name4_salutation = models.SmallIntegerField(blank=True, null=True)
    name5_salutation = models.SmallIntegerField(blank=True, null=True)
    gender1 = models.CharField(max_length=1, blank=True, null=True)
    gender2 = models.CharField(max_length=1, blank=True, null=True)
    gender3 = models.CharField(max_length=1, blank=True, null=True)
    gender4 = models.CharField(max_length=1, blank=True, null=True)
    gender5 = models.CharField(max_length=1, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    efir_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    efir_date = models.DateTimeField(blank=True, null=True)
    econfirm = models.CharField(max_length=1, blank=True, null=True)
    eremark = models.TextField(blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    efilno = models.CharField(max_length=99)

    class Meta:
        managed = False
        db_table = 'police_stat_details_t_a'


class PoliceStatDetailsTRejected(models.Model):
    case_no = models.CharField(max_length=15, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    crno = models.CharField(max_length=17, blank=True, null=True)
    court_no = models.IntegerField()
    police_stn_code = models.IntegerField()
    fir_type_code = models.SmallIntegerField()
    fir_no = models.CharField(max_length=15)
    fir_year = models.SmallIntegerField()
    fir_date = models.DateField(blank=True, null=True)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    from_time = models.CharField(max_length=10, blank=True, null=True)
    to_time = models.CharField(max_length=10, blank=True, null=True)
    paddress = models.TextField(blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    cname = models.CharField(max_length=100, blank=True, null=True)
    relation_flag = models.CharField(max_length=2)
    relation_name = models.CharField(max_length=100, blank=True, null=True)
    dateofbirth = models.DateField(blank=True, null=True)
    age = models.SmallIntegerField()
    passport_no = models.CharField(max_length=25, blank=True, null=True)
    dateofissue = models.DateField(blank=True, null=True)
    placeofissue = models.CharField(max_length=50, blank=True, null=True)
    occupation = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    name1 = models.CharField(max_length=100, blank=True, null=True)
    lname1 = models.CharField(max_length=100, blank=True, null=True)
    name2 = models.CharField(max_length=100, blank=True, null=True)
    lname2 = models.CharField(max_length=100, blank=True, null=True)
    name3 = models.CharField(max_length=100, blank=True, null=True)
    lname3 = models.CharField(max_length=100, blank=True, null=True)
    name4 = models.CharField(max_length=100, blank=True, null=True)
    lname4 = models.CharField(max_length=100, blank=True, null=True)
    name5 = models.CharField(max_length=100, blank=True, null=True)
    lname5 = models.CharField(max_length=100, blank=True, null=True)
    age1 = models.SmallIntegerField()
    age2 = models.SmallIntegerField()
    age3 = models.SmallIntegerField()
    age4 = models.SmallIntegerField()
    age5 = models.SmallIntegerField()
    sex1 = models.CharField(max_length=1, blank=True, null=True)
    sex2 = models.CharField(max_length=1, blank=True, null=True)
    sex3 = models.CharField(max_length=1, blank=True, null=True)
    sex4 = models.CharField(max_length=1, blank=True, null=True)
    sex5 = models.CharField(max_length=1, blank=True, null=True)
    charge1 = models.CharField(max_length=1, blank=True, null=True)
    charge2 = models.CharField(max_length=1, blank=True, null=True)
    charge3 = models.CharField(max_length=1, blank=True, null=True)
    charge4 = models.CharField(max_length=1, blank=True, null=True)
    charge5 = models.CharField(max_length=1, blank=True, null=True)
    investofficer = models.CharField(max_length=99, blank=True, null=True)
    linvestofficer = models.CharField(max_length=99, blank=True, null=True)
    beltno = models.CharField(max_length=50, blank=True, null=True)
    investofficer1 = models.CharField(max_length=99, blank=True, null=True)
    linvestofficer1 = models.CharField(max_length=99, blank=True, null=True)
    beltno1 = models.CharField(max_length=50, blank=True, null=True)
    rank = models.CharField(max_length=99)
    rank1 = models.CharField(max_length=99)
    fircontents = models.TextField(blank=True, null=True)
    lfircontents = models.TextField(blank=True, null=True)
    firreceiptdate = models.DateField(blank=True, null=True)
    firreceipttime = models.CharField(max_length=10, blank=True, null=True)
    lpaddress = models.TextField(blank=True, null=True)
    lcname = models.CharField(max_length=100, blank=True, null=True)
    lrelationname = models.CharField(max_length=150, blank=True, null=True)
    lplaceofissue = models.CharField(max_length=150, blank=True, null=True)
    loccupation = models.CharField(max_length=150, blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    summ_charge = models.SmallIntegerField()
    summary_id = models.SmallIntegerField()
    remarks = models.TextField(blank=True, null=True)
    lremarks = models.TextField(blank=True, null=True)
    receivedate = models.DateField(blank=True, null=True)
    receivetime = models.CharField(max_length=10, blank=True, null=True)
    address1 = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    address3 = models.TextField(blank=True, null=True)
    address4 = models.TextField(blank=True, null=True)
    address5 = models.TextField(blank=True, null=True)
    laddress1 = models.TextField(blank=True, null=True)
    laddress2 = models.TextField(blank=True, null=True)
    laddress3 = models.TextField(blank=True, null=True)
    laddress4 = models.TextField(blank=True, null=True)
    laddress5 = models.TextField(blank=True, null=True)
    crime_no = models.IntegerField()
    crime_year = models.SmallIntegerField()
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    state_id = models.IntegerField(blank=True, null=True)
    cname_salutation = models.SmallIntegerField(blank=True, null=True)
    name1_salutation = models.SmallIntegerField(blank=True, null=True)
    name2_salutation = models.SmallIntegerField(blank=True, null=True)
    name3_salutation = models.SmallIntegerField(blank=True, null=True)
    name4_salutation = models.SmallIntegerField(blank=True, null=True)
    name5_salutation = models.SmallIntegerField(blank=True, null=True)
    gender1 = models.CharField(max_length=1, blank=True, null=True)
    gender2 = models.CharField(max_length=1, blank=True, null=True)
    gender3 = models.CharField(max_length=1, blank=True, null=True)
    gender4 = models.CharField(max_length=1, blank=True, null=True)
    gender5 = models.CharField(max_length=1, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    efir_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    efir_date = models.DateTimeField(blank=True, null=True)
    econfirm = models.CharField(max_length=1, blank=True, null=True)
    eremark = models.TextField(blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    efilno = models.CharField(max_length=99)

    class Meta:
        managed = False
        db_table = 'police_stat_details_t_rejected'


class PoliceStnT(models.Model):
    pk = models.CompositePrimaryKey('state_id', 'dist_code', 'police_st_code')
    police_st_code = models.IntegerField()
    uniform_code = models.BigIntegerField()
    police_st_name = models.CharField(max_length=100, blank=True, null=True)
    lpolice_st_name = models.CharField(max_length=100, blank=True, null=True)
    area_court_no = models.CharField(max_length=500, blank=True, null=True)
    officer_incharge = models.CharField(max_length=150, blank=True, null=True)
    lofficer_incharge = models.CharField(max_length=150, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.CharField(max_length=254, blank=True, null=True)
    mobileno = models.CharField(max_length=15, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    unique_code = models.BigIntegerField()
    state_id = models.IntegerField()
    zonecode = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    active = models.CharField(max_length=1)
    est_code_src = models.CharField(max_length=6)
    last_fir_no = models.IntegerField(blank=True, null=True)
    last_fir_year = models.IntegerField(blank=True, null=True)
    last_chargesheet_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'police_stn_t'


class PrDetails(models.Model):
    pk = models.CompositePrimaryKey('pr_no', 'pr_year', 'item_no')
    pr_no = models.IntegerField()
    pr_year = models.SmallIntegerField()
    item_no = models.IntegerField()
    item_count = models.CharField(max_length=6, blank=True, null=True)
    item_desc = models.CharField(max_length=150, blank=True, null=True)
    item_value = models.CharField(max_length=150, blank=True, null=True)
    tbslno = models.CharField(max_length=10, blank=True, null=True)
    tbno = models.CharField(max_length=10, blank=True, null=True)
    pr_item_date = models.DateField(blank=True, null=True)
    disposal_status = models.CharField(max_length=1, blank=True, null=True)
    display = models.CharField(max_length=1, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pr_details'


class PrDisposal(models.Model):
    pk = models.CompositePrimaryKey('pr_no', 'pr_dispdate', 'pr_year')
    pr_no = models.IntegerField()
    item_no = models.IntegerField(blank=True, null=True)
    item_count = models.CharField(max_length=6, blank=True, null=True)
    pr_dispcode = models.SmallIntegerField()
    pr_dispdate = models.DateField()
    remarks = models.TextField(blank=True, null=True)
    partyname = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    auctionvalue = models.CharField(max_length=10, blank=True, null=True)
    courtname = models.CharField(max_length=50, blank=True, null=True)
    pr_year = models.SmallIntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pr_disposal'


class PrTable(models.Model):
    pk = models.CompositePrimaryKey('pr_no', 'production_date', 'cino')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    police_st_code = models.IntegerField()
    fir_no = models.CharField(max_length=15, blank=True, null=True)
    fir_year = models.SmallIntegerField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    lname = models.CharField(max_length=100, blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    circumstances = models.TextField(blank=True, null=True)
    propertyformno = models.IntegerField()
    propertyformyear = models.SmallIntegerField(blank=True, null=True)
    pr_no = models.IntegerField()
    under_act1 = models.BigIntegerField()
    under_sec1 = models.CharField(max_length=100, blank=True, null=True)
    under_act2 = models.BigIntegerField()
    under_sec2 = models.CharField(max_length=100, blank=True, null=True)
    under_act3 = models.BigIntegerField()
    under_sec3 = models.CharField(max_length=100, blank=True, null=True)
    under_act4 = models.BigIntegerField()
    under_sec4 = models.CharField(max_length=100, blank=True, null=True)
    pr_date = models.DateField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    produced_by = models.CharField(max_length=99, blank=True, null=True)
    production_date = models.DateField()
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pr_table'


class PrayerDetailsT(models.Model):
    pk = models.CompositePrimaryKey('pet_res_name', 'pray_date', 'cino')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    pet_res_name = models.CharField(max_length=100)
    prayers = models.CharField(max_length=255, blank=True, null=True)
    pray_date = models.DateField()
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'prayer_details_t'


class PrayerT(models.Model):
    prayercode = models.SmallIntegerField(primary_key=True)
    prayer_type = models.CharField(max_length=255, blank=True, null=True)
    lprayer_type = models.CharField(max_length=255, blank=True, null=True)
    prayer = models.TextField(blank=True, null=True)
    lprayer = models.TextField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    flag_filing = models.CharField(max_length=1, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'prayer_t'


class PreTrialApplication(models.Model):
    pk = models.CompositePrimaryKey('crno', 'srno')
    crno = models.CharField(max_length=17)
    police_stn_code = models.IntegerField()
    fir_no = models.CharField(max_length=15, blank=True, null=True)
    fir_year = models.SmallIntegerField()
    fir_type_code = models.SmallIntegerField()
    accused_id = models.SmallIntegerField()
    accused_name = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=1, blank=True, null=True)
    date_of_application = models.DateField(blank=True, null=True)
    date_of_order = models.DateField(blank=True, null=True)
    onvc = models.TextField(blank=True, null=True)  # This field type is a guess.
    other_party_flag = models.CharField(max_length=1, blank=True, null=True)
    appl_id = models.SmallIntegerField()
    srno = models.SmallIntegerField()
    date_of_decision = models.DateField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    laccused_name = models.CharField(max_length=100, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    pretrialshort_order = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'pre_trial_application'


class PretrialBail(models.Model):
    pk = models.CompositePrimaryKey('crno', 'srno')
    crno = models.CharField(max_length=17)
    police_stn_code = models.IntegerField()
    fir_no = models.CharField(max_length=15, blank=True, null=True)
    fir_year = models.SmallIntegerField()
    fir_type_code = models.SmallIntegerField()
    accused_id = models.SmallIntegerField()
    accused_name = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=1, blank=True, null=True)
    bail_date = models.DateField(blank=True, null=True)
    appl_date = models.DateField(blank=True, null=True)
    onvc = models.TextField(blank=True, null=True)  # This field type is a guess.
    surety_req = models.SmallIntegerField()
    srno = models.SmallIntegerField()
    date_of_decision = models.DateField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    laccused_name = models.CharField(max_length=100, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    pretrialshort_order = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'pretrial_bail'


class PretrialOrder(models.Model):
    pk = models.CompositePrimaryKey('crno', 'order_no')
    crno = models.CharField(max_length=17)
    police_stn_code = models.IntegerField()
    fir_no = models.CharField(max_length=15, blank=True, null=True)
    fir_year = models.SmallIntegerField()
    fir_type_code = models.SmallIntegerField()
    court_no = models.IntegerField()
    order_no = models.SmallIntegerField()
    order_date = models.DateField(blank=True, null=True)
    docu_type = models.SmallIntegerField()
    remark = models.TextField(blank=True, null=True)
    ordloc_lang = models.TextField(blank=True, null=True)  # This field type is a guess.
    jocode = models.CharField(max_length=150, blank=True, null=True)
    userlogin = models.CharField(max_length=150, blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pretrial_order'


class PretrialProc(models.Model):
    pk = models.CompositePrimaryKey('cr_no', 'accused_no', 'next_date')
    cr_no = models.CharField(max_length=17)
    accused_no = models.SmallIntegerField()
    appl_from = models.CharField(max_length=1, blank=True, null=True)
    todays_date = models.DateField(blank=True, null=True)
    next_date = models.DateField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    pretrialshort_order = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'pretrial_proc'


class PretrialRelease(models.Model):
    pk = models.CompositePrimaryKey('crno', 'srno')
    crno = models.CharField(max_length=17)
    police_stn_code = models.IntegerField()
    fir_no = models.CharField(max_length=15, blank=True, null=True)
    fir_year = models.SmallIntegerField()
    fir_type_code = models.SmallIntegerField()
    accused_id = models.SmallIntegerField()
    accused_name = models.CharField(max_length=100, blank=True, null=True)
    bail_date = models.DateField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    onvc = models.TextField(blank=True, null=True)  # This field type is a guess.
    srno = models.SmallIntegerField()
    laccused_name = models.CharField(max_length=100, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pretrial_release'


class PrisonT(models.Model):
    prison_id = models.SmallIntegerField(primary_key=True)
    prison_name = models.CharField(max_length=100, blank=True, null=True)
    lprison_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    display = models.TextField()  # This field type is a guess.
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    prision_code = models.CharField(max_length=10, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'prison_t'


class ProcessAllocate(models.Model):
    pk = models.CompositePrimaryKey('process_id', 'process_messenger_type', 'bailiff_id', 'allocation_date', 'cino')
    process_date = models.DateField(blank=True, null=True)
    process_id = models.CharField(max_length=20)
    process_messenger_type = models.CharField(max_length=50)
    bailiff_id = models.SmallIntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    other_court_name = models.CharField(max_length=250, blank=True, null=True)
    other_court_case_no = models.CharField(max_length=250, blank=True, null=True)
    allocation_date = models.DateField()
    returnable_date = models.DateField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'process_allocate'


class ProcessAreaT(models.Model):
    area_id = models.SmallIntegerField(primary_key=True)
    area = models.CharField(max_length=250, blank=True, null=True)
    larea = models.CharField(max_length=250, blank=True, null=True)
    district = models.SmallIntegerField()
    taluka = models.SmallIntegerField()
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'process_area_t'


class ProcessDelivery(models.Model):
    est_code = models.CharField(max_length=6, blank=True, null=True)
    process_id = models.CharField(primary_key=True, max_length=25)
    delivery_estcode = models.CharField(max_length=6, blank=True, null=True)
    delivery_estname = models.CharField(max_length=99, blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)
    served_not_or_served = models.TextField(blank=True, null=True)  # This field type is a guess.
    process_messenger_id = models.BigIntegerField(blank=True, null=True)
    process_messenger_name = models.CharField(max_length=250, blank=True, null=True)
    baliff_id = models.BigIntegerField(blank=True, null=True)
    bailiff_name = models.CharField(max_length=99, blank=True, null=True)
    reason_for_not_service_id = models.BigIntegerField(blank=True, null=True)
    reason_for_not_service = models.TextField(blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    field1 = models.BigIntegerField(blank=True, null=True)
    field2 = models.CharField(max_length=99, blank=True, null=True)
    field3 = models.CharField(max_length=250, blank=True, null=True)
    field4 = models.TextField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'process_delivery'


class ProcessMessengerT(models.Model):
    process_id = models.SmallIntegerField(primary_key=True)
    process_messenger = models.CharField(max_length=250, blank=True, null=True)
    lprocess_messenger = models.CharField(max_length=250, blank=True, null=True)
    contact_address = models.TextField(blank=True, null=True)
    lcontact_address = models.TextField(blank=True, null=True)
    contact_name = models.CharField(max_length=100, blank=True, null=True)
    lcontact_name = models.CharField(max_length=100, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.CharField(max_length=254, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'process_messenger_t'


class ProcessUnsuccessfulT(models.Model):
    unsuccessful_id = models.SmallIntegerField(primary_key=True)
    unsuccessful_name = models.CharField(max_length=250, blank=True, null=True)
    lunsuccessful_name = models.CharField(max_length=250, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'process_unsuccessful_t'


class PropertyDispT(models.Model):
    prop_code = models.BigIntegerField(primary_key=True)
    prop_name = models.CharField(max_length=50, blank=True, null=True)
    lprop_name = models.CharField(max_length=50, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'property_disp_t'


class PurposeT(models.Model):
    purpose_code = models.SmallIntegerField(primary_key=True)
    purpose_name = models.CharField(max_length=100, blank=True, null=True)
    lpurpose_name = models.CharField(max_length=100, blank=True, null=True)
    purpose_flag = models.SmallIntegerField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    purpose_priority = models.SmallIntegerField()
    res_disp = models.SmallIntegerField()
    national_code = models.BigIntegerField()
    substage_id = models.CharField(max_length=1000, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'purpose_t'


class RegisterT(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    regis_name = models.CharField(max_length=50, blank=True, null=True)
    lregis_name = models.CharField(max_length=50, blank=True, null=True)
    case_type = models.TextField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    appl_no = models.IntegerField()
    appl_year = models.SmallIntegerField()
    extra_amount = models.DecimalField(max_digits=17, decimal_places=2)
    amount_formula = models.TextField(blank=True, null=True)
    receipt_no = models.IntegerField()
    receipt_year = models.SmallIntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'register_t'


class RelationMaster(models.Model):
    relation_id = models.IntegerField(primary_key=True)
    relation_name = models.CharField(max_length=50, blank=True, null=True)
    lrelation_name = models.CharField(max_length=50, blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'relation_master'


class Religion(models.Model):
    religion_id = models.SmallIntegerField(primary_key=True)
    religion_name = models.CharField(max_length=100, blank=True, null=True)
    lreligion_name = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    national_code = models.BigIntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'religion'


class Restorerevoke(models.Model):
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    datefield = models.DateField(blank=True, null=True)
    datetype = models.CharField(max_length=50, blank=True, null=True)
    order_remark = models.TextField(blank=True, null=True)
    todays_date = models.DateField(blank=True, null=True)
    court_no = models.IntegerField(blank=True, null=True)
    exhibit = models.TextField(blank=True, null=True)
    lorder_remark = models.TextField(blank=True, null=True)
    lexhibit = models.TextField(blank=True, null=True)
    ia_no = models.CharField(max_length=12, blank=True, null=True)
    goshwara_no = models.SmallIntegerField()
    disp_nature = models.SmallIntegerField()
    jocode = models.CharField(max_length=150, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    next_date = models.DateField(blank=True, null=True)
    present = models.TextField(blank=True, null=True)
    lpresent = models.TextField(blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    desig_code = models.CharField(max_length=50, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    ref_order_ia_no = models.CharField(max_length=12, blank=True, null=True)
    ref_cino = models.CharField(max_length=16, blank=True, null=True)
    ref_order_ia_case_type = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'restorerevoke'


class ReturnProcess(models.Model):
    pk = models.CompositePrimaryKey('process_id', 'process_date', 'process_messenger_type', 'bailiff_id', 'cino')
    casecode = models.CharField(max_length=15)
    process_id = models.CharField(max_length=20)
    date_return = models.DateField(blank=True, null=True)
    result = models.TextField()  # This field type is a guess.
    unsuccessfulype = models.SmallIntegerField()
    process_date = models.DateField()
    process_messenger_type = models.SmallIntegerField()
    bailiff_id = models.SmallIntegerField()
    display = models.TextField()  # This field type is a guess.
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'return_process'


class RoasterChange(models.Model):
    roaster_id = models.IntegerField(primary_key=True)
    sitting_date = models.DateField(blank=True, null=True)
    source_benchid = models.IntegerField(blank=True, null=True)
    target_benchid = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'roaster_change'


class RoasterTrans(models.Model):
    pk = models.CompositePrimaryKey('roaster_id', 'cino')
    roaster_id = models.IntegerField()
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'roaster_trans'


class RosterBench(models.Model):
    pk = models.CompositePrimaryKey('bench_id', 'roster_bench_date')
    roster_id = models.CharField(max_length=100, blank=True, null=True)
    roster_heading = models.CharField(max_length=255, blank=True, null=True)
    bench_id = models.IntegerField()
    roster_bench_date = models.DateField()
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'roster_bench'


class RosterCreation(models.Model):
    roster_id = models.CharField(max_length=100, blank=True, null=True)
    from_date = models.DateField(primary_key=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    to_date = models.DateField(blank=True, null=True)
    rec_no = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'roster_creation'


class RosterSubject(models.Model):
    roster_id = models.IntegerField(primary_key=True)
    roster_subject = models.TextField(blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    case_types = models.CharField(max_length=255, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'roster_subject'


class RoznamaDetails(models.Model):
    pk = models.CompositePrimaryKey('roznama_dt', 'cino')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    roznama_dt = models.DateField()
    download = models.TextField()  # This field type is a guess.
    upload = models.TextField()  # This field type is a guess.
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'roznama_details'


class SalutationMaster(models.Model):
    salutation_id = models.IntegerField(primary_key=True)
    salutation_name = models.CharField(max_length=15, blank=True, null=True)
    lsalutation_name = models.CharField(max_length=15, blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'salutation_master'


class SectionT(models.Model):
    sectioncode = models.BigIntegerField(primary_key=True)
    section_name = models.CharField(max_length=100, blank=True, null=True)
    lsection_name = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'section_t'


class State(models.Model):
    state_id = models.SmallIntegerField(primary_key=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    lstate = models.CharField(max_length=100, blank=True, null=True)
    census = models.IntegerField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'state'


class StatusMaster(models.Model):
    status_id = models.IntegerField(primary_key=True)
    status_name = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    next_date = models.TextField(blank=True, null=True)  # This field type is a guess.
    afh = models.IntegerField(blank=True, null=True)
    status_priority = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'status_master'


class SubjectMaster(models.Model):
    subject_code = models.IntegerField(primary_key=True)
    subject_name = models.CharField(max_length=200, blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subject_master'


class Subnature1T(models.Model):
    pk = models.CompositePrimaryKey('case_type_cd', 'nature_cd', 'subnature1_cd')
    case_type_cd = models.IntegerField()
    nature_cd = models.IntegerField()
    subnature1_cd = models.IntegerField()
    subnature1_desc = models.CharField(max_length=255, blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subnature1_t'


class Subnature2T(models.Model):
    pk = models.CompositePrimaryKey('case_type_cd', 'nature_cd', 'subnature1_cd', 'subnature2_cd')
    case_type_cd = models.IntegerField()
    nature_cd = models.IntegerField()
    subnature1_cd = models.IntegerField()
    subnature2_cd = models.IntegerField()
    subnature2_desc = models.CharField(max_length=255, blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subnature2_t'


class Subnature3T(models.Model):
    pk = models.CompositePrimaryKey('case_type_cd', 'nature_cd', 'subnature1_cd', 'subnature2_cd', 'subnature3_cd')
    case_type_cd = models.IntegerField()
    nature_cd = models.IntegerField()
    subnature1_cd = models.IntegerField()
    subnature2_cd = models.IntegerField()
    subnature3_cd = models.IntegerField()
    subnature3_desc = models.CharField(max_length=255, blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subnature3_t'


class SubpurposeT(models.Model):
    pk = models.CompositePrimaryKey('purpose_id', 'subpurpose_id')
    purpose_id = models.SmallIntegerField()
    subpurpose_id = models.SmallIntegerField()
    sub_purpose = models.CharField(max_length=150, blank=True, null=True)
    lsub_purpose = models.CharField(max_length=150, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    national_code = models.IntegerField()
    subpurpose_priority = models.SmallIntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subpurpose_t'


class SuitSchedule(models.Model):
    pk = models.CompositePrimaryKey('schedule_id', 'case_no')
    case_no = models.CharField(max_length=15)
    schedule_name = models.CharField(max_length=255, blank=True, null=True)
    schedule_id = models.SmallIntegerField()
    display = models.TextField()  # This field type is a guess.
    cino = models.CharField(max_length=16, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'suit_schedule'


class SummonsT(models.Model):
    summonscode = models.SmallIntegerField(primary_key=True)
    summons_title = models.CharField(max_length=255, blank=True, null=True)
    lsummons_title = models.CharField(max_length=255, blank=True, null=True)
    summon_detail = models.TextField(blank=True, null=True)
    lsummon_detail = models.TextField(blank=True, null=True)
    file_name = models.CharField(max_length=50, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    national_code = models.BigIntegerField(blank=True, null=True)
    label1 = models.CharField(max_length=150, blank=True, null=True)
    label2 = models.CharField(max_length=150, blank=True, null=True)
    label3 = models.CharField(max_length=150, blank=True, null=True)
    label4 = models.CharField(max_length=150, blank=True, null=True)
    label5 = models.CharField(max_length=150, blank=True, null=True)
    label1mar = models.CharField(max_length=150, blank=True, null=True)
    label2mar = models.CharField(max_length=150, blank=True, null=True)
    label3mar = models.CharField(max_length=150, blank=True, null=True)
    label4mar = models.CharField(max_length=150, blank=True, null=True)
    label5mar = models.CharField(max_length=150, blank=True, null=True)
    summons_priority = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'summons_t'


class SuretyType(models.Model):
    surety_id = models.SmallIntegerField(primary_key=True)
    surety_type = models.CharField(max_length=100, blank=True, null=True)
    lsurety_type = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'surety_type'


class TakenOnBoard(models.Model):
    pk = models.CompositePrimaryKey('cino', 'sr_no')
    cino = models.CharField(max_length=16)
    sr_no = models.IntegerField()
    linkid = models.IntegerField(blank=True, null=True)
    old_next_date = models.DateField(blank=True, null=True)
    old_purpose_code = models.SmallIntegerField(blank=True, null=True)
    new_next_date = models.DateField(blank=True, null=True)
    new_purpose_code = models.SmallIntegerField(blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    users = models.CharField(max_length=100, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    ia_no = models.CharField(max_length=12, blank=True, null=True)
    ia_case_type = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'taken_on_board'


class TalukaT(models.Model):
    pk = models.CompositePrimaryKey('state_id', 'taluka_code', 'dist_code')
    taluka_code = models.SmallIntegerField()
    taluka_name = models.CharField(max_length=150, blank=True, null=True)
    dist_code = models.SmallIntegerField()
    ltaluka_name = models.CharField(max_length=150, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    national_code = models.BigIntegerField(blank=True, null=True)
    state_id = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'taluka_t'


class TargetT(models.Model):
    pk = models.CompositePrimaryKey('tarnext_date', 'tarpurpose_code', 'cino')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    tarnext_date = models.DateField()
    tarpurpose_code = models.SmallIntegerField()
    court_no = models.IntegerField()
    deleted = models.TextField()  # This field type is a guess.
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'target_t'


class Temptransfer(models.Model):
    pk = models.CompositePrimaryKey('srno', 'casetype', 'caseyear', 'cino')
    srno = models.SmallIntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    fromcourt_no = models.SmallIntegerField()
    tocourtno = models.SmallIntegerField()
    casetype = models.BigIntegerField()
    caseyear = models.SmallIntegerField()
    checkuncheck = models.SmallIntegerField()
    not_before_me = models.CharField(max_length=50, blank=True, null=True)
    before_me = models.CharField(max_length=50, blank=True, null=True)
    fromdate = models.DateField(blank=True, null=True)
    todate = models.DateField(blank=True, null=True)
    userlogin = models.CharField(max_length=150, blank=True, null=True)
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'temptransfer'


class TimeTableMaster(models.Model):
    auto_number = models.BigIntegerField(primary_key=True)
    case_type_id = models.SmallIntegerField()
    stage_id = models.SmallIntegerField()
    sequence_id = models.SmallIntegerField()
    no_of_days = models.IntegerField()
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'time_table_master'


class TimeTableTransaction(models.Model):
    pk = models.CompositePrimaryKey('sequence_id', 'cino')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    sequence_id = models.SmallIntegerField()
    stage_id = models.SmallIntegerField()
    my_date = models.DateField(blank=True, null=True)
    cino = models.CharField(max_length=16)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'time_table_transaction'


class Timeslot(models.Model):
    timeslot_id = models.SmallIntegerField(primary_key=True)
    timeslot = models.CharField(max_length=50, blank=True, null=True)
    time_slot_name = models.CharField(max_length=50, blank=True, null=True)
    ltime_slot_name = models.CharField(max_length=50, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'timeslot'


class TownT(models.Model):
    pk = models.CompositePrimaryKey('state_id', 'district_code', 'town_code')
    district_code = models.SmallIntegerField()
    town_code = models.SmallIntegerField()
    town_name = models.CharField(max_length=50, blank=True, null=True)
    ltown_name = models.CharField(max_length=50, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    national_code = models.BigIntegerField(blank=True, null=True)
    state_id = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'town_t'


class TrafficopCourtT(models.Model):
    sr_no = models.BigIntegerField(primary_key=True)
    accused_name = models.CharField(max_length=100, blank=True, null=True)
    sex = models.CharField(max_length=1, blank=True, null=True)
    age = models.SmallIntegerField()
    address = models.TextField(blank=True, null=True)
    police_station = models.CharField(max_length=150, blank=True, null=True)
    fir_no = models.CharField(max_length=15, blank=True, null=True)
    fir_year = models.SmallIntegerField()
    offence_date = models.DateField(blank=True, null=True)
    no_of_previousoffence = models.SmallIntegerField()
    previous_offence_details = models.CharField(max_length=150, blank=True, null=True)
    vechicle_no = models.CharField(max_length=100, blank=True, null=True)
    license_no = models.CharField(max_length=100, blank=True, null=True)
    act1 = models.BigIntegerField()
    sec1 = models.CharField(max_length=100, blank=True, null=True)
    act2 = models.BigIntegerField()
    sec2 = models.CharField(max_length=100, blank=True, null=True)
    act3 = models.BigIntegerField()
    sec3 = models.CharField(max_length=100, blank=True, null=True)
    act4 = models.BigIntegerField()
    sec4 = models.CharField(max_length=100, blank=True, null=True)
    act5 = models.BigIntegerField()
    sec5 = models.CharField(max_length=100, blank=True, null=True)
    remarks = models.CharField(max_length=150, blank=True, null=True)
    dateofreceive = models.DateField(blank=True, null=True)
    copiedtocis = models.CharField(max_length=1)
    gender = models.CharField(max_length=1, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trafficop_court_t'


class TrialJudge(models.Model):
    judge_code = models.SmallIntegerField(primary_key=True)
    jocode = models.CharField(max_length=7, blank=True, null=True)
    judge_name = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'trial_judge'


class TrialLowerCourt(models.Model):
    pk = models.CompositePrimaryKey('cino', 'lower_trial')
    lower_court_code = models.SmallIntegerField(blank=True, null=True)
    lower_court = models.CharField(max_length=40, blank=True, null=True)
    lower_court_dec_dt = models.DateField(blank=True, null=True)
    lcc_applied_date = models.DateField(blank=True, null=True)
    lcc_received_date = models.DateField(blank=True, null=True)
    lower_cino = models.CharField(max_length=16, blank=True, null=True)
    lower_judge_name = models.CharField(max_length=100, blank=True, null=True)
    lower_dist_code = models.IntegerField(blank=True, null=True)
    lregis_date = models.DateField(blank=True, null=True)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    cino = models.CharField(max_length=16)
    lowerjocode = models.CharField(max_length=150, blank=True, null=True)
    filing_case = models.IntegerField(blank=True, null=True)
    lower_taluka_code = models.IntegerField(blank=True, null=True)
    lower_state_id = models.IntegerField(blank=True, null=True)
    lower_trial = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    qjnumber = models.CharField(max_length=255, blank=True, null=True)
    case_ref_no = models.CharField(max_length=15, blank=True, null=True)
    ljudid = models.IntegerField(blank=True, null=True)
    judg_local_lang = models.TextField(blank=True, null=True)  # This field type is a guess.
    langflag = models.TextField(blank=True, null=True)  # This field type is a guess.
    oagainst = models.CharField(max_length=1, blank=True, null=True)
    date_of_order = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trial_lower_court'


class UnderTrial(models.Model):
    case_no = models.CharField(max_length=15, blank=True, null=True)
    pet_res = models.CharField(max_length=99, blank=True, null=True)
    lpet_res = models.CharField(max_length=99, blank=True, null=True)
    arrest_date = models.DateField(blank=True, null=True)
    bail_date = models.DateField(blank=True, null=True)
    custody_type = models.CharField(max_length=1, blank=True, null=True)
    name1 = models.CharField(max_length=100, blank=True, null=True)
    lname1 = models.CharField(max_length=100, blank=True, null=True)
    amount1 = models.DecimalField(max_digits=17, decimal_places=2)
    property1 = models.CharField(max_length=255, blank=True, null=True)
    lproperty1 = models.CharField(max_length=250, blank=True, null=True)
    name2 = models.CharField(max_length=100, blank=True, null=True)
    lname2 = models.CharField(max_length=100, blank=True, null=True)
    amount2 = models.DecimalField(max_digits=17, decimal_places=2)
    property2 = models.CharField(max_length=255, blank=True, null=True)
    lproperty2 = models.CharField(max_length=250, blank=True, null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    prison_id = models.SmallIntegerField()
    landphone1 = models.CharField(max_length=15, blank=True, null=True)
    landphone2 = models.CharField(max_length=15, blank=True, null=True)
    age1 = models.SmallIntegerField()
    age2 = models.SmallIntegerField()
    mobile1 = models.CharField(max_length=15, blank=True, null=True)
    mobile2 = models.CharField(max_length=15, blank=True, null=True)
    address1 = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    street1 = models.CharField(max_length=100, blank=True, null=True)
    street2 = models.CharField(max_length=100, blank=True, null=True)
    pincode1 = models.IntegerField()
    pincode2 = models.IntegerField()
    dist_code1 = models.SmallIntegerField()
    dist_code2 = models.SmallIntegerField()
    taluka_code1 = models.SmallIntegerField()
    taluka_code2 = models.SmallIntegerField()
    hobli1 = models.IntegerField()
    hobli2 = models.IntegerField()
    hamlet1 = models.IntegerField()
    hamlet2 = models.BigIntegerField()
    village_code1 = models.IntegerField()
    village_code2 = models.IntegerField()
    town_code1 = models.IntegerField()
    town_code2 = models.BigIntegerField()
    ward_code1 = models.IntegerField()
    ward_code2 = models.IntegerField()
    father_name1 = models.CharField(max_length=100, blank=True, null=True)
    father_name2 = models.CharField(max_length=100, blank=True, null=True)
    org_name1 = models.CharField(max_length=100, blank=True, null=True)
    org_name2 = models.CharField(max_length=100, blank=True, null=True)
    uid1 = models.BigIntegerField()
    uid2 = models.BigIntegerField()
    release_date = models.DateField(blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    state_id1 = models.IntegerField(blank=True, null=True)
    state_id2 = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    max_act_national_code = models.CharField(max_length=15, blank=True, null=True)
    max_section = models.CharField(max_length=100, blank=True, null=True)
    max_imprisonment = models.IntegerField(blank=True, null=True)
    life_death = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'under_trial'


class UnittypeclsT(models.Model):
    unitcls_code = models.BigIntegerField(primary_key=True)
    unitcls_name = models.CharField(max_length=99, blank=True, null=True)
    lunitcls_name = models.CharField(max_length=99, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'unittypecls_t'


class UnittypedisposalT(models.Model):
    pk = models.CompositePrimaryKey('case_type_cd', 'unit_cd')
    case_type_cd = models.SmallIntegerField()
    unit_cd = models.SmallIntegerField()
    unit_desc = models.CharField(max_length=100, blank=True, null=True)
    lunit_desc = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    units = models.DecimalField(max_digits=17, decimal_places=2)
    unitflag = models.SmallIntegerField()
    nature_code = models.SmallIntegerField()
    unit_type = models.SmallIntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'unittypedisposal_t'


class UnlinkLog(models.Model):
    pk = models.CompositePrimaryKey('cino', 'unlink_date')
    cino = models.CharField(max_length=16)
    case_no = models.CharField(max_length=15)
    link_code = models.CharField(max_length=15, blank=True, null=True)
    flink_id = models.IntegerField(blank=True, null=True)
    unlink_date = models.DateTimeField()
    unlink_flag = models.TextField(blank=True, null=True)  # This field type is a guess.
    newlink_code = models.CharField(max_length=15, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'unlink_log'


class UrgordT(models.Model):
    registercode = models.SmallIntegerField(primary_key=True)
    urgentrate = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    ordinaryrate = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    appearance_days = models.SmallIntegerField()
    appearance_days_urgent = models.SmallIntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'urgord_t'


class UserDesig(models.Model):
    pk = models.CompositePrimaryKey('user_code', 'sr_no')
    user_code = models.IntegerField()
    user_name = models.CharField(max_length=100, blank=True, null=True)
    sr_no = models.IntegerField()
    branch_code = models.IntegerField(blank=True, null=True)
    desig_code = models.IntegerField(blank=True, null=True)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    reporting_user_code = models.IntegerField(blank=True, null=True)
    reporting_user_name = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    inward_user = models.TextField(blank=True, null=True)  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_desig'


class UserRole(models.Model):
    user_id = models.SmallIntegerField(primary_key=True)
    user_role = models.CharField(max_length=50, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_role'


class UserT(models.Model):
    pk = models.CompositePrimaryKey('user_login', 'type_of_user')
    user_name = models.CharField(max_length=50, blank=True, null=True)
    luser_name = models.CharField(max_length=50, blank=True, null=True)
    user_login = models.CharField(max_length=20)
    pass_word = models.CharField(max_length=100, blank=True, null=True)
    type_of_user = models.CharField(max_length=40)
    court_no = models.IntegerField()
    case_no = models.CharField(max_length=15, blank=True, null=True)
    link_name = models.CharField(max_length=15, blank=True, null=True)
    extracourts = models.CharField(max_length=255, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    logint = models.DateTimeField(blank=True, null=True)
    logoutt = models.DateTimeField(blank=True, null=True)
    sessionid = models.CharField(max_length=50, blank=True, null=True)
    dt_create = models.DateField(blank=True, null=True)
    acclock = models.CharField(max_length=10, blank=True, null=True)
    times = models.SmallIntegerField()
    singlesignon = models.CharField(max_length=150, blank=True, null=True)
    allest = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_t'


class UtypeLink(models.Model):
    pk = models.CompositePrimaryKey('utype', 'linkid')
    tab_id = models.CharField(max_length=255, blank=True, null=True)
    amd = models.CharField(max_length=20, blank=True, null=True)
    utype = models.IntegerField()
    linkid = models.IntegerField()
    mode_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'utype_link'


class VictimT(models.Model):
    pk = models.CompositePrimaryKey('party_no', 'cino')
    party_no = models.SmallIntegerField()
    filing_no = models.CharField(max_length=15, blank=True, null=True)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    orgid = models.SmallIntegerField()
    name = models.CharField(max_length=100, blank=True, null=True)
    lname = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    altaddress = models.TextField(blank=True, null=True)
    altladdress = models.TextField(blank=True, null=True)
    pet_age = models.SmallIntegerField()
    father_name = models.CharField(max_length=100, blank=True, null=True)
    lfather_name = models.CharField(max_length=100, blank=True, null=True)
    father_flag = models.CharField(max_length=2)
    pet_caste = models.SmallIntegerField(blank=True, null=True)
    type = models.SmallIntegerField()
    adv_name = models.CharField(max_length=100, blank=True, null=True)
    ladv_name = models.CharField(max_length=100, blank=True, null=True)
    adv_cd = models.BigIntegerField()
    pet_occu = models.CharField(max_length=30, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    legal_heir = models.TextField()  # This field type is a guess.
    pet_nationality = models.CharField(max_length=99, blank=True, null=True)
    pet_email = models.CharField(max_length=254, blank=True, null=True)
    pet_mobile = models.CharField(max_length=15, blank=True, null=True)
    pet_phone = models.CharField(max_length=15, blank=True, null=True)
    pet_fax = models.CharField(max_length=15, blank=True, null=True)
    parentid = models.SmallIntegerField()
    pet_sex = models.CharField(max_length=1, blank=True, null=True)
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    altdist_code = models.SmallIntegerField()
    alttaluka_code = models.SmallIntegerField()
    altvillage_code = models.IntegerField()
    altvillage1_code = models.IntegerField()
    altvillage2_code = models.IntegerField()
    alttown_code = models.IntegerField()
    altward_code = models.IntegerField()
    passportno = models.CharField(max_length=25, blank=True, null=True)
    pincode = models.IntegerField(blank=True, null=True)
    country = models.CharField(max_length=99, blank=True, null=True)
    uid_no = models.BigIntegerField(blank=True, null=True)
    cino = models.CharField(max_length=16)
    pet_gender = models.CharField(max_length=1, blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    altstate_id = models.IntegerField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    category = models.CharField(max_length=2, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'victim_t'


class Village1T(models.Model):
    pk = models.CompositePrimaryKey('state_id', 'dist_code', 'taluka_code', 'village_code', 'village1_code')
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village1_name = models.CharField(max_length=50, blank=True, null=True)
    lvillage1_name = models.CharField(max_length=50, blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    national_code = models.BigIntegerField(blank=True, null=True)
    state_id = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'village1_t'


class Village2T(models.Model):
    pk = models.CompositePrimaryKey('state_id', 'dist_code', 'taluka_code', 'village_code', 'village1_code', 'village2_code')
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    village2_name = models.CharField(max_length=50, blank=True, null=True)
    lvillage2_name = models.CharField(max_length=50, blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    national_code = models.BigIntegerField(blank=True, null=True)
    state_id = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'village2_t'


class VillageT(models.Model):
    pk = models.CompositePrimaryKey('state_id', 'dist_code', 'taluka_code', 'village_code')
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village_name = models.CharField(max_length=50, blank=True, null=True)
    lvillage_name = models.CharField(max_length=50, blank=True, null=True)
    village_census_code = models.CharField(max_length=50, blank=True, null=True)
    display = models.TextField(blank=True, null=True)  # This field type is a guess.
    national_code = models.BigIntegerField(blank=True, null=True)
    state_id = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'village_t'


class WardT(models.Model):
    pk = models.CompositePrimaryKey('state_id', 'district_code', 'town_code', 'ward_code')
    district_code = models.SmallIntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    ward_name = models.CharField(max_length=99, blank=True, null=True)
    lward_name = models.CharField(max_length=99, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    national_code = models.BigIntegerField(blank=True, null=True)
    state_id = models.IntegerField()
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'ward_t'


class WarnList(models.Model):
    pk = models.CompositePrimaryKey('warnlist_type', 'warnlist_date', 'cino')
    sr_no = models.IntegerField()
    cino = models.CharField(max_length=16)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    next_date = models.DateField(blank=True, null=True)
    court_no = models.IntegerField()
    ctype = models.CharField(max_length=1)
    originalsr_no = models.IntegerField(blank=True, null=True)
    case_remark = models.TextField(blank=True, null=True)
    warnlist_type = models.IntegerField()
    warnlist_period = models.CharField(max_length=1, blank=True, null=True)
    list_from_date = models.DateField(blank=True, null=True)
    list_to_date = models.DateField(blank=True, null=True)
    warnlist_date = models.DateField()
    reg_dt = models.DateField(blank=True, null=True)
    filing_dt = models.DateField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'warn_list'


class WarnListA(models.Model):
    pk = models.CompositePrimaryKey('warnlist_type', 'warnlist_date', 'cino')
    sr_no = models.IntegerField()
    cino = models.CharField(max_length=16)
    case_no = models.CharField(max_length=15, blank=True, null=True)
    next_date = models.DateField(blank=True, null=True)
    court_no = models.IntegerField()
    ctype = models.CharField(max_length=1)
    originalsr_no = models.IntegerField(blank=True, null=True)
    case_remark = models.TextField(blank=True, null=True)
    warnlist_type = models.IntegerField()
    warnlist_period = models.CharField(max_length=1, blank=True, null=True)
    list_from_date = models.DateField(blank=True, null=True)
    list_to_date = models.DateField(blank=True, null=True)
    warnlist_date = models.DateField()
    reg_dt = models.DateField(blank=True, null=True)
    filing_dt = models.DateField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'warn_list_a'


class WarnlistTitle(models.Model):
    pk = models.CompositePrimaryKey('warnlist_id', 'warnlist_date')
    bench_id = models.IntegerField(blank=True, null=True)
    warnlist_id = models.IntegerField()
    warnlist_date = models.DateField()
    wheader = models.TextField(blank=True, null=True)
    wfooter = models.TextField(blank=True, null=True)
    published = models.TextField(blank=True, null=True)  # This field type is a guess.
    published_date = models.DateField(blank=True, null=True)
    archive = models.CharField(max_length=1, blank=True, null=True)
    published_ip = models.CharField(max_length=99, blank=True, null=True)
    published_user = models.CharField(max_length=99, blank=True, null=True)
    prepared = models.CharField(max_length=1, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'warnlist_title'


class WitnessInfoT(models.Model):
    pk = models.CompositePrimaryKey('witness_no', 'witness_flag', 'cino')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    court_no = models.IntegerField()
    witness_no = models.SmallIntegerField()
    witness_name = models.CharField(max_length=100, blank=True, null=True)
    witness_flag = models.SmallIntegerField()
    occupation = models.TextField(blank=True, null=True)
    lfather_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    witness_language = models.CharField(max_length=100, blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    date_of_examination = models.DateField(blank=True, null=True)
    age = models.SmallIntegerField()
    dist_code = models.SmallIntegerField()
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    father_name = models.CharField(max_length=100, blank=True, null=True)
    loccupation = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=254, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    father_flag = models.CharField(max_length=2)
    pincode = models.IntegerField(blank=True, null=True)
    uid_no = models.BigIntegerField(blank=True, null=True)
    party_no = models.CharField(max_length=10, blank=True, null=True)
    cino = models.CharField(max_length=16)
    state_id = models.IntegerField(blank=True, null=True)
    org_id = models.IntegerField()
    hod_name = models.CharField(max_length=99, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'witness_info_t'


class WitnessT(models.Model):
    pk = models.CompositePrimaryKey('name', 'summon_id', 'notice_id', 'process_id', 'cino')
    case_no = models.CharField(max_length=15, blank=True, null=True)
    w_courtno = models.SmallIntegerField()
    name = models.CharField(max_length=100)
    fathername = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    address_type = models.TextField()  # This field type is a guess.
    next_date = models.DateField(blank=True, null=True)
    purpose_code = models.SmallIntegerField()
    summon_id = models.SmallIntegerField()
    notice_id = models.SmallIntegerField()
    ns_date = models.DateField(blank=True, null=True)
    w_district = models.SmallIntegerField()
    w_taluka = models.SmallIntegerField()
    w_village = models.IntegerField()
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    w_email = models.CharField(max_length=254, blank=True, null=True)
    w_mobile = models.CharField(max_length=15, blank=True, null=True)
    w_pincode = models.CharField(max_length=15, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    process_id = models.IntegerField()
    party_type = models.SmallIntegerField()
    process_fees = models.IntegerField()
    fees_type = models.CharField(max_length=1, blank=True, null=True)
    receipt_no = models.CharField(max_length=50, blank=True, null=True)
    receipt_year = models.CharField(max_length=50, blank=True, null=True)
    receipt_dates = models.CharField(max_length=255, blank=True, null=True)
    fee = models.CharField(max_length=100, blank=True, null=True)
    date_of_decision = models.DateField(blank=True, null=True)
    police_st_code = models.IntegerField()
    pet_adv = models.CharField(max_length=99, blank=True, null=True)
    res_adv = models.CharField(max_length=99, blank=True, null=True)
    fir_no = models.CharField(max_length=15, blank=True, null=True)
    fir_year = models.SmallIntegerField()
    relief_offense = models.TextField(blank=True, null=True)
    receiver_adv = models.CharField(max_length=99, blank=True, null=True)
    receiver_age = models.SmallIntegerField()
    previous_hearing_date = models.DateField(blank=True, null=True)
    causeofaction = models.TextField(blank=True, null=True)
    party_witness = models.CharField(max_length=99, blank=True, null=True)
    court_process_id = models.SmallIntegerField()
    type = models.CharField(max_length=1, blank=True, null=True)
    jocode = models.CharField(max_length=150, blank=True, null=True)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    party_no = models.SmallIntegerField()
    witness_no = models.SmallIntegerField()
    lname = models.CharField(max_length=100, blank=True, null=True)
    lfathername = models.CharField(max_length=100, blank=True, null=True)
    laddress = models.TextField(blank=True, null=True)
    lpet_adv = models.CharField(max_length=99, blank=True, null=True)
    pet_adv_cd = models.BigIntegerField()
    lres_adv = models.CharField(max_length=99, blank=True, null=True)
    res_adv_cd = models.BigIntegerField()
    lreceiver_adv = models.CharField(max_length=99, blank=True, null=True)
    receiver_adv_cd = models.BigIntegerField()
    cino = models.CharField(max_length=16)
    w_state_id = models.IntegerField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'witness_t'


class Writ(models.Model):
    writ_code = models.SmallIntegerField(primary_key=True)
    writ_name = models.CharField(max_length=100, blank=True, null=True)
    lwrit_name = models.CharField(max_length=100, blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'writ'


class WritT(models.Model):
    case_no = models.CharField(max_length=15, blank=True, null=True)
    app_case_no = models.CharField(max_length=50, blank=True, null=True)
    app_authority = models.CharField(max_length=50, blank=True, null=True)
    lapp_authority = models.CharField(max_length=50, blank=True, null=True)
    date_of_receipt = models.DateField(blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)
    stay_upto = models.DateField(blank=True, null=True)
    stay_vacated_date = models.DateField(blank=True, null=True)
    party_type = models.CharField(max_length=5, blank=True, null=True)
    party_id = models.SmallIntegerField()
    order_code = models.TextField(blank=True, null=True)
    lorder_code = models.TextField(blank=True, null=True)
    comp_date = models.DateField(blank=True, null=True)
    stayed = models.TextField()  # This field type is a guess.
    display = models.TextField()  # This field type is a guess.
    action = models.TextField(blank=True, null=True)
    laction = models.CharField(max_length=200, blank=True, null=True)
    app_auth_code = models.SmallIntegerField()
    writ_code = models.SmallIntegerField()
    apl_court_srno = models.SmallIntegerField()
    certifed_date = models.DateField(blank=True, null=True)
    dispatch_no = models.IntegerField()
    judge_name = models.CharField(max_length=100, blank=True, null=True)
    ljudge_name = models.CharField(max_length=100, blank=True, null=True)
    cino = models.CharField(max_length=16, blank=True, null=True)
    srno = models.AutoField(primary_key=True)
    lower_court = models.CharField(max_length=15, blank=True, null=True)
    date_of_dispatch = models.DateField(blank=True, null=True)
    outward_no = models.CharField(max_length=50, blank=True, null=True)
    app_pet_party = models.CharField(max_length=100, blank=True, null=True)
    lapp_pet_party = models.CharField(max_length=100, blank=True, null=True)
    app_res_party = models.CharField(max_length=100, blank=True, null=True)
    lapp_res_party = models.CharField(max_length=100, blank=True, null=True)
    recordoncall = models.TextField(blank=True, null=True)  # This field type is a guess.
    stayed_fromdt = models.DateField(blank=True, null=True)
    stayed_todt = models.DateField(blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'writ_t'


class Zone(models.Model):
    dcode = models.IntegerField()
    zonecode = models.IntegerField()
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    usercode = models.IntegerField(blank=True, null=True)
    ent_dt = models.DateField(blank=True, null=True)
    display = models.CharField(max_length=1)
    srno = models.AutoField(primary_key=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'zone'
