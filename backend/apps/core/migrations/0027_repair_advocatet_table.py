from django.conf import settings
from django.db import migrations, models


CREATE_ADVOCATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS advocate_t (
    adv_code bigint PRIMARY KEY,
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone NULL,
    is_active boolean NOT NULL DEFAULT TRUE,
    adv_name varchar(100) NULL,
    ladv_name varchar(100) NULL,
    adv_reg varchar(20) NULL,
    display text NOT NULL,
    address text NULL,
    laddress text NULL,
    email varchar(254) NULL,
    adv_sex varchar(1) NULL,
    adv_mobile varchar(15) NULL,
    adv_phone varchar(15) NULL,
    adv_phone1 varchar(15) NULL,
    off_add text NULL,
    loff_add text NULL,
    dist_code smallint NOT NULL,
    taluka_code smallint NOT NULL,
    village_code integer NOT NULL,
    village1_code integer NOT NULL,
    village2_code integer NOT NULL,
    town_code integer NOT NULL,
    ward_code integer NOT NULL,
    adv_fax varchar(15) NULL,
    date_birth date NULL,
    debarred text NOT NULL,
    pincode integer NULL,
    dist_code_res smallint NOT NULL,
    taluka_code_res smallint NOT NULL,
    village_code_res integer NOT NULL,
    village1_code_res integer NOT NULL,
    village2_code_res integer NOT NULL,
    town_code_res integer NOT NULL,
    ward_code_res integer NOT NULL,
    status integer NOT NULL,
    frequent text NOT NULL,
    adv_full_name varchar(100) NULL,
    adv_seniority integer NULL,
    adv_gender varchar(1) NULL,
    state_id_res integer NULL,
    uid bigint NULL,
    state_id integer NULL,
    advocate_type smallint NOT NULL,
    ori_adv_code bigint NULL,
    ori_adv_bar varchar(20) NULL,
    adv_desig_from_date date NULL,
    amd varchar(1) NULL,
    create_modify timestamp with time zone NULL,
    est_code_src varchar(6) NOT NULL,
    user_id bigint NULL,
    created_by_id bigint NULL,
    updated_by_id bigint NULL
);
"""

ADD_MISSING_AUDIT_COLUMNS_SQL = """
ALTER TABLE advocate_t ADD COLUMN IF NOT EXISTS user_id bigint NULL;
ALTER TABLE advocate_t ADD COLUMN IF NOT EXISTS created_by_id bigint NULL;
ALTER TABLE advocate_t ADD COLUMN IF NOT EXISTS updated_by_id bigint NULL;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0026_alter_advocatet_options"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=CREATE_ADVOCATE_TABLE_SQL,
                    reverse_sql=migrations.RunSQL.noop,
                ),
                migrations.RunSQL(
                    sql=ADD_MISSING_AUDIT_COLUMNS_SQL,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="advocatet",
                    name="user",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.CASCADE,
                        related_name="advocate_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                migrations.AddField(
                    model_name="advocatet",
                    name="created_by",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name="advocatet_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                migrations.AddField(
                    model_name="advocatet",
                    name="updated_by",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name="advocatet_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
