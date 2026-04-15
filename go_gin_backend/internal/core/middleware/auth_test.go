package middleware

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"

	coreaudit "github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/audit"
	coreauth "github.com/dhrunam/hcs_cms/go_gin_backend/internal/core/auth"
)

func TestOptionalAuthAllowsAnonymous(t *testing.T) {
	gin.SetMode(gin.TestMode)
	r := gin.New()
	r.Use(OptionalAuth("secret"))
	r.GET("/", func(c *gin.Context) {
		c.Status(http.StatusOK)
	})

	req := httptest.NewRequest(http.MethodGet, "/", nil)
	resp := httptest.NewRecorder()
	r.ServeHTTP(resp, req)

	if resp.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", resp.Code)
	}
}

func TestOptionalAuthRejectsInvalidHeader(t *testing.T) {
	gin.SetMode(gin.TestMode)
	r := gin.New()
	r.Use(OptionalAuth("secret"))
	r.GET("/", func(c *gin.Context) {
		c.Status(http.StatusOK)
	})

	req := httptest.NewRequest(http.MethodGet, "/", nil)
	req.Header.Set("Authorization", "Bad token")
	resp := httptest.NewRecorder()
	r.ServeHTTP(resp, req)

	if resp.Code != http.StatusUnauthorized {
		t.Fatalf("expected 401, got %d", resp.Code)
	}
}

func TestOptionalAuthPopulatesUserContext(t *testing.T) {
	gin.SetMode(gin.TestMode)
	r := gin.New()
	r.Use(OptionalAuth("secret"))
	r.GET("/", func(c *gin.Context) {
		userID := coreaudit.UserID(c.Request.Context())
		if userID != "42" {
			c.Status(http.StatusUnauthorized)
			return
		}
		c.Status(http.StatusOK)
	})

	token := signedToken(t, "secret", "42")
	req := httptest.NewRequest(http.MethodGet, "/", nil)
	req.Header.Set("Authorization", "Bearer "+token)
	resp := httptest.NewRecorder()
	r.ServeHTTP(resp, req)

	if resp.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", resp.Code)
	}
}

func TestAuthRequiredRejectsMissingToken(t *testing.T) {
	gin.SetMode(gin.TestMode)
	r := gin.New()
	r.Use(AuthRequired("secret"))
	r.GET("/", func(c *gin.Context) {
		c.Status(http.StatusOK)
	})

	req := httptest.NewRequest(http.MethodGet, "/", nil)
	resp := httptest.NewRecorder()
	r.ServeHTTP(resp, req)

	if resp.Code != http.StatusUnauthorized {
		t.Fatalf("expected 401, got %d", resp.Code)
	}
}

func TestAuthRequiredAcceptsValidToken(t *testing.T) {
	gin.SetMode(gin.TestMode)
	r := gin.New()
	r.Use(AuthRequired("secret"))
	r.GET("/", func(c *gin.Context) {
		if coreaudit.UserID(c.Request.Context()) != "84" {
			c.Status(http.StatusUnauthorized)
			return
		}
		c.Status(http.StatusOK)
	})

	token := signedToken(t, "secret", "84")
	req := httptest.NewRequest(http.MethodGet, "/", nil)
	req.Header.Set("Authorization", "Bearer "+token)
	resp := httptest.NewRecorder()
	r.ServeHTTP(resp, req)

	if resp.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", resp.Code)
	}
}

func signedToken(t *testing.T, secret, userID string) string {
	t.Helper()
	claims := coreauth.Claims{
		UserID: userID,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(1 * time.Hour)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
		},
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	signed, err := token.SignedString([]byte(secret))
	if err != nil {
		t.Fatalf("failed to sign token: %v", err)
	}
	return signed
}
