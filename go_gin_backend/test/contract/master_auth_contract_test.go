package contract_test

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"

	mastermodel "github.com/dhrunam/hcs_cms/go_gin_backend/internal/master/model"
	masterroutes "github.com/dhrunam/hcs_cms/go_gin_backend/internal/master/routes"
)

func TestMasterAuthParity(t *testing.T) {
	gin.SetMode(gin.TestMode)
	db := setupAuthMasterDB(t)
	seedAuthMasterData(t, db)

	router := gin.New()
	apiV1 := router.Group("/api/v1")
	masterroutes.Register(apiV1, db, "test-secret")

	tests := []struct {
		name           string
		authorization  string
		expectedStatus int
	}{
		{name: "anonymous allowed", authorization: "", expectedStatus: http.StatusOK},
		{name: "invalid auth header", authorization: "Token abc", expectedStatus: http.StatusUnauthorized},
		{name: "invalid bearer token", authorization: "Bearer invalid.token.value", expectedStatus: http.StatusUnauthorized},
		{name: "valid bearer token", authorization: "Bearer " + signedAuthToken(t, "test-secret", "99"), expectedStatus: http.StatusOK},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/master/states", nil)
			if tc.authorization != "" {
				req.Header.Set("Authorization", tc.authorization)
			}
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)

			if resp.Code != tc.expectedStatus {
				t.Fatalf("expected %d, got %d, body=%s", tc.expectedStatus, resp.Code, resp.Body.String())
			}
		})
	}
}

func setupAuthMasterDB(t *testing.T) *gorm.DB {
	t.Helper()
	db, err := gorm.Open(sqlite.Open("file::memory:?cache=shared"), &gorm.Config{})
	if err != nil {
		t.Fatalf("failed to init sqlite: %v", err)
	}
	if err := db.AutoMigrate(&mastermodel.State{}); err != nil {
		t.Fatalf("failed to migrate state model: %v", err)
	}
	return db
}

func seedAuthMasterData(t *testing.T, db *gorm.DB) {
	t.Helper()
	stateName := "Sikkim"
	if err := db.Exec(`
		DELETE FROM state
	`).Error; err != nil {
		t.Fatalf("failed to clear state table: %v", err)
	}
	if err := db.Exec(`
		INSERT INTO state
		(id, created_at, updated_at, created_by_id, updated_by_id, is_active, state, create_modify, est_code_src, national_code)
		VALUES (?, NULL, NULL, NULL, NULL, ?, ?, NULL, ?, NULL)
	`, 1, true, stateName, "SKNM01").Error; err != nil {
		t.Fatalf("failed to seed state: %v", err)
	}
}

func signedAuthToken(t *testing.T, secret, userID string) string {
	t.Helper()
	claims := jwt.MapClaims{
		"user_id": userID,
		"exp":     time.Now().Add(1 * time.Hour).Unix(),
		"iat":     time.Now().Unix(),
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	signed, err := token.SignedString([]byte(secret))
	if err != nil {
		t.Fatalf("failed to sign token: %v", err)
	}
	return signed
}
