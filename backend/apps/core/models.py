
from django.db import IntegrityError, models, transaction
from django.utils import timezone

# Create your models here.
from apps.accounts.models import User
from apps.core.audit_context import get_current_user

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_updated')
    is_active = models.BooleanField(default=True)

    def _capture_original_audit_state(self) -> None:
        """Snapshot audit FK ids for save() logic. Safe for deferred fields."""
        self._original_created_by_id = self.created_by_id
        self._original_updated_by_id = self.updated_by_id

    def save(self, *args, **kwargs):
        acting_user = get_current_user()
        is_create = self._state.adding

        # Deferred-field safe: touching created_by_id / updated_by_id in __init__ can recurse
        # on Django 6+ (descriptor refresh_from_db → from_db → __init__).
        if not is_create and not hasattr(self, "_original_updated_by_id"):
            self._capture_original_audit_state()

        if acting_user is not None:
            if is_create:
                if self.created_by_id is None:
                    self.created_by = acting_user
                if self.updated_by_id is None:
                    self.updated_by = acting_user
            elif self.updated_by_id == getattr(self, "_original_updated_by_id", None):
                self.updated_by = acting_user

        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            update_fields = set(update_fields)
            if not is_create:
                update_fields.add("updated_at")
                if acting_user is not None:
                    update_fields.add("updated_by")
            kwargs["update_fields"] = update_fields

        super().save(*args, **kwargs)
        self._capture_original_audit_state()

    class Meta:
        abstract = True 


# class CISFilingNumber(BaseModel):
#     """
#     Represents a filing number issued by CIS 1.0 after scrutiny acceptance.
#     This model tracks the EC-prefixed filing number linked to accepted e-filings.
#     """

#     case_number = models.CharField(
#         max_length=100,
#         unique=True,
#         verbose_name="Case number (CIS filing number)",
#         help_text="e.g., EC_SKNM01/2026/12345",
#     )
#     case_title = models.CharField(
#         max_length=500,
#         verbose_name="Case title from CIS",
#     )
#     case_type = models.CharField(
#         max_length=50,
#         verbose_name="Case type from CIS",
#     )
#     petitioner = models.CharField(
#         max_length=300,
#         verbose_name="Petitioner name from CIS",
#     )
#     respondent = models.CharField(
#         max_length=300,
#         verbose_name="Respondent name from CIS",
#     )
#     filing_date = models.DateField(
#         verbose_name="Filing date in CIS",
#         null=True,
#         blank=True,
#     )
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name="Created at",
#     )

#     class Meta:
#         verbose_name = "CIS Filing Number"
#         verbose_name_plural = "CIS Filing Numbers"
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"{self.case_number} - {self.case_title}"


# class CISDataLog(BaseModel):
#     """
#     Audit log for all data transactions between CMS and CIS 1.0.
#     Tracks successful and failed data consuming operations.
#     """

#     class Status(models.TextChoices):
#         SUCCESS = "SUCCESS", "Success"
#         FAILED = "FAILED", "Failed"
#         PENDING = "PENDING", "Pending"

#     operation = models.CharField(
#         max_length=100,
#         verbose_name="Operation type",
#         help_text="e.g., FILING_NUMBER_GENERATION, DATA_SYNC",
#     )
#     status = models.CharField(
#         max_length=20,
#         choices=Status.choices,
#         default=Status.PENDING,
#         verbose_name="Status",
#     )
#     source_case_id = models.CharField(
#         max_length=100,
#         verbose_name="Source case ID (from CMS)",
#     )
#     target_case_number = models.CharField(
#         max_length=100,
#         verbose_name="Target case number (from CIS)",
#         null=True,
#         blank=True,
#     )
#     payload = models.JSONField(
#         verbose_name="Payload sent",
#         null=True,
#         blank=True,
#     )
#     response = models.JSONField(
#         verbose_name="Response received",
#         null=True,
#         blank=True,
#     )
#     error_message = models.TextField(
#         verbose_name="Error message",
#         null=True,
#         blank=True,
#     )
#     timestamp = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name="Timestamp",
#     )

#     class Meta:
#         verbose_name = "CIS Data Log"
#         verbose_name_plural = "CIS Data Logs"
#         ordering = ["-timestamp"]

#     def __str__(self):
#         return f"{self.operation} - {self.status} ({self.timestamp})"
    

class CaseTypeT(BaseModel):
    case_type = models.SmallIntegerField()
    type_name = models.CharField(max_length=50, blank=True, null=True)
    ltype_name = models.CharField(max_length=50, blank=True, null=True)
    full_form = models.CharField(max_length=100, blank=True, null=True)
    lfull_form = models.CharField(max_length=100, blank=True, null=True)
    type_flag = models.TextField()  # This field type is a guess.
    est_code_src = models.CharField(max_length=6)
    reg_no = models.IntegerField()
    reg_year = models.SmallIntegerField()

    class Meta:
      
        db_table = 'case_type_t'


class State(BaseModel):
    state = models.CharField(max_length=100, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)
    national_code = models.CharField(max_length=15, blank=True, null=True)
    class Meta:
      
        db_table = 'state'

class District(BaseModel):
    state_id = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='districts')
    district = models.CharField(max_length=100, blank=True, null=True)
    natinal_code = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
       
        db_table = 'district'

class Court(BaseModel):
    court_name = models.CharField(max_length=500, blank=True, null=True)
    address= models.CharField(max_length=255, blank=True, null=True)
    est_code_src = models.CharField(max_length=6)
    class Meta:
       
        db_table = 'court'

class OrgtypeT(BaseModel):
    orgtype = models.CharField(max_length=100, blank=True, null=True)
    national_code = models.CharField(max_length=15, blank=True, null=True)
   
    class Meta:
       
        db_table = 'orgtype_t'


class ActT(BaseModel):

    actcode = models.BigIntegerField(primary_key=True)
    actname = models.CharField(max_length=250, blank=True, null=True)
    lactname = models.CharField(max_length=250, blank=True, null=True)
    acttype = models.TextField()  # This field type is a guess.
    display = models.TextField()  # This field type is a guess.
    national_code = models.CharField(max_length=15, blank=True, null=True)
    shortact = models.CharField(max_length=50, blank=True, null=True)
    amd = models.CharField(max_length=1, blank=True, null=True)
    create_modify = models.DateTimeField(blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
        db_table = 'act_t'


class OrgnameT(BaseModel):
    orgtype=models.ForeignKey(OrgtypeT, on_delete=models.SET_NULL, null=True, blank=True, related_name='orgnames')
    orgname = models.CharField(max_length=100, blank=True, null=True)
    contactperson = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    state_id = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='orgnames')  
    district_id = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='orgnames')
    taluka_code = models.SmallIntegerField()
    village_code = models.IntegerField()
    email = models.CharField(max_length=254, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    fax = models.CharField(max_length=15, blank=True, null=True)
    village1_code = models.IntegerField()
    village2_code = models.IntegerField()
    town_code = models.IntegerField()
    ward_code = models.IntegerField()
    national_code = models.CharField(max_length=15, blank=True, null=True)
    est_code_src = models.CharField(max_length=6)

    class Meta:
      
        db_table = 'orgname_t'

class EfilingSequence(models.Model):
    year = models.IntegerField(unique=True)  # one row per year
    last_sequence = models.IntegerField(default=0)

    class Meta:
        db_table = "e_filing_sequence"
        
class IAfilingSequence(models.Model):
    year = models.IntegerField(unique=True)  # one row per year
    last_sequence = models.IntegerField(default=0)

    class Meta:
        db_table = "ia_filing_sequence"

class Efiling(BaseModel):
    case_type= models.ForeignKey(CaseTypeT, on_delete=models.SET_NULL, null=True, blank=True, related_name='efilings')
    bench = models.CharField(max_length=200, blank=True, null=True)
    petitioner_name = models.CharField(max_length=300, blank=True, null=True)
    petitioner_vs_respondent = models.CharField(max_length=600, blank=True, null=True)
    petitioner_contact = models.CharField(max_length=10, blank=True, null=True)
    e_filing_number = models.CharField(max_length=100, unique=True, blank=True, null=True) # Should be genrated at last submission step and should be unique.
    filing_date = models.DateField(blank=True, null=True)
    case_number = models.CharField(max_length=120, unique=True, blank=True, null=True)
    is_draft = models.BooleanField(default=True)
    status = models.CharField(max_length=50, blank=True, null=True) # e.g., DRAFT, SUBMITTED, ACCEPTED, REJECTED, etc.
    accepted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        
        db_table = 'e_filing'
        
    # generate e_filing_number in the format ASK2024XXXXXXXCYYYYZZZZZ where XXXXXXX is a zero-padded sequence number, YYYY is the current year, and 
    # ZZZZZ is a zero-padded sequence number of length 5. The prefix "ASK" and suffix "C" are constant. The sequence number should be unique for each e-filing and should reset every year.

    @property
    def petitioner_vs_respondent_display(self):
        from apps.efiling.party_display import build_petitioner_vs_respondent
        if self.petitioner_vs_respondent:
            return self.petitioner_vs_respondent
        return build_petitioner_vs_respondent(self, fallback_petitioner_name=self.petitioner_name or "Petitioner")

    def save(self, *args, **kwargs):
        # Generate filing number only on first save
        if self.pk is None and not self.e_filing_number:
            current_year = timezone.now().year

            with transaction.atomic():  # Atomic block for concurrency
                # Get or create the sequence for this year
                seq_obj, created = EfilingSequence.objects.select_for_update().get_or_create(year=current_year)

                # Increment sequence
                seq_obj.last_sequence += 1
                new_sequence = seq_obj.last_sequence
                seq_obj.save()

                # Format the number
                seq7 = str(new_sequence).zfill(7)
                seq5 = str(new_sequence).zfill(5)
                self.e_filing_number = f"ASK2024{seq7}C{current_year}{seq5}"

        super().save(*args, **kwargs)

    def build_case_number(self) -> tuple[str, int, int]:
        current_year = timezone.now().year
        case_type = self.case_type

        if case_type is None:
            raise ValueError("Case type is required before generating a case number.")

        type_name = (case_type.type_name or "").strip()
        if not type_name:
            raise ValueError("Case type name is required before generating a case number.")

        stored_reg_year = int(case_type.reg_year or 0)
        stored_reg_no = int(case_type.reg_no or 0)

        if stored_reg_year != current_year:
            next_reg_no = 1
        else:
            next_reg_no = stored_reg_no + 1 if stored_reg_no > 0 else 1

        case_number = f"{type_name}/{next_reg_no}/{current_year}"
        return case_number, next_reg_no, current_year

class DocumentIndex(BaseModel):
    name=models.CharField(max_length=215, null=False, blank=False)
    case_type= models.ForeignKey(CaseTypeT, on_delete=models.SET_NULL, null=True, blank=True, related_name='document_index')
    sequence_number = models.IntegerField(blank=False, null=False)
    for_new_filing = models.BooleanField(default=False)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    class Meta:
      
        db_table = 'document_index'

class EfilingLitigant(BaseModel): #party details of petitioner and respondent
    e_filing = models.ForeignKey(Efiling, on_delete=models.CASCADE, related_name='litigants')
    e_filing_number = models.CharField(max_length=100, blank=True, null=True)
    organization = models.ForeignKey(OrgnameT, on_delete=models.SET_NULL, null=True, blank=True, related_name='litigants')
    name = models.CharField(max_length=300, blank=True, null=True)
    gender= models.CharField(max_length=1, blank=True, null=True)
    age = models.SmallIntegerField(blank=True, null=True)
    is_diffentially_abled = models.BooleanField(default=False)
    contact = models.CharField(max_length=10, blank=True, null=True)
    is_petitioner = models.BooleanField(default=False)
    sequence_number = models.IntegerField(blank=False, null=False)
    email= models.EmailField(blank=True, null=True)
    religion = models.CharField(max_length=50, blank=True, null=True)
    caste = models.CharField(max_length=50, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    state_id = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='litigants')  
    district_id = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='litigants')
    taluka= models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)
    

    class Meta:
        
        db_table = 'e_filing_litigant'

class EfilingCaseDetails(BaseModel):
    e_filing = models.ForeignKey(Efiling, on_delete=models.CASCADE, related_name='case_details')
    e_filing_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    cause_of_action = models.CharField(max_length=500, blank=True, null=True)
    date_of_cause_of_action = models.DateField(blank=True, null=True)
    dispute_state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='case_details')
    dispute_district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='case_details')
    dispute_taluka = models.CharField(max_length=100, blank=True, null=True
       )
    
    class Meta:
        db_table = 'e_filing_case_details'

class EfilingActs(BaseModel):
    e_filing = models.ForeignKey(Efiling, on_delete=models.CASCADE, related_name='efiling_acts')
    e_filing_number = models.CharField(max_length=100, blank=True, null=True)
    act = models.ForeignKey(ActT, on_delete=models.SET_NULL, null=True, blank=True, related_name='efiling_acts')
    section = models.CharField(max_length=100, blank=True, null=True)
    sub_section = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        
        db_table = 'e_filing_acts'


def _safe_folder_component(value: str, default: str = "unknown") -> str:
    """
    Make a string safe to use as a folder name.
    Keep it simple: allow alnum + '._-' and replace everything else with '_'.
    """

    raw = (value or "").strip()
    if not raw:
        return default

    # Avoid directory traversal if a value accidentally contains path separators.
    raw = raw.replace("\\", "/").split("/")[-1]

    cleaned_chars: list[str] = []
    for ch in raw:
        if ch.isalnum() or ch in "._-":
            cleaned_chars.append(ch)
        else:
            cleaned_chars.append("_")

    cleaned = "".join(cleaned_chars).strip("_")
    return cleaned or default
       


class EfilingDocuments(BaseModel):
    e_filing = models.ForeignKey(Efiling, on_delete=models.CASCADE, related_name='efiling_documents')
    e_filing_number = models.CharField(max_length=100, blank=True, null=True)
    ia_number = models.CharField(max_length=100, blank=True, null=True)
    document_type = models.CharField(max_length=512, blank=True, null=True) 
    parent_e_filing_document = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_documents')
    final_document = models.FileField(upload_to='media/efile/final_documents/', max_length=512, blank=True, null=True)
    is_ia = models.BooleanField(default=False) 
    filed_by = models.CharField(max_length=100, blank=True, null=True)
    class Meta:
      
        db_table = 'efiling_documents'


class EfilingDocumentsIndex(BaseModel):
    class ScrutinyStatus(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        UNDER_SCRUTINY = "UNDER_SCRUTINY", "Under Scrutiny"
        LEVEL_1_APPROVED = "LEVEL_1_APPROVED", "Level 1 Approved"
        LEVEL_1_REJECTED = "LEVEL_1_REJECTED", "Level 1 Rejected"
        LEVEL_2_APPROVED = "LEVEL_2_APPROVED", "Level 2 Approved"
        LEVEL_2_REJECTED = "LEVEL_2_REJECTED", "Level 2 Rejected"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"

    document= models.ForeignKey(EfilingDocuments, on_delete=models.SET_NULL, null=True, blank=True)
    index= models.ForeignKey(DocumentIndex,on_delete=models.SET_NULL, null=True, blank=True)
    document_part_name = models.CharField(max_length=256, blank=False, null=False)
    def file_part_upload_to(instance, filename):
        efiling_number = None
        if instance.document and instance.document.e_filing_number:
            efiling_number = instance.document.e_filing_number
        else:
            efiling_number = "unknown"
        part_name = _safe_folder_component(instance.document_part_name or "part", default="part")
        doc = instance.document

        # IA documents: /media/efile/<filing_no>/IA/<subfolder>/<part>.pdf
        if doc and getattr(doc, "is_ia", False):
            # IA filing (document_type is "IA"): use IA number as subfolder
            # Document filing with IA selected: use document_type as subfolder
            doc_type = (doc.document_type or "").strip()
            ia_num = (doc.ia_number or "").strip()
            if doc_type.upper() == "IA" and ia_num:
                subfolder = _safe_folder_component(ia_num, default="IA")
            else:
                subfolder = _safe_folder_component(doc_type, default="document_type")
            return f"efile/{efiling_number}/IA/{subfolder}/{part_name}.pdf"

        # Case documents: /media/efile/<filing_no>/<document_type>/<part>.pdf
        document_type_folder = _safe_folder_component(
            doc.document_type if doc else None,
            default="document_type",
        )
        return f"efile/{efiling_number}/{document_type_folder}/{part_name}.pdf"
    # Nullable: parent "header" rows (name only) for grouped index uploads; file rows link via parent_document_index.
    file_part_path = models.FileField(
        upload_to=file_part_upload_to, max_length=512, blank=True, null=True
    )
    is_locked = models.BooleanField(default=False)
    document_sequence = models.IntegerField(blank=True, null=True)
    is_compliant = models.BooleanField(default=False)
    comments = models.TextField(blank=True, null=True)
    scrutiny_status = models.CharField(
        max_length=32,
        choices=ScrutinyStatus.choices,
        default=ScrutinyStatus.DRAFT,
    )
    draft_scrutiny_status = models.CharField(
        max_length=32,
        choices=ScrutinyStatus.choices,
        blank=True,
        null=True,
    )
    draft_comments = models.TextField(blank=True, null=True)
    draft_reviewed_at = models.DateTimeField(blank=True, null=True)
    is_new_for_scrutiny = models.BooleanField(default=False)#Added for allowing accept reject for new document (accepted cases)
    last_resubmitted_at = models.DateTimeField(blank=True, null=True)
    last_reviewed_at = models.DateTimeField(blank=True, null=True)
    parent_document_index = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='resubmissions')
    class Meta:
      
        db_table = 'efiling_documents_index'

class IA(BaseModel):
    e_filing = models.ForeignKey(Efiling, on_delete=models.CASCADE, related_name='ias')
    e_filing_number = models.CharField(max_length=100, blank=True, null=True)
    ia_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    ia_text = models.CharField(max_length=500, blank=True, null=True) 
    status = models.CharField(max_length=50, blank=True, null=True)
    disposal_date = models.DateField(blank=True, null=True) # next date or disposal date   

    class Meta:
      
        db_table = 'ia'
        
    def save(self, *args, **kwargs):
        # Generate filing number only on first save
        if self.pk is None and not self.ia_number:
            current_year = timezone.now().year

            with transaction.atomic():  # Atomic block for concurrency
                # Get or create the sequence for this year
                seq_obj, created = IAfilingSequence.objects.select_for_update().get_or_create(year=current_year)

                # Increment sequence
                seq_obj.last_sequence += 1
                new_sequence = seq_obj.last_sequence
                seq_obj.save()

                # Format the number
              
                seq5 = str(new_sequence).zfill(5)
                self.ia_number = f"IA{current_year}{seq5}"

        super().save(*args, **kwargs)

class IAActs(BaseModel):
    ia = models.ForeignKey(IA, on_delete=models.CASCADE, related_name='ia_acts', null=True, blank=True)
    ia_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    e_filing = models.ForeignKey(Efiling, on_delete=models.CASCADE, related_name='ia_acts')
    e_filing_number = models.CharField(max_length=100, blank=True, null=True)
    act = models.ForeignKey(ActT, on_delete=models.SET_NULL, null=True, blank=True, related_name='ia_acts')
    section = models.CharField(max_length=100, blank=True, null=True)
    sub_section = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        
        db_table = 'ia_acts'


class FileScrutinyCheckList(BaseModel):
    case_type = models.ForeignKey(CaseTypeT, on_delete=models.SET_NULL, null=True, blank=True, related_name='scrutiny_checklists')
    checklist_item = models.CharField(max_length=500, blank=True, null=True)
    class Meta:
      
        db_table = 'file_scrutiny_checklist'

class EfilingDocumentsScrutinyHistory(BaseModel):
    efiling_document_index = models.ForeignKey(EfilingDocumentsIndex, on_delete=models.SET_NULL, null=True, blank=True, related_name='scrutiny_history')
    is_compliant = models.BooleanField(default=False)
    comments = models.TextField(blank=True, null=True)
    scrutiny_status = models.CharField(
        max_length=32,
        choices=EfilingDocumentsIndex.ScrutinyStatus.choices,
        default=EfilingDocumentsIndex.ScrutinyStatus.DRAFT,
    )
    recieved_at = models.DateTimeField(blank=False, null=False)
    response_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
      
        db_table = 'efiling_documents_scrutiny_history'

class Vakalatnama(BaseModel):
    e_filing = models.ForeignKey(Efiling, on_delete=models.CASCADE, related_name='vakalatnamas')
    e_filing_number = models.CharField(max_length=100, blank=True, null=True)
    vakalatnama_document = models.FileField(upload_to='media/efile/vakalatnamas/', max_length=512, blank=True, null=True)
    

    class Meta:
      
        db_table = 'vakalatnama'

class EfilerDocumentAccess(BaseModel):
    vakalatnama= models.ForeignKey(Vakalatnama, on_delete=models.CASCADE, related_name='document_accesses')
    e_filing = models.ForeignKey(Efiling, on_delete=models.CASCADE, related_name='assigned_advocates')
    e_filing_number = models.CharField(max_length=100, blank=True, null=True)
    efiler = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_advocates')
    accces_allowed_from= models.DateTimeField(blank=True, null=True)
    access_provided_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='provided_accesses')

    class Meta:
      
        db_table = 'efiler_document_access'


class CaseAccessRequest(BaseModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    advocate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="case_access_requests",
    )
    e_filing = models.ForeignKey(
        Efiling,
        on_delete=models.CASCADE,
        related_name="case_access_requests",
    )
    case_number = models.CharField(max_length=120)
    vakalatnama_document = models.FileField(
        upload_to="media/efile/case-access-requests/",
        max_length=512,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    rejection_reason = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_case_access_requests",
    )
    reviewed_at = models.DateTimeField(blank=True, null=True)
    resubmission_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reapplications",
    )
    approved_access = models.ForeignKey(
        EfilerDocumentAccess,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_requests",
    )

    class Meta:
        db_table = "case_access_request"
        ordering = ["-id"]

        
class CivilT(BaseModel):
    case_no = models.CharField(max_length=15, blank=True, null=True)
    pet_name = models.CharField(max_length=100, blank=True, null=True)
    lpet_name = models.CharField(max_length=100, blank=True, null=True)
    pet_sex = models.CharField(max_length=1, blank=True, null=True)
    pet_name = models.CharField(max_length=255, blank=True, null=True)
    lpet_name = models.CharField(max_length=255, blank=True, null=True)
    res_name = models.CharField(max_length=255, blank=True, null=True)
    lres_name = models.CharField(max_length=255, blank=True, null=True)
    pet_father_name = models.CharField(max_length=255, blank=True, null=True)
    lpet_father_name = models.CharField(max_length=255, blank=True, null=True)
    res_father_name = models.CharField(max_length=255, blank=True, null=True)
    lres_father_name = models.CharField(max_length=255, blank=True, null=True)
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
    cino = models.CharField(max_length=16)
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
        
        db_table = 'civil_t'

class AdvocateT(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advocate_profile', null=True, blank=True)
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
        db_table = 'advocate_t'
        
class JudgeT(BaseModel):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='judge_profile', null=True, blank=True)
    judge_code = models.CharField(max_length=50, unique=True)
    judge_name = models.CharField(max_length=100, blank=True, null=True)
    seniority = models.IntegerField(blank=True, null=True)
    display = models.TextField()  # This field type is a guess.
    date_of_joining = models.DateField(blank=False, null=False)
    date_of_leaving = models.DateField(blank=True, null=True)
    def __str__(self):
        return self.judge_name
    class Meta:
        db_table = 'judge_t'
    

class BenchT(BaseModel):
    id = models.AutoField(primary_key=True)
    bench_code = models.CharField(max_length=10)
    bench_name = models.CharField(max_length=500, blank=True, null=True)
    bench_type_code = models.CharField(max_length=10, blank=True, null=True)
    judge_code = models.CharField(max_length=50, blank=True, null=True)
    judge = models.ForeignKey(JudgeT, on_delete=models.SET_NULL, null=True, blank=True, related_name='benches')
    from_date = models.DateField(blank=False, null=False)
    to_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'bench_t'


class ReaderJudgeAssignment(BaseModel):
    id = models.AutoField(primary_key=True)
    judge = models.OneToOneField(
        JudgeT,
        on_delete=models.CASCADE,
        related_name='reader_assignment',
    )
    reader_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reader_judge_assignments',
    )
    effective_from = models.DateField(default=timezone.localdate)
    effective_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'reader_judge_assignment'
        indexes = [
            models.Index(fields=['reader_user']),
            models.Index(fields=['effective_from', 'effective_to']),
        ]

    def __str__(self) -> str:
        judge_name = self.judge.judge_name or self.judge.judge_code
        return f'{judge_name} -> {self.reader_user}'
    
class ChatMessage(BaseModel):
    id = models.AutoField(primary_key=True)
    e_filing = models.ForeignKey(Efiling, on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_chat_messages')
    message = models.TextField(blank=True, null=True, max_length=2000)    

    class Meta:
        db_table = 'chat_message'
        
class BudgetHeadT(BaseModel):
    id = models.AutoField(primary_key=True)
    major_head = models.CharField(max_length=4, blank=False, null=False)
    minor_head = models.CharField(max_length=6, blank=False, null=False)
    case_type = models.ForeignKey(CaseTypeT, on_delete=models.SET_NULL, null=True, blank=True, related_name='budget_heads')
    description = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'budget_head_t'
        
class PurposeT(BaseModel):
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
        db_table = 'purpose_t'