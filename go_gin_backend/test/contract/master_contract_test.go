package contract_test

import (
	"encoding/json"
	"testing"

	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/master/model"
)

func TestCaseTypeJSONContract(t *testing.T) {
	item := model.CaseType{}
	keys := jsonKeys(t, item)
	expectKeys(t, keys, []string{
		"id", "created_at", "updated_at", "created_by", "updated_by", "is_active",
		"case_type", "type_name", "ltype_name", "full_form", "lfull_form", "type_flag", "est_code_src", "reg_no", "reg_year",
	})
}

func TestStateJSONContract(t *testing.T) {
	item := model.State{}
	keys := jsonKeys(t, item)
	expectKeys(t, keys, []string{
		"id", "created_at", "updated_at", "created_by", "updated_by", "is_active",
		"state", "create_modify", "est_code_src", "national_code",
	})
}

func TestDistrictJSONContract(t *testing.T) {
	item := model.District{}
	keys := jsonKeys(t, item)
	expectKeys(t, keys, []string{
		"id", "created_at", "updated_at", "created_by", "updated_by", "is_active",
		"state_id", "district", "natinal_code",
	})
}

func TestCourtJSONContract(t *testing.T) {
	item := model.Court{}
	keys := jsonKeys(t, item)
	expectKeys(t, keys, []string{
		"id", "created_at", "updated_at", "created_by", "updated_by", "is_active",
		"court_name", "address", "est_code_src",
	})
}

func TestOrgTypeJSONContract(t *testing.T) {
	item := model.OrgType{}
	keys := jsonKeys(t, item)
	expectKeys(t, keys, []string{
		"id", "created_at", "updated_at", "created_by", "updated_by", "is_active",
		"orgtype", "national_code",
	})
}

func TestOrgNameJSONContract(t *testing.T) {
	item := model.OrgName{}
	keys := jsonKeys(t, item)
	expectKeys(t, keys, []string{
		"id", "created_at", "updated_at", "created_by", "updated_by", "is_active",
		"orgtype", "orgname", "contactperson", "address", "state_id", "district_id", "taluka_code", "village_code",
		"email", "mobile", "phone", "fax", "village1_code", "village2_code", "town_code", "ward_code", "national_code", "est_code_src",
	})
}

func TestActJSONContract(t *testing.T) {
	item := model.Act{}
	keys := jsonKeys(t, item)
	expectKeys(t, keys, []string{
		"id", "created_at", "updated_at", "created_by", "updated_by", "is_active",
		"actcode", "actname", "lactname", "acttype", "display", "national_code", "shortact", "amd", "create_modify", "est_code_src",
	})
}

func jsonKeys(t *testing.T, v interface{}) map[string]struct{} {
	t.Helper()
	b, err := json.Marshal(v)
	if err != nil {
		t.Fatalf("marshal failed: %v", err)
	}
	obj := map[string]interface{}{}
	if err := json.Unmarshal(b, &obj); err != nil {
		t.Fatalf("unmarshal failed: %v", err)
	}
	keys := make(map[string]struct{}, len(obj))
	for k := range obj {
		keys[k] = struct{}{}
	}
	return keys
}

func expectKeys(t *testing.T, got map[string]struct{}, expected []string) {
	t.Helper()
	for _, key := range expected {
		if _, ok := got[key]; !ok {
			t.Fatalf("missing key in JSON contract: %s", key)
		}
	}
}
