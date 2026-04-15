package contract_test

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"reflect"
	"testing"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"

	mastermodel "github.com/dhrunam/hcs_cms/go_gin_backend/internal/master/model"
	masterroutes "github.com/dhrunam/hcs_cms/go_gin_backend/internal/master/routes"
)

func TestMasterEndpointsMatchFixtures(t *testing.T) {
	gin.SetMode(gin.TestMode)

	db := setupMasterDB(t)
	seedMasterData(t, db)

	router := gin.New()
	apiV1 := router.Group("/api/v1")
	masterroutes.Register(apiV1, db, "test-secret")

	tests := []struct {
		name         string
		path         string
		fixtureFile  string
		requiresAuth bool
	}{
		{name: "case types", path: "/api/v1/master/case-types", fixtureFile: "case_types.json", requiresAuth: false},
		{name: "states", path: "/api/v1/master/states", fixtureFile: "states.json", requiresAuth: false},
		{name: "districts filtered", path: "/api/v1/master/districts?state_id=1", fixtureFile: "districts.json", requiresAuth: true},
		{name: "courts", path: "/api/v1/master/courts", fixtureFile: "courts.json", requiresAuth: true},
		{name: "org types", path: "/api/v1/master/org-types", fixtureFile: "org_types.json", requiresAuth: true},
		{name: "org names", path: "/api/v1/master/org-names", fixtureFile: "org_names.json", requiresAuth: false},
		{name: "acts", path: "/api/v1/master/acts", fixtureFile: "acts.json", requiresAuth: false},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			req := httptest.NewRequest(http.MethodGet, tc.path, nil)
			if tc.requiresAuth {
				req.Header.Set("Authorization", "Bearer "+signedAuthToken(t, "test-secret", "99"))
			}
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)

			if resp.Code != http.StatusOK {
				t.Fatalf("expected 200, got %d, body=%s", resp.Code, resp.Body.String())
			}

			var got interface{}
			if err := json.Unmarshal(resp.Body.Bytes(), &got); err != nil {
				t.Fatalf("response is not valid JSON: %v", err)
			}

			expected := loadFixtureAny(t, tc.fixtureFile)
			if !reflect.DeepEqual(got, expected) {
				gotJSON, _ := json.MarshalIndent(got, "", "  ")
				expJSON, _ := json.MarshalIndent(expected, "", "  ")
				t.Fatalf("strict snapshot mismatch\nexpected=%s\nactual=%s", expJSON, gotJSON)
			}
		})
	}
}

func setupMasterDB(t *testing.T) *gorm.DB {
	t.Helper()
	db, err := gorm.Open(sqlite.Open("file::memory:?cache=shared"), &gorm.Config{})
	if err != nil {
		t.Fatalf("failed to init sqlite: %v", err)
	}

	if err := db.AutoMigrate(
		&mastermodel.CaseType{},
		&mastermodel.State{},
		&mastermodel.District{},
		&mastermodel.Court{},
		&mastermodel.OrgType{},
		&mastermodel.OrgName{},
		&mastermodel.Act{},
	); err != nil {
		t.Fatalf("failed to migrate models: %v", err)
	}
	return db
}

func seedMasterData(t *testing.T, db *gorm.DB) {
	t.Helper()

	caseTypeName := "Writ"
	fullForm := "Writ Petition"
	stateName := "Sikkim"
	districtName := "East Sikkim"
	courtName := "High Court of Sikkim"
	orgTypeName := "Government"
	orgName := "High Court of Sikkim"
	actName := "Constitution of India"
	actType := "CENTRAL"
	display := "Y"
	estCode := "SKNM01"

	for _, table := range []string{"case_type_t", "state", "district", "court", "orgtype_t", "orgname_t", "act_t"} {
		if err := db.Exec("DELETE FROM " + table).Error; err != nil {
			t.Fatalf("failed to clear table %s: %v", table, err)
		}
	}

	if err := db.Exec(`
		INSERT INTO case_type_t
		(id, created_at, updated_at, created_by_id, updated_by_id, is_active, case_type, type_name, ltype_name, full_form, lfull_form, type_flag, est_code_src, reg_no, reg_year)
		VALUES (?, NULL, NULL, NULL, NULL, ?, ?, ?, NULL, ?, NULL, ?, ?, ?, ?)
	`, 1, true, 10, caseTypeName, fullForm, "W", estCode, 1, 2026).Error; err != nil {
		t.Fatalf("failed to seed case_type_t: %v", err)
	}

	if err := db.Exec(`
		INSERT INTO state
		(id, created_at, updated_at, created_by_id, updated_by_id, is_active, state, create_modify, est_code_src, national_code)
		VALUES (?, NULL, NULL, NULL, NULL, ?, ?, NULL, ?, NULL)
	`, 1, true, stateName, estCode).Error; err != nil {
		t.Fatalf("failed to seed state: %v", err)
	}

	if err := db.Exec(`
		INSERT INTO district
		(id, created_at, updated_at, created_by_id, updated_by_id, is_active, state_id_id, district, natinal_code)
		VALUES (?, NULL, NULL, NULL, NULL, ?, ?, ?, NULL)
	`, 1, true, 1, districtName).Error; err != nil {
		t.Fatalf("failed to seed district: %v", err)
	}

	if err := db.Exec(`
		INSERT INTO court
		(id, created_at, updated_at, created_by_id, updated_by_id, is_active, court_name, address, est_code_src)
		VALUES (?, NULL, NULL, NULL, NULL, ?, ?, NULL, ?)
	`, 1, true, courtName, estCode).Error; err != nil {
		t.Fatalf("failed to seed court: %v", err)
	}

	if err := db.Exec(`
		INSERT INTO orgtype_t
		(id, created_at, updated_at, created_by_id, updated_by_id, is_active, orgtype, national_code)
		VALUES (?, NULL, NULL, NULL, NULL, ?, ?, NULL)
	`, 1, true, orgTypeName).Error; err != nil {
		t.Fatalf("failed to seed orgtype_t: %v", err)
	}

	if err := db.Exec(`
		INSERT INTO orgname_t
		(id, created_at, updated_at, created_by_id, updated_by_id, is_active, orgtype_id, orgname, contactperson, address, state_id_id, district_id_id, taluka_code, village_code, email, mobile, phone, fax, village1_code, village2_code, town_code, ward_code, national_code, est_code_src)
		VALUES (?, NULL, NULL, NULL, NULL, ?, ?, ?, NULL, NULL, ?, ?, ?, ?, NULL, NULL, NULL, NULL, ?, ?, ?, ?, NULL, ?)
	`, 1, true, 1, orgName, 1, 1, 0, 0, 0, 0, 0, 0, estCode).Error; err != nil {
		t.Fatalf("failed to seed orgname_t: %v", err)
	}

	if err := db.Exec(`
		INSERT INTO act_t
		(id, created_at, updated_at, created_by_id, updated_by_id, is_active, actcode, actname, lactname, acttype, display, national_code, shortact, amd, create_modify, est_code_src)
		VALUES (?, NULL, NULL, NULL, NULL, ?, ?, ?, NULL, ?, ?, NULL, NULL, NULL, NULL, ?)
	`, 1, true, 101, actName, actType, display, estCode).Error; err != nil {
		t.Fatalf("failed to seed act_t: %v", err)
	}
}

func loadFixtureAny(t *testing.T, fileName string) interface{} {
	t.Helper()
	path := filepath.Join("..", "fixtures", "master", fileName)
	bytes, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("failed to read fixture %s: %v", path, err)
	}
	var out interface{}
	if err := json.Unmarshal(bytes, &out); err != nil {
		t.Fatalf("invalid fixture JSON %s: %v", path, err)
	}
	return out
}
