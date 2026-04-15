package contract_test

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"

	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/auth"
	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/master/model"
	"github.com/dhrunam/hcs_cms/go_gin_backend/internal/master/routes"
)

func TestDistrictsWithStateFilter(t *testing.T) {
	gin.SetMode(gin.TestMode)
	db := setupTestDB(t)
	router := gin.New()
	apiV1 := router.Group("/api/v1")

	jwtSecret := "test-secret"
	routes.Register(apiV1, db, jwtSecret)

	// Seed test data
	state1 := "Karnataka"
	state2 := "Tamil Nadu"
	district1 := "Bangalore"
	district2 := "Chennai"

	db.Create(&model.State{
		AuditFields: model.AuditFields{ID: 1, IsActive: true},
		State:       &state1,
	})
	db.Create(&model.State{
		AuditFields: model.AuditFields{ID: 2, IsActive: true},
		State:       &state2,
	})

	db.Create(&model.District{
		AuditFields: model.AuditFields{ID: 1, IsActive: true},
		StateID:     ptrUint(1),
		District:    &district1,
	})
	db.Create(&model.District{
		AuditFields: model.AuditFields{ID: 2, IsActive: true},
		StateID:     ptrUint(2),
		District:    &district2,
	})

	// Test without filter
	req := httptest.NewRequest(http.MethodGet, "/api/v1/master/districts", nil)
	req.Header.Set("Authorization", "Bearer "+validJWT(jwtSecret))
	resp := httptest.NewRecorder()
	router.ServeHTTP(resp, req)

	if resp.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", resp.Code)
	}

	var districts []model.District
	if err := json.Unmarshal(resp.Body.Bytes(), &districts); err != nil {
		t.Fatalf("failed to unmarshal response: %v", err)
	}
	if len(districts) != 2 {
		t.Fatalf("expected 2 districts, got %d", len(districts))
	}

	// Test with state_id filter
	req = httptest.NewRequest(http.MethodGet, "/api/v1/master/districts?state_id=1", nil)
	req.Header.Set("Authorization", "Bearer "+validJWT(jwtSecret))
	resp = httptest.NewRecorder()
	router.ServeHTTP(resp, req)

	if resp.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", resp.Code)
	}

	var filteredDistricts []model.District
	if err := json.Unmarshal(resp.Body.Bytes(), &filteredDistricts); err != nil {
		t.Fatalf("failed to unmarshal response: %v", err)
	}
	if len(filteredDistricts) != 1 {
		t.Fatalf("expected 1 filtered district, got %d", len(filteredDistricts))
	}
	if *filteredDistricts[0].District != district1 {
		t.Fatalf("expected %q, got %q", district1, *filteredDistricts[0].District)
	}
}

func TestCourtsPagination(t *testing.T) {
	gin.SetMode(gin.TestMode)
	db := setupTestDB(t)
	router := gin.New()
	apiV1 := router.Group("/api/v1")

	jwtSecret := "test-secret"
	routes.Register(apiV1, db, jwtSecret)

	// Seed 25 courts
	for i := 1; i <= 25; i++ {
		name := "Court " + string(rune('0'+i/10)) + string(rune('0'+i%10))
		db.Create(&model.Court{
			AuditFields: model.AuditFields{ID: uint(i), IsActive: true},
			CourtName:   &name,
			EstCodeSrc:  "CT" + string(rune('0'+i/10)) + string(rune('0'+i%10)),
		})
	}

	// Test first page (default page_size=20)
	req := httptest.NewRequest(http.MethodGet, "/api/v1/master/courts", nil)
	req.Header.Set("Authorization", "Bearer "+validJWT(jwtSecret))
	resp := httptest.NewRecorder()
	router.ServeHTTP(resp, req)

	if resp.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", resp.Code)
	}

	var paginatedResp struct {
		Count    int64         `json:"count"`
		Next     interface{}   `json:"next"`
		Previous interface{}   `json:"previous"`
		Results  []model.Court `json:"results"`
	}
	if err := json.Unmarshal(resp.Body.Bytes(), &paginatedResp); err != nil {
		t.Fatalf("failed to unmarshal response: %v", err)
	}

	if paginatedResp.Count != 25 {
		t.Fatalf("expected count 25, got %d", paginatedResp.Count)
	}
	if len(paginatedResp.Results) != 20 {
		t.Fatalf("expected 20 results, got %d", len(paginatedResp.Results))
	}
	if paginatedResp.Next == nil {
		t.Fatal("expected next page link")
	}

	// Test second page
	req = httptest.NewRequest(http.MethodGet, "/api/v1/master/courts?page=2", nil)
	req.Header.Set("Authorization", "Bearer "+validJWT(jwtSecret))
	resp = httptest.NewRecorder()
	router.ServeHTTP(resp, req)

	if err := json.Unmarshal(resp.Body.Bytes(), &paginatedResp); err != nil {
		t.Fatalf("failed to unmarshal response: %v", err)
	}

	if len(paginatedResp.Results) != 5 {
		t.Fatalf("expected 5 results on page 2, got %d", len(paginatedResp.Results))
	}
}

func TestOrgTypesEndpoint(t *testing.T) {
	gin.SetMode(gin.TestMode)
	db := setupTestDB(t)
	router := gin.New()
	apiV1 := router.Group("/api/v1")

	jwtSecret := "test-secret"
	routes.Register(apiV1, db, jwtSecret)

	// Seed test data
	orgType1 := "Government"
	orgType2 := "Private"

	db.Create(&model.OrgType{
		AuditFields: model.AuditFields{ID: 1, IsActive: true},
		OrgType:     &orgType1,
	})
	db.Create(&model.OrgType{
		AuditFields: model.AuditFields{ID: 2, IsActive: true},
		OrgType:     &orgType2,
	})

	// Test endpoint
	req := httptest.NewRequest(http.MethodGet, "/api/v1/master/org-types", nil)
	req.Header.Set("Authorization", "Bearer "+validJWT(jwtSecret))
	resp := httptest.NewRecorder()
	router.ServeHTTP(resp, req)

	if resp.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", resp.Code)
	}

	var orgTypes []model.OrgType
	if err := json.Unmarshal(resp.Body.Bytes(), &orgTypes); err != nil {
		t.Fatalf("failed to unmarshal response: %v", err)
	}

	if len(orgTypes) != 2 {
		t.Fatalf("expected 2 org types, got %d", len(orgTypes))
	}
}

func TestOrgNamesWithOptionalAuth(t *testing.T) {
	gin.SetMode(gin.TestMode)
	db := setupTestDB(t)
	router := gin.New()
	apiV1 := router.Group("/api/v1")

	jwtSecret := "test-secret"
	routes.Register(apiV1, db, jwtSecret)

	// Seed test data
	orgName1 := "Mumbai Office"
	orgName2 := "Delhi Office"

	db.Create(&model.OrgName{
		AuditFields: model.AuditFields{ID: 1, IsActive: true},
		OrgName:     &orgName1,
	})
	db.Create(&model.OrgName{
		AuditFields: model.AuditFields{ID: 2, IsActive: true},
		OrgName:     &orgName2,
	})

	// Test without authentication (should succeed for read-only)
	req := httptest.NewRequest(http.MethodGet, "/api/v1/master/org-names", nil)
	resp := httptest.NewRecorder()
	router.ServeHTTP(resp, req)

	if resp.Code != http.StatusOK {
		t.Fatalf("expected org-names to allow unauthenticated access, got %d", resp.Code)
	}

	var orgNames []model.OrgName
	if err := json.Unmarshal(resp.Body.Bytes(), &orgNames); err != nil {
		t.Fatalf("failed to unmarshal response: %v", err)
	}

	if len(orgNames) != 2 {
		t.Fatalf("expected 2 org names, got %d", len(orgNames))
	}

	// Test with authentication (should also succeed)
	req = httptest.NewRequest(http.MethodGet, "/api/v1/master/org-names", nil)
	req.Header.Set("Authorization", "Bearer "+validJWT(jwtSecret))
	resp = httptest.NewRecorder()
	router.ServeHTTP(resp, req)

	if resp.Code != http.StatusOK {
		t.Fatalf("expected 200 with auth, got %d", resp.Code)
	}
}

func TestMasterAuthRequirements(t *testing.T) {
	gin.SetMode(gin.TestMode)
	db := setupTestDB(t)

	// Seed test data for auth tests
	db.Create(&model.State{
		AuditFields: model.AuditFields{ID: 1, IsActive: true},
		State:       ptrStr("TestState"),
	})
	db.Create(&model.Court{
		AuditFields: model.AuditFields{ID: 1, IsActive: true},
		CourtName:   ptrStr("TestCourt"),
		EstCodeSrc:  "TST",
	})

	tests := []struct {
		endpoint     string
		requiresAuth bool
		name         string
	}{
		{"/api/v1/master/districts", true, "districts require auth"},
		{"/api/v1/master/courts", true, "courts require auth"},
		{"/api/v1/master/org-types", true, "org-types require auth"},
		{"/api/v1/master/states", false, "states allow optional auth"},
		{"/api/v1/master/case-types", false, "case-types allow optional auth"},
		{"/api/v1/master/acts", false, "acts allow optional auth"},
		{"/api/v1/master/org-names", false, "org-names allow optional auth"},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			router := gin.New()
			apiV1 := router.Group("/api/v1")
			jwtSecret := "test-secret"
			routes.Register(apiV1, db, jwtSecret)

			// Test without auth
			req := httptest.NewRequest(http.MethodGet, tc.endpoint, nil)
			resp := httptest.NewRecorder()
			router.ServeHTTP(resp, req)

			if tc.requiresAuth && resp.Code != http.StatusUnauthorized {
				t.Fatalf("expected 401 for %s without auth, got %d, body=%s", tc.endpoint, resp.Code, resp.Body.String())
			} else if !tc.requiresAuth && resp.Code != http.StatusOK {
				t.Fatalf("expected 200 for %s without auth, got %d, body=%s", tc.endpoint, resp.Code, resp.Body.String())
			}

			// Test with valid auth
			req = httptest.NewRequest(http.MethodGet, tc.endpoint, nil)
			req.Header.Set("Authorization", "Bearer "+validJWT(jwtSecret))
			resp = httptest.NewRecorder()
			router.ServeHTTP(resp, req)

			if resp.Code != http.StatusOK {
				t.Fatalf("expected 200 for %s with auth, got %d, body=%s", tc.endpoint, resp.Code, resp.Body.String())
			}
		})
	}
}

func setupTestDB(t *testing.T) *gorm.DB {
	db, err := gorm.Open(sqlite.Open("file:test_extended?mode=memory&cache=shared"), &gorm.Config{})
	if err != nil {
		t.Fatalf("failed to open test db: %v", err)
	}

	if err := db.AutoMigrate(
		&model.State{},
		&model.CaseType{},
		&model.District{},
		&model.Court{},
		&model.OrgType{},
		&model.OrgName{},
		&model.Act{},
	); err != nil {
		t.Fatalf("failed to migrate test db: %v", err)
	}

	return db
}

func validJWT(secret string) string {
	claims := &auth.Claims{
		UserID: "1",
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(1 * time.Hour)),
		},
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, _ := token.SignedString([]byte(secret))
	return tokenString
}

func ptrStr(s string) *string {
	return &s
}

func ptrUint(u uint) *uint {
	return &u
}
