package contract_test

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"

	accountmodel "github.com/dhrunam/hcs_cms/go_gin_backend/internal/accounts/model"
	accountsroutes "github.com/dhrunam/hcs_cms/go_gin_backend/internal/accounts/routes"
)

type authGroup struct {
	ID   uint   `gorm:"column:id;primaryKey"`
	Name string `gorm:"column:name"`
}

func (authGroup) TableName() string { return "auth_group" }

type authUserGroup struct {
	ID      uint `gorm:"column:id;primaryKey"`
	UserID  uint `gorm:"column:user_id"`
	GroupID uint `gorm:"column:group_id"`
}

func (authUserGroup) TableName() string { return "auth_user_groups" }

func TestAccountsMeReturnsCurrentUserProfile(t *testing.T) {
	gin.SetMode(gin.TestMode)
	db := setupAccountsDB(t)
	seedAccountsData(t, db)

	router := gin.New()
	apiV1 := router.Group("/api/v1")
	accountsroutes.Register(apiV1, db, "test-secret")

	req := httptest.NewRequest(http.MethodGet, "/api/v1/accounts/users/me", nil)
	req.Header.Set("Authorization", "Bearer "+signedAuthToken(t, "test-secret", "99"))
	resp := httptest.NewRecorder()

	router.ServeHTTP(resp, req)

	if resp.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d, body=%s", resp.Code, resp.Body.String())
	}

	var body map[string]interface{}
	if err := json.Unmarshal(resp.Body.Bytes(), &body); err != nil {
		t.Fatalf("invalid JSON response: %v", err)
	}

	if body["email"] != "reader@example.com" {
		t.Fatalf("expected email reader@example.com, got %+v", body["email"])
	}
	groups, ok := body["groups"].([]interface{})
	if !ok || len(groups) != 1 || groups[0] != "READER" {
		t.Fatalf("unexpected groups payload: %+v", body["groups"])
	}
}

func TestAccountsMeRequiresAuth(t *testing.T) {
	gin.SetMode(gin.TestMode)
	db := setupAccountsDB(t)

	router := gin.New()
	apiV1 := router.Group("/api/v1")
	accountsroutes.Register(apiV1, db, "test-secret")

	req := httptest.NewRequest(http.MethodGet, "/api/v1/accounts/users/me", nil)
	resp := httptest.NewRecorder()

	router.ServeHTTP(resp, req)

	if resp.Code != http.StatusUnauthorized {
		t.Fatalf("expected 401, got %d, body=%s", resp.Code, resp.Body.String())
	}
}

func TestAccountsTokenVerifyMatchesSimpleJWTStyle(t *testing.T) {
	gin.SetMode(gin.TestMode)
	db := setupAccountsDB(t)

	router := gin.New()
	apiV1 := router.Group("/api/v1")
	accountsroutes.Register(apiV1, db, "test-secret")

	validToken := signedAuthToken(t, "test-secret", "99")
	req := httptest.NewRequest(http.MethodPost, "/api/v1/accounts/auth/token/verify/", strings.NewReader(`{"token":"`+validToken+`"}`))
	req.Header.Set("Content-Type", "application/json")
	resp := httptest.NewRecorder()

	router.ServeHTTP(resp, req)

	if resp.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d, body=%s", resp.Code, resp.Body.String())
	}
	if resp.Body.String() != "{}" {
		t.Fatalf("expected empty JSON object, got %s", resp.Body.String())
	}
}

func TestAccountsNotImplementedEndpointsReturn501(t *testing.T) {
	gin.SetMode(gin.TestMode)
	db := setupAccountsDB(t)

	router := gin.New()
	apiV1 := router.Group("/api/v1")
	accountsroutes.Register(apiV1, db, "test-secret")

	paths := []string{
		"/api/v1/accounts/auth/token/",
		"/api/v1/accounts/auth/token/refresh/",
		"/api/v1/accounts/auth/token/blacklist/",
		"/api/v1/accounts/auth/register/party/",
		"/api/v1/accounts/auth/register/advocate/",
		"/api/v1/accounts/auth/verify-email/",
	}

	for _, path := range paths {
		req := httptest.NewRequest(http.MethodPost, path, nil)
		resp := httptest.NewRecorder()
		router.ServeHTTP(resp, req)

		if resp.Code != http.StatusNotImplemented {
			t.Fatalf("expected 501 for %s, got %d, body=%s", path, resp.Code, resp.Body.String())
		}
	}
}

func setupAccountsDB(t *testing.T) *gorm.DB {
	t.Helper()
	db, err := gorm.Open(sqlite.Open("file:test_accounts_contract?mode=memory&cache=shared"), &gorm.Config{})
	if err != nil {
		t.Fatalf("failed to open sqlite db: %v", err)
	}

	if err := db.AutoMigrate(&accountmodel.User{}, &accountmodel.RegistrationProfile{}, &authGroup{}, &authUserGroup{}); err != nil {
		t.Fatalf("failed to migrate accounts tables: %v", err)
	}

	return db
}

func seedAccountsData(t *testing.T, db *gorm.DB) {
	t.Helper()
	now := time.Now().UTC()
	user := accountmodel.User{
		ID:               99,
		Username:         "reader.user",
		Email:            "reader@example.com",
		FirstName:        "Reader",
		LastName:         "User",
		PhoneNumber:      "9999999999",
		Department:       "Registry",
		Designation:      "Reader",
		RegistrationType: "",
		EmailVerified:    true,
		IsActive:         true,
		IsStaff:          true,
		DateJoined:       now,
	}
	if err := db.Create(&user).Error; err != nil {
		t.Fatalf("failed to seed user: %v", err)
	}

	group := authGroup{ID: 1, Name: "READER"}
	if err := db.Create(&group).Error; err != nil {
		t.Fatalf("failed to seed group: %v", err)
	}
	if err := db.Create(&authUserGroup{ID: 1, UserID: 99, GroupID: 1}).Error; err != nil {
		t.Fatalf("failed to seed user-group mapping: %v", err)
	}
}
