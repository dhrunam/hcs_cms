package contract_test

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"

	cismodel "github.com/dhrunam/hcs_cms/go_gin_backend/internal/cis/model"
	cisroutes "github.com/dhrunam/hcs_cms/go_gin_backend/internal/cis/routes"
	mastermodel "github.com/dhrunam/hcs_cms/go_gin_backend/internal/master/model"
)

func TestCISMigrateStatesRequiresAuth(t *testing.T) {
	gin.SetMode(gin.TestMode)
	primaryDB, legacyDB := setupCISMigrationDBs(t)
	router := setupCISMigrationRouter(primaryDB, legacyDB)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/cis/migrate/states", nil)
	resp := httptest.NewRecorder()

	router.ServeHTTP(resp, req)

	if resp.Code != http.StatusUnauthorized {
		t.Fatalf("expected %d, got %d, body=%s", http.StatusUnauthorized, resp.Code, resp.Body.String())
	}

	var body map[string]interface{}
	if err := json.Unmarshal(resp.Body.Bytes(), &body); err != nil {
		t.Fatalf("failed to parse auth error response: %v", err)
	}
	if body["detail"] != "authentication credentials were not provided" {
		t.Fatalf("unexpected auth error detail: %+v", body)
	}
}

func TestCISMigrateStatesRejectsInvalidToken(t *testing.T) {
	gin.SetMode(gin.TestMode)
	primaryDB, legacyDB := setupCISMigrationDBs(t)
	router := setupCISMigrationRouter(primaryDB, legacyDB)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/cis/migrate/states", nil)
	req.Header.Set("Authorization", "Bearer invalid.token.value")
	resp := httptest.NewRecorder()

	router.ServeHTTP(resp, req)

	if resp.Code != http.StatusUnauthorized {
		t.Fatalf("expected %d, got %d, body=%s", http.StatusUnauthorized, resp.Code, resp.Body.String())
	}

	var body map[string]interface{}
	if err := json.Unmarshal(resp.Body.Bytes(), &body); err != nil {
		t.Fatalf("failed to parse auth error response: %v", err)
	}
	if body["detail"] != "invalid token" {
		t.Fatalf("unexpected invalid token detail: %+v", body)
	}
}

func TestCISMigrateStatesReturns503WhenLegacyDBMissing(t *testing.T) {
	gin.SetMode(gin.TestMode)
	primaryDB, _ := setupCISMigrationDBs(t)
	router := setupCISMigrationRouter(primaryDB, nil)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/cis/migrate/states", nil)
	req.Header.Set("Authorization", "Bearer "+signedAuthToken(t, "test-secret", "99"))
	resp := httptest.NewRecorder()

	router.ServeHTTP(resp, req)

	if resp.Code != http.StatusServiceUnavailable {
		t.Fatalf("expected %d, got %d, body=%s", http.StatusServiceUnavailable, resp.Code, resp.Body.String())
	}

	var body map[string]interface{}
	if err := json.Unmarshal(resp.Body.Bytes(), &body); err != nil {
		t.Fatalf("failed to parse service unavailable response: %v", err)
	}
	if body["detail"] != "legacy cis database is not configured" {
		t.Fatalf("unexpected 503 detail: %+v", body)
	}
}

func TestCISMigrateStatesEndpointUsesLimit(t *testing.T) {
	gin.SetMode(gin.TestMode)
	primaryDB, legacyDB := setupCISMigrationDBs(t)

	stateOne := "Sikkim"
	stateTwo := "Assam"
	if err := legacyDB.Create(&cismodel.LegacyState{StateID: 1, State: &stateOne}).Error; err != nil {
		t.Fatalf("failed to seed first legacy state: %v", err)
	}
	if err := legacyDB.Create(&cismodel.LegacyState{StateID: 2, State: &stateTwo}).Error; err != nil {
		t.Fatalf("failed to seed second legacy state: %v", err)
	}

	router := setupCISMigrationRouter(primaryDB, legacyDB)
	req := httptest.NewRequest(http.MethodPost, "/api/v1/cis/migrate/states?limit=1", nil)
	req.Header.Set("Authorization", "Bearer "+signedAuthToken(t, "test-secret", "99"))
	resp := httptest.NewRecorder()

	router.ServeHTTP(resp, req)

	if resp.Code != http.StatusOK {
		t.Fatalf("expected %d, got %d, body=%s", http.StatusOK, resp.Code, resp.Body.String())
	}

	var got map[string]interface{}
	if err := json.Unmarshal(resp.Body.Bytes(), &got); err != nil {
		t.Fatalf("failed to parse migration response: %v", err)
	}

	if got["created"] != float64(1) || got["updated"] != float64(0) || got["skipped"] != float64(0) {
		t.Fatalf("unexpected migration summary: %+v", got)
	}

	var states []mastermodel.State
	if err := primaryDB.Order("id asc").Find(&states).Error; err != nil {
		t.Fatalf("failed to read primary states: %v", err)
	}
	if len(states) != 1 {
		t.Fatalf("expected one migrated state with limit=1, got %d", len(states))
	}
}

func TestCISMigrateStatesEndpointIsIdempotent(t *testing.T) {
	tests := []struct {
		name                string
		path                string
		expectedFirstCreated float64
		expectedSecondUpdated float64
		expectedRows         int
	}{
		{
			name:                 "without limit",
			path:                 "/api/v1/cis/migrate/states",
			expectedFirstCreated:  2,
			expectedSecondUpdated: 2,
			expectedRows:          2,
		},
		{
			name:                 "with limit",
			path:                 "/api/v1/cis/migrate/states?limit=1",
			expectedFirstCreated:  1,
			expectedSecondUpdated: 1,
			expectedRows:          1,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			gin.SetMode(gin.TestMode)
			primaryDB, legacyDB := setupCISMigrationDBs(t)

			stateOne := "Sikkim"
			stateTwo := "Assam"
			if err := legacyDB.Create(&cismodel.LegacyState{StateID: 1, State: &stateOne}).Error; err != nil {
				t.Fatalf("failed to seed first legacy state: %v", err)
			}
			if err := legacyDB.Create(&cismodel.LegacyState{StateID: 2, State: &stateTwo}).Error; err != nil {
				t.Fatalf("failed to seed second legacy state: %v", err)
			}

			router := setupCISMigrationRouter(primaryDB, legacyDB)

			runMigrateStates := func() map[string]interface{} {
				req := httptest.NewRequest(http.MethodPost, tc.path, nil)
				req.Header.Set("Authorization", "Bearer "+signedAuthToken(t, "test-secret", "99"))
				resp := httptest.NewRecorder()

				router.ServeHTTP(resp, req)
				if resp.Code != http.StatusOK {
					t.Fatalf("expected %d, got %d, body=%s", http.StatusOK, resp.Code, resp.Body.String())
				}

				var body map[string]interface{}
				if err := json.Unmarshal(resp.Body.Bytes(), &body); err != nil {
					t.Fatalf("failed to parse migrate/states response: %v", err)
				}
				return body
			}

			firstRun := runMigrateStates()
			if firstRun["created"] != tc.expectedFirstCreated || firstRun["updated"] != float64(0) || firstRun["skipped"] != float64(0) {
				t.Fatalf("unexpected first-run summary: %+v", firstRun)
			}

			secondRun := runMigrateStates()
			if secondRun["created"] != float64(0) || secondRun["updated"] != tc.expectedSecondUpdated || secondRun["skipped"] != float64(0) {
				t.Fatalf("unexpected second-run summary: %+v", secondRun)
			}

			var states []mastermodel.State
			if err := primaryDB.Order("id asc").Find(&states).Error; err != nil {
				t.Fatalf("failed to read migrated states after second run: %v", err)
			}
			if len(states) != tc.expectedRows {
				t.Fatalf("expected %d state rows after second run, got %d", tc.expectedRows, len(states))
			}
		})
	}
}

func TestCISMigrateStatesInvalidLimitFallsBackToNoLimit(t *testing.T) {
	tests := []struct {
		name  string
		limit string
	}{
		{name: "zero", limit: "0"},
		{name: "negative", limit: "-1"},
		{name: "non numeric", limit: "abc"},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			gin.SetMode(gin.TestMode)
			primaryDB, legacyDB := setupCISMigrationDBs(t)

			stateOne := "Sikkim"
			stateTwo := "Assam"
			if err := legacyDB.Create(&cismodel.LegacyState{StateID: 1, State: &stateOne}).Error; err != nil {
				t.Fatalf("failed to seed first legacy state: %v", err)
			}
			if err := legacyDB.Create(&cismodel.LegacyState{StateID: 2, State: &stateTwo}).Error; err != nil {
				t.Fatalf("failed to seed second legacy state: %v", err)
			}

			router := setupCISMigrationRouter(primaryDB, legacyDB)
			path := "/api/v1/cis/migrate/states?limit=" + tc.limit
			req := httptest.NewRequest(http.MethodPost, path, nil)
			req.Header.Set("Authorization", "Bearer "+signedAuthToken(t, "test-secret", "99"))
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)

			if resp.Code != http.StatusOK {
				t.Fatalf("expected %d, got %d, body=%s", http.StatusOK, resp.Code, resp.Body.String())
			}

			var got map[string]interface{}
			if err := json.Unmarshal(resp.Body.Bytes(), &got); err != nil {
				t.Fatalf("failed to parse migration response: %v", err)
			}
			if got["created"] != float64(2) || got["updated"] != float64(0) || got["skipped"] != float64(0) {
				t.Fatalf("unexpected migration summary for invalid limit=%s: %+v", tc.limit, got)
			}

			var states []mastermodel.State
			if err := primaryDB.Find(&states).Error; err != nil {
				t.Fatalf("failed to read migrated states: %v", err)
			}
			if len(states) != 2 {
				t.Fatalf("expected two migrated states for invalid limit=%s, got %d", tc.limit, len(states))
			}
		})
	}
}

func TestCISMigrateAllEndpointMigratesAllEntities(t *testing.T) {
	gin.SetMode(gin.TestMode)
	primaryDB, legacyDB := setupCISMigrationDBs(t)

	stateName := "Sikkim"
	if err := legacyDB.Create(&cismodel.LegacyState{StateID: 10, State: &stateName}).Error; err != nil {
		t.Fatalf("failed to seed legacy state: %v", err)
	}

	caseTypeName := "Civil"
	typeFlag := "Y"
	if err := legacyDB.Create(&cismodel.LegacyCaseType{CaseType: 20, TypeName: &caseTypeName, TypeFlag: &typeFlag}).Error; err != nil {
		t.Fatalf("failed to seed legacy case type: %v", err)
	}

	actName := "Evidence Act"
	actType := "Central"
	display := "Y"
	if err := legacyDB.Create(&cismodel.LegacyAct{ActCode: 30, ActName: &actName, ActType: &actType, Display: &display}).Error; err != nil {
		t.Fatalf("failed to seed legacy act: %v", err)
	}

	router := setupCISMigrationRouter(primaryDB, legacyDB)
	req := httptest.NewRequest(http.MethodPost, "/api/v1/cis/migrate/all", nil)
	req.Header.Set("Authorization", "Bearer "+signedAuthToken(t, "test-secret", "99"))
	resp := httptest.NewRecorder()

	router.ServeHTTP(resp, req)

	if resp.Code != http.StatusOK {
		t.Fatalf("expected %d, got %d, body=%s", http.StatusOK, resp.Code, resp.Body.String())
	}

	var body struct {
		Detail    string                   `json:"detail"`
		Summaries []map[string]interface{} `json:"summaries"`
	}
	if err := json.Unmarshal(resp.Body.Bytes(), &body); err != nil {
		t.Fatalf("failed to parse migration response: %v", err)
	}
	if len(body.Summaries) != 3 {
		t.Fatalf("expected 3 entity summaries, got %d", len(body.Summaries))
	}

	var states []mastermodel.State
	if err := primaryDB.Find(&states).Error; err != nil {
		t.Fatalf("failed to query migrated states: %v", err)
	}
	if len(states) != 1 {
		t.Fatalf("expected one migrated state, got %d", len(states))
	}

	var caseTypes []mastermodel.CaseType
	if err := primaryDB.Find(&caseTypes).Error; err != nil {
		t.Fatalf("failed to query migrated case types: %v", err)
	}
	if len(caseTypes) != 1 {
		t.Fatalf("expected one migrated case type, got %d", len(caseTypes))
	}

	var acts []mastermodel.Act
	if err := primaryDB.Find(&acts).Error; err != nil {
		t.Fatalf("failed to query migrated acts: %v", err)
	}
	if len(acts) != 1 {
		t.Fatalf("expected one migrated act, got %d", len(acts))
	}
}

func TestCISMigrateAllEndpointIsIdempotent(t *testing.T) {
	gin.SetMode(gin.TestMode)
	primaryDB, legacyDB := setupCISMigrationDBs(t)

	stateName := "Sikkim"
	if err := legacyDB.Create(&cismodel.LegacyState{StateID: 10, State: &stateName}).Error; err != nil {
		t.Fatalf("failed to seed legacy state: %v", err)
	}

	caseTypeName := "Civil"
	typeFlag := "Y"
	if err := legacyDB.Create(&cismodel.LegacyCaseType{CaseType: 20, TypeName: &caseTypeName, TypeFlag: &typeFlag}).Error; err != nil {
		t.Fatalf("failed to seed legacy case type: %v", err)
	}

	actName := "Evidence Act"
	actType := "Central"
	display := "Y"
	if err := legacyDB.Create(&cismodel.LegacyAct{ActCode: 30, ActName: &actName, ActType: &actType, Display: &display}).Error; err != nil {
		t.Fatalf("failed to seed legacy act: %v", err)
	}

	router := setupCISMigrationRouter(primaryDB, legacyDB)

	runMigrateAll := func() []map[string]interface{} {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/cis/migrate/all", nil)
		req.Header.Set("Authorization", "Bearer "+signedAuthToken(t, "test-secret", "99"))
		resp := httptest.NewRecorder()

		router.ServeHTTP(resp, req)
		if resp.Code != http.StatusOK {
			t.Fatalf("expected %d, got %d, body=%s", http.StatusOK, resp.Code, resp.Body.String())
		}

		var body struct {
			Summaries []map[string]interface{} `json:"summaries"`
		}
		if err := json.Unmarshal(resp.Body.Bytes(), &body); err != nil {
			t.Fatalf("failed to parse migrate/all response: %v", err)
		}
		if len(body.Summaries) != 3 {
			t.Fatalf("expected 3 summaries, got %d", len(body.Summaries))
		}
		return body.Summaries
	}

	getSummary := func(summaries []map[string]interface{}, entity string) map[string]interface{} {
		for _, summary := range summaries {
			if summary["entity"] == entity {
				return summary
			}
		}
		t.Fatalf("missing summary for entity %s", entity)
		return nil
	}

	firstRun := runMigrateAll()
	for _, entity := range []string{"states", "case_types", "acts"} {
		summary := getSummary(firstRun, entity)
		if summary["created"] != float64(1) || summary["updated"] != float64(0) || summary["skipped"] != float64(0) {
			t.Fatalf("unexpected first-run summary for %s: %+v", entity, summary)
		}
	}

	secondRun := runMigrateAll()
	for _, entity := range []string{"states", "case_types", "acts"} {
		summary := getSummary(secondRun, entity)
		if summary["created"] != float64(0) || summary["updated"] != float64(1) || summary["skipped"] != float64(0) {
			t.Fatalf("unexpected second-run summary for %s: %+v", entity, summary)
		}
	}

	var states []mastermodel.State
	if err := primaryDB.Find(&states).Error; err != nil {
		t.Fatalf("failed to query states after second run: %v", err)
	}
	if len(states) != 1 {
		t.Fatalf("expected one state row after second run, got %d", len(states))
	}

	var caseTypes []mastermodel.CaseType
	if err := primaryDB.Find(&caseTypes).Error; err != nil {
		t.Fatalf("failed to query case types after second run: %v", err)
	}
	if len(caseTypes) != 1 {
		t.Fatalf("expected one case type row after second run, got %d", len(caseTypes))
	}

	var acts []mastermodel.Act
	if err := primaryDB.Find(&acts).Error; err != nil {
		t.Fatalf("failed to query acts after second run: %v", err)
	}
	if len(acts) != 1 {
		t.Fatalf("expected one act row after second run, got %d", len(acts))
	}
}

func setupCISMigrationRouter(primaryDB, legacyDB *gorm.DB) *gin.Engine {
	router := gin.New()
	apiV1 := router.Group("/api/v1")
	cisroutes.Register(apiV1, primaryDB, legacyDB, "test-secret")
	return router
}

func setupCISMigrationDBs(t *testing.T) (*gorm.DB, *gorm.DB) {
	t.Helper()

	base := strings.ReplaceAll(strings.ToLower(t.Name()), "/", "_")
	primaryDSN := fmt.Sprintf("file:%s_primary?mode=memory&cache=shared", base)
	legacyDSN := fmt.Sprintf("file:%s_legacy?mode=memory&cache=shared", base)

	primaryDB, err := gorm.Open(sqlite.Open(primaryDSN), &gorm.Config{})
	if err != nil {
		t.Fatalf("failed to open primary sqlite db: %v", err)
	}
	legacyDB, err := gorm.Open(sqlite.Open(legacyDSN), &gorm.Config{})
	if err != nil {
		t.Fatalf("failed to open legacy sqlite db: %v", err)
	}

	if err := primaryDB.AutoMigrate(&mastermodel.State{}, &mastermodel.CaseType{}, &mastermodel.Act{}); err != nil {
		t.Fatalf("failed to migrate primary models: %v", err)
	}
	if err := legacyDB.AutoMigrate(&cismodel.LegacyState{}, &cismodel.LegacyCaseType{}, &cismodel.LegacyAct{}); err != nil {
		t.Fatalf("failed to migrate legacy models: %v", err)
	}

	return primaryDB, legacyDB
}
